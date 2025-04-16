import psycopg2
import xml.etree.ElementTree as ET
from datetime import datetime
import os
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Параметры подключения к PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT")
)
cur = conn.cursor()

def parse_value(val, typ=str):
    if val is None:
        return None
    try:
        if typ == bool:
            return val.lower() in ['true', '1']
        if typ == datetime:
            return datetime.fromisoformat(val.replace("Z", ""))
        return typ(val)
    except:
        return None

# Универсальный загрузчик таблиц
def load_table(table_name, xml_path, fields, types):
    print(f"Loading: {table_name} from {xml_path}")
    tree = ET.parse(xml_path)
    root = tree.getroot()

    batch = []
    batch_size = 1000

    for i, row in enumerate(root.findall('row')):
        attr = row.attrib
        entry = tuple(parse_value(attr.get(f), t) for f, t in zip(fields, types))
        batch.append(entry)

        if len(batch) >= batch_size:
            insert_batch(table_name, fields, batch)
            batch.clear()

    if batch:
        insert_batch(table_name, fields, batch)

def insert_batch(table, fields, data):
    placeholders = ','.join(['%s'] * len(fields))
    fieldlist = ','.join(fields)
    query = f"INSERT INTO {table} ({fieldlist}) VALUES ({placeholders})"
    cur.executemany(query, data)
    conn.commit()

# Таблицы и конфигурации
TABLES = {
    "Users": {
        "file": "Users.xml",
        "fields": [
            "Id", "AccountId", "Reputation", "CreationDate", "DisplayName", "LastAccessDate",
            "WebsiteUrl", "Location", "AboutMe", "Views", "UpVotes", "DownVotes"
        ],
        "types": [int, int, int, datetime, str, datetime, str, str, str, int, int, int]
    },
    "Posts": {
        "file": "Posts.xml",
        "fields": [
            "Id", "PostTypeId", "ParentId", "AcceptedAnswerId", "CreationDate", "Score", "ViewCount", "Body",
            "OwnerUserId", "LastEditorUserId", "LastEditDate", "LastActivityDate", "Title", "Tags",
            "AnswerCount", "CommentCount", "FavoriteCount", "ClosedDate", "CommunityOwnedDate", "ContentLicense"
        ],
        "types": [int, int, int, int, datetime, int, int, str, int, int, datetime, datetime, str, str, int, int, int, datetime, datetime, str]
    },
    "Tags": {
        "file": "Tags.xml",
        "fields": ["Id", "TagName", "Count", "ExcerptPostId", "WikiPostId", "IsModeratorOnly", "IsRequired"],
        "types": [int, str, int, int, int, bool, bool]
    },
    "Votes": {
        "file": "Votes.xml",
        "fields": ["Id", "PostId", "VoteTypeId", "CreationDate"],
        "types": [int, int, int, datetime]
    },
    "Badges": {
        "file": "Badges.xml",
        "fields": ["Id", "UserId", "Name", "Date", "Class", "TagBased"],
        "types": [int, int, str, datetime, int, bool]
    },
    "PostHistory": {
        "file": "PostHistory.xml",
        "fields": ["Id", "PostHistoryTypeId", "PostId", "RevisionGUID", "CreationDate", "UserId", "Comment", "Text", "ContentLicense"],
        "types": [int, int, int, str, datetime, int, str, str, str]
    },
    "PostLinks": {
        "file": "PostLinks.xml",
        "fields": ["Id", "CreationDate", "PostId", "RelatedPostId", "LinkTypeId"],
        "types": [int, datetime, int, int, int]
    },
    "Comments": {
        "file": "Comments.xml",
        "fields": ["Id", "PostId", "Score", "Text", "CreationDate", "UserId"],
        "types": [int, int, int, str, datetime, int]
    }
}

if __name__ == "__main__":
    data_dir = os.getenv("DATA_PATH")

    for table, config in TABLES.items():
        path = os.path.join(data_dir, config["file"])
        if not os.path.exists(path):
            print(f"⚠️ Файл не найден: {path}, пропуск.")
            continue
        load_table(table, path, config["fields"], config["types"])

    cur.close()
    conn.close()
    print("✅ Загрузка завершена.")