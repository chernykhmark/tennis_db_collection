from dotenv import load_dotenv
load_dotenv()


import subprocess
import os


def download_files_rsync():
    # Параметры
    username = os.getenv('DRIVER_SERVER_USERNAME')
    server_ip = os.getenv('DRIVER_SERVER_IP')
    remote_path = os.getenv('DRIVER_SERVER_DIRECTORY_PATH')
    local_path = "./data/"

    # Создаем локальную папку
    os.makedirs(local_path, exist_ok=True)

    # Команда rsync
    cmd = [
        "rsync",
        "-avz",
        "--include=*.json",
        "--include=*.html",
        "--exclude=*",
        f"{username}@{server_ip}:{remote_path}/",
        local_path + "/"
    ]

    # Запускаем
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Файлы успешно скачаны")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Ошибка: {e}")
        print(e.stderr)


# Использование
download_files_rsync()