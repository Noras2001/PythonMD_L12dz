
import os
import json
import zipfile
from datetime import datetime
import chardet
from jsonschema import validate, ValidationError, SchemaError

# Класс Data для хранения информации о данных файлов
class Data:
    def __init__(self, file_name, text, text_processed, file_size, last_change_time):
        self.file_name = file_name
        self.text = text
        self.text_processed = text_processed
        self.file_size = file_size
        self.last_change_time = last_change_time

# Класс FileInfo для хранения информации о файлах
class FileInfo:
    def __init__(self, file_name, full_path, file_size, creation_time, last_change_time):
        self.file_name = file_name
        self.full_path = full_path
        self.file_size = file_size
        self.creation_time = creation_time
        self.last_change_time = last_change_time

def data_to_dict(data):
    return {
        'file_name': data.file_name, 
        'text': data.text, 
        'text_processed': data.text_processed, 
        'file_size': data.file_size, 
        'last_change_time': data.last_change_time
    }

def file_info_to_dict(file_info):
    return {
        'file_name': file_info.file_name,
        'full_path': file_info.full_path,
        'file_size': file_info.file_size,
        'creation_time': file_info.creation_time,
        'last_change_time': file_info.last_change_time
    }

# Функция для создания структуры директорий проекта
def create_project_structure():
    dirs = [
        "project_root/data/raw",
        "project_root/data/processed",
        "project_root/logs",
        "project_root/backups",
        "project_root/output"
    ]
    
    for dir in dirs:
        os.makedirs(dir, exist_ok=True)

# Функция для логирования действий
def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open('project_root/logs/project_log.txt', 'a', encoding='utf-8') as logfile:
        logfile.write(f"{timestamp} - {message}\n")

# Функция для создания примерных файлов с разными кодировками
def create_example_files():
    files = [
        ('project_root/data/raw/example1.txt', 'Hello, World!', 'utf-8'),
        ('project_root/data/raw/example2.txt', 'Привет, мир!', 'utf-8'),
        ('project_root/data/raw/example3.txt', '¡Hola mundo!', 'iso-8859-1'),
        ('project_root/data/raw/example4.txt', 'Hola mundo!', 'ascii'),
        ('project_root/data/raw/example5.txt', 'Hello, World', 'ascii'),
    ]
    
    for filepath, content, encoding in files:
        with open(filepath, 'w', encoding=encoding) as file:
            file.write(content)
            log(f"File '{filepath}' created with encoding '{encoding}' and content: {content}")

    log("Example files created successfully.")
    return files

# Функция для обработки файлов: преобразование регистра и сохранение в другую директорию
def process_files(files):
    for filepath, _, _ in files:
        with open(filepath, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
            text = raw_data.decode(encoding)
            
            processed_text = text.swapcase()
            processed_filepath = filepath.replace('/raw/', '/processed/').replace('.txt', '_processed.txt')
            with open(processed_filepath, 'w', encoding=encoding) as processed_file:
                processed_file.write(processed_text)
                log(f"Processed file '{processed_filepath}' created with content: {processed_text}")

    log("File processing completed successfully.")

# Функция для сериализации обработанных данных в JSON-файл
def serialize_processed_data():
    processed_dir = 'project_root/data/processed/'
    output_dir = 'project_root/output/'
    data_list = []
    
    for file_name in os.listdir(processed_dir):
        file_path = os.path.join(processed_dir, file_name)
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

            text_processed = raw_data.decode(encoding)
            text = text_processed.swapcase()
            
            file_size = os.path.getsize(file_path)
            last_change_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')

            data = Data(file_name, text, text_processed, file_size, last_change_time)
            data_list.append(data_to_dict(data))
    
    output_file_path = os.path.join(output_dir, 'processed_data.json')
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data_list, json_file, ensure_ascii=False, indent=4)
    
    log(f"Data serialized and saved to {output_file_path}")

