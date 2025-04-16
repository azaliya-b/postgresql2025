# StackExchange Data Dump в PostgreSQL

## 📌 Цель проекта

Импортировать данные StackExchange Data Dump (dba.stackexchange.org) в PostgreSQL, восстановить связи между таблицами, выполнить два аналитических запроса и оптимизировать работу с большими объёмами данных.

---

## ⚙️ Что делает проект

- Переносит данные StackExchange из XML-дампов в PostgreSQL.
- Создаёт схему данных с учётом только реально присутствующих столбцов.
- Загружает данные в таблицы без ключей → очищает некорректные ссылки → восстанавливает внешние ключи.
- Выполняет аналитические SQL-запросы:
  - Q1: Анализ пар тегов и связи с репутацией.
  - Q2: Поиск принятых ответов с отрицательными оценками.

---

## 🔧 Как запустить проект

### 1. Установите PostgreSQL (желательно 17+)
Скачать: https://www.postgresql.org/download/

### 2. Подготовьте дампы
Скачайте архивы:

  - [dba.stackexchange.com.7z](https://archive.org/download/stackexchange/dba.stackexchange.com.7z)
  - [dba.meta.stackexchange.com.7z](https://archive.org/download/stackexchange/dba.meta.stackexchange.com.7z)

Создайте папку:

```bash
mkdir data
```
Распакуйте архив dba.stackexchange.com.7z в папку `data/`.

### ⚠️ Важно

Для проекта нужен **только один архив**:

- ✅ `dba.stackexchange.com.7z` — содержит все необходимые XML-файлы (Posts.xml, Users.xml и др.)
- ❌ `dba.meta.stackexchange.com.7z` — не используется и может быть проигнорирован

### 3. Создайте базу данных

```bash
createdb stackdb
```

### 4. Настройте переменные окружения
Создайте файл .env в корне проекта, скопировав шаблон:

```bash
cp .env.example .env
```
Откройте .env и укажите:

```env
## Путь к XML-файлам
DATA_PATH=data/dba.stackexchange.com

# Параметры подключения к PostgreSQL
POSTGRES_DB=stackdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin123
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

### 5. Настройка путей

Если вы используете другую структуру директорий или переименовали `data/dba.stackexchange.com`, создайте файл `.env` в корне и укажите путь к XML-файлам:

```env
DATA_PATH=путь/к/вашим/xml-файлам
```

### 6. Установите зависимости
```bash
pip install -r requirements.txt
```

### (Необязательно) Проверка структуры XML-файлов
Скрипт `extract_fields.py` позволяет вывести список полей, реально присутствующих в каждом XML:

```bash
python scripts/extract_fields.py
```

### 7. Создайте базу данных PostgreSQL
```bash
createdb stackdb
```

### 8. Выполните создание схемы

```bash
psql -d stackdb -f sql/create_schema.sql
```

> Скрипт включает только те поля, которые реально присутствуют в XML-дампах.

### 9. Загрузите данные

```bash
python scripts/load_data.py --data-dir ./data
```

- Загружает данные из XML в PostgreSQL.
- Таблицы пока без внешних ключей.

### 10. Очистите недействительные ссылки

```bash
python scripts/cleanup_invalid_references.py
```

- Удаляет строки, нарушающие будущие внешние ключи.

### 11. Добавьте внешние ключи

```bash
psql -d stackdb -f sql/add_foreign_keys.sql
```

---

## 🔍 SQL-запросы

### ▶️ Как запустить запросы
Подключитесь к базе данных:

```bash
psql -d stackdb
```

Выполните SQL-файл с запросами:

```bash
\i sql/queries.sql
```


Или откройте queries.sql, скопируйте нужный запрос и выполните его вручную в psql.

ℹ️ Для анализа производительности можно использовать:

```sql
EXPLAIN ANALYZE
```


### ✅ Q1 — Репутационные пары

Анализирует, какие теги (вопросы с `postgresql`) часто задаются вместе, как быстро на них отвечают, и какова репутация пользователей, которые дают эти ответы.

```sql
WITH PostgresqlQuestions AS (
    SELECT Id, CreationDate, Tags
    FROM Posts
    WHERE PostTypeId = 1 AND Tags LIKE '%|postgresql|%'
),
Answers AS (
    SELECT p.Id AS AnswerId, p.ParentId, p.CreationDate AS AnswerDate, p.OwnerUserId, u.Reputation
    FROM Posts p
    JOIN Users u ON u.Id = p.OwnerUserId
    WHERE p.PostTypeId = 2
),
QnA AS (
    SELECT q.Id AS QuestionId,
           q.CreationDate AS QuestionDate,
           a.AnswerDate,
           a.Reputation,
           q.Tags
    FROM PostgresqlQuestions q
    JOIN Answers a ON a.ParentId = q.Id
),
TagPairs AS (
    SELECT
        t1.tag AS tag1,
        t2.tag AS tag2,
        EXTRACT(EPOCH FROM (qna.AnswerDate - qna.QuestionDate)) / 3600 AS hours_to_answer,
        qna.Reputation
    FROM QnA qna
    CROSS JOIN LATERAL unnest(string_to_array(trim(BOTH '|' FROM qna.Tags), '|')) AS t1(tag)
    CROSS JOIN LATERAL unnest(string_to_array(trim(BOTH '|' FROM qna.Tags), '|')) AS t2(tag)
    WHERE t1.tag < t2.tag
)
SELECT
    tag1,
    tag2,
    COUNT(*) AS pair_count,
    ROUND(AVG(hours_to_answer), 2) AS avg_hours_to_answer,
    ROUND(AVG(Reputation)) AS avg_user_reputation
FROM TagPairs
GROUP BY tag1, tag2
HAVING COUNT(*) > 3
ORDER BY pair_count DESC
LIMIT 20;
```

**План выполнения**: Вы можете ознакомиться с планом выполнения для этого запроса в файле sql/query1_plan.txt.

---

### ✅ Q2 — Успешные шутники

Находит ответы с отрицательной оценкой, которые были приняты как лучшие (`AcceptedAnswerId`), и при этом связаны с тегом `postgresql`.

```sql
WITH Questions AS (
    SELECT
        Id AS question_id,
        AcceptedAnswerId,
        Tags
    FROM Posts
    WHERE PostTypeId = 1 AND Tags LIKE '%postgresql%'
),
AcceptedBadAnswers AS (
    SELECT
        p.Id AS answer_id,
        p.Score,
        u.DisplayName,
        q.question_id
    FROM Questions q
    JOIN Posts p ON p.Id = q.AcceptedAnswerId AND p.Score < 0
    LEFT JOIN Users u ON u.Id = p.OwnerUserId
)
SELECT *
FROM AcceptedBadAnswers
ORDER BY Score ASC;
```

**План выполнения**: Вы можете ознакомиться с планом выполнения для этого запроса в файле sql/query1_plan.txt.

---

## 📈 Идеи по оптимизации

1. **Индексация:**
   - `CREATE INDEX ON Posts (Tags);`
   - `CREATE INDEX ON Posts (PostTypeId);`
   - `CREATE INDEX ON Posts (ParentId);`
   - `CREATE INDEX ON Users (Reputation);`

2. **Предварительная агрегация в CTE:**
   - Для Q1 можно кэшировать пары тегов для уменьшения вычислений.

3. **Визуализация (опционально):**
   - Данные можно визуализировать в Metabase или Superset.
   - Таблицы: `Posts`, `Users`.

---

## 💭 Вопросы и принятые решения

| Вопрос | Решение |
|-------|---------|
| Как определить, какие поля включать в схему? | Использован предварительный парсинг XML |
| Что делать с внешними ключами? | Загружаем без них → очищаем данные → ставим `ALTER TABLE ADD CONSTRAINT` |
| Как бороться с плохими связями? | Использован Python-скрипт `cleanup_invalid_references.py` |
| Как выбрать пары тегов? | Используем `unnest` + `CROSS JOIN LATERAL` |

---

## 🗂️ Структура репозитория

```
.
.
├── data/                    # XML-дампы
├── sql/
│   ├── create_schema.sql
│   ├── add_foreign_keys.sql
│   ├── q1_plan.txt             # План выполнения для Q1
│   ├── q2_plan.txt             # План выполнения для Q2
│   └── queries.sql
├── scripts/
│   ├── load_data.py
│   ├── cleanup_invalid_references.py
│   └── extract_fields.py  
├── requirements.txt
├── .env.example
└── README.md


```

---

## ✅ Итог

- ✔ Перенос данных выполнен
- ✔ Связи между таблицами восстановлены
- ✔ SQL-запросы реализованы и оптимизированы
- ✔ README объединяет отчёт, код и документацию

---

## 📌 Приложения

Все файлы доступны в корне проекта. Ниже краткое описание каждого:

| Файл | Назначение |
|------|------------|
| `create_schema.sql` | SQL-скрипт создания схемы БД на основе XML-дампа |
| `load_data.py` | Загрузка XML-данных в PostgreSQL |
| `cleanup_invalid_references.py` | Удаление строк с нарушенными связями перед добавлением внешних ключей |
| `add_foreign_keys.sql` | Добавление внешних ключей после очистки |
| `queries.sql` | Финальные SQL-запросы (Q1 и Q2) |
| `extract_fields.py` | Скрипт для извлечения структуры полей из XML-дампов (выводит атрибуты, присутствующие в XML-файле) |
| `requirements.txt` | Зависимости для Python |
| `README.md` | Инструкция и отчёт по выполнению задания |
| `data/` | Каталог для распакованных XML-дампов |

📎 Все команды и пути уже описаны выше — просто следуйте пошаговой инструкции.
