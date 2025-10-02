import json
import os
from datetime import datetime


class TestData:

    def __init__(self):
        project_root = os.path.dirname(os.path.abspath(__file__))
        self.data_file = os.path.join(project_root, "test_data.json")
        self.registered_user = None
        self._ensure_data_file()

    def _ensure_data_file(self):
        if not os.path.exists(self.data_file):
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
            print(f" Создан файл для данных: {self.data_file}")

    def save_registered_user(self, username: str, email: str, password: str):
        self.registered_user = {
            "username": username,
            "email": email,
            "password": password,
            "registration_time": datetime.now().isoformat(),
        }

        data = {
            "registered_user": self.registered_user,
            "last_updated": datetime.now().isoformat(),
        }

        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f" Данные сохранены в файл: {self.data_file}")
        except Exception as e:
            print(f" Ошибка сохранения в файл: {e}")

    def get_registered_user(self):
        if self.registered_user:
            return self.registered_user

        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.registered_user = data.get("registered_user")
                    print(f" Данные загружены из файла: {self.data_file}")
                    return self.registered_user
        except Exception as e:
            print(f" Ошибка загрузки из файла: {e}")

        return None

    def clear_data(self):
        self.registered_user = None
        if os.path.exists(self.data_file):
            os.remove(self.data_file)
            print(" Файл с данными удален")


# Глобальный экземпляр
test_data = TestData()