# Функция для создания резервной копии всех данных из директории data/
def create_backup():
    backup_dir = 'project_root/backups/'
    data_dir = 'project_root/data/'
    date_str = datetime.now().strftime('%Y%m%d')
    backup_file = os.path.join(backup_dir, f'backup_{date_str}.zip')

    with zipfile.ZipFile(backup_file, 'w') as backup_zip:
        for foldername, subfolders, filenames in os.walk(data_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                backup_zip.write(file_path, os.path.relpath(file_path, data_dir))
    
    log(f"Backup created at {backup_file}")

# Функция для восстановления данных из резервной копии
def restore_backup(backup_file):
    data_dir = 'project_root/data/'
    
    with zipfile.ZipFile(backup_file, 'r') as backup_zip:
        backup_zip.extractall(data_dir)
    
    log(f"Backup restored from {backup_file}")

# Функция для сбора информации о всех файлах в директории data/processed/ и сериализации их в JSON
def collect_file_info():
    processed_dir = 'project_root/data/processed/'
    file_info_list = []
    
    for file_name in os.listdir(processed_dir):
        file_path = os.path.join(processed_dir, file_name)
        file_size = os.path.getsize(file_path)
        creation_time = datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        last_change_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')

        file_info = FileInfo(file_name, file_path, file_size, creation_time, last_change_time)
        file_info_list.append(file_info_to_dict(file_info))
    
    output_file_path = 'project_root/output/file_info.json'
    with open(output_file_path, 'w', encoding='utf-8') as json_file:
        json.dump(file_info_list, json_file, ensure_ascii=False, indent=4)
    
    log(f"File info serialized and saved to {output_file_path}")
    return output_file_path

# Функция для десериализации данных из JSON
def deserialize_file_info(json_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        file_info_list = json.load(json_file)
    
    deserialized_info = [FileInfo(**file_info) for file_info in file_info_list]
    log("File info deserialized successfully")
    return deserialized_info

# Функция для получения схемы JSON для валидации
def get_file_info_schema():
    return {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "file_name": {"type": "string"},
                "full_path": {"type": "string"},
                "file_size": {"type": "integer"},
                "creation_time": {"type": "string", "format": "date-time"},
                "last_change_time": {"type": "string", "format": "date-time"}
            },
            "required": ["file_name", "full_path", "file_size", "creation_time", "last_change_time"]
        }
    }

# Функция для валидации JSON-файла с использованием схемы
def validate_json(json_file_path):
    schema = get_file_info_schema()
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    try:
        validate(instance=data, schema=schema)
        log("JSON file is valid according to the schema")
        return True
    except ValidationError as e:
        log(f"Validation error: {e.message}")
    except SchemaError as e:
        log(f"Schema error: {e.message}")
    
    return False

# Функция для генерации итогового отчета
def generate_report(start_time, json_validation_result):
    end_time = datetime.now()
    elapsed_time = end_time - start_time

    report = {
        "start_time": start_time.strftime('%Y-%m-%d %H:%M:%S'),
        "end_time": end_time.strftime('%Y-%m-%d %H:%M:%S'),
        "elapsed_time": str(elapsed_time),
        "tasks": [
            {
                "task": "Create project structure",
                "status": "Completed",
                "details": "Directories for the project were created."
            },
            {
                "task": "Create and process files",
                "status": "Completed",
                "details": "Files were created and processed, and data was serialized."
            },
            {
                "task": "Validate JSON",
                "status": "Completed" if json_validation_result else "Failed",
                "details": "JSON validation result."
            }
        ],
        "conclusions": "All tasks were completed. "
    }

    report_path = 'project_root/output/report.json'
    with open(report_path, 'w', encoding='utf-8') as json_file:
        json.dump(report, json_file, ensure_ascii=False, indent=4)
    
    txt_report_path = 'project_root/output/report.txt'
    with open(txt_report_path, 'w', encoding='utf-8') as txt_file:
        for key, value in report.items():
            txt_file.write(f"{key}: {value}\n\n")

    log(f"Report generated and saved to {report_path} and {txt_report_path}")

# Основной блок выполнения всех задач
if __name__ == "__main__":
    start_time = datetime.now()

    # Сначала создаем структуру директорий
    create_project_structure()

    # Теперь можем начать логирование
    log("Project structure created")

    # Создание и обработка файлов
    files = create_example_files()
    process_files(files)

    # Сериализация данных
    serialize_processed_data()

    # Сбор информации о файлах и её сериализация
    json_file_path = collect_file_info()

    # Валидация JSON
    json_validation_result = validate_json(json_file_path)

    # Генерация отчета
    generate_report(start_time, json_validation_result)

    # Создание резервной копии
    create_backup()

    # Пример восстановления данных из последней резервной копии
    latest_backup = os.path.join('project_root/backups/', f'backup_{datetime.now().strftime("%Y%m%d")}.zip')
    restore_backup(latest_backup)

    log("All steps completed successfully.")
