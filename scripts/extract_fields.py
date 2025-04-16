import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

def extract_fields(file_path, limit=100):
    fields = set()
    count = 0
    for event, elem in ET.iterparse(file_path, events=('start',)):
        if elem.tag == 'row':
            fields.update(elem.attrib.keys())
            count += 1
            if count >= limit:
                break
    return fields

def main():
    data_dir = os.getenv("DATA_PATH", "data/dba.stackexchange.com")  # путь по умолчанию
    if not os.path.exists(data_dir):
        print(f"❌ Директория {data_dir} не найдена. Проверь путь.")
        return

    xml_files = [f for f in os.listdir(data_dir) if f.endswith(".xml")]
    if not xml_files:
        print("❌ Нет XML-файлов в директории.")
        return

    for file_name in sorted(xml_files):
        file_path = os.path.join(data_dir, file_name)
        print(f"\n📄 Поля в {file_name}:")
        try:
            fields = extract_fields(file_path)
            for field in sorted(fields):
                print(f"  - {field}")
        except Exception as e:
            print(f"⚠️ Ошибка при обработке {file_name}: {e}")

if __name__ == "__main__":
    main()
