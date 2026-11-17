"""JSON ფაილში მონაცემების შენახვა და ჩატვირთვა."""
import json
import os

from exceptions import StorageError


class JsonStorage:
    """ინახავს და კითხულობს დავალებების სიას JSON ფაილიდან."""

    def __init__(self, path="tasks.json"):
        self.path = path

    def load(self):
        """აბრუნებს ჩანაწერების სიას. ფაილის არარსებობისას აბრუნებს ცარიელ სიას."""
        if not os.path.exists(self.path):
            return []
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            raise StorageError(f"ფაილი '{self.path}' დაზიანებულია. გაასწორეთ ან წაშალეთ.")
        except OSError as e:
            raise StorageError(f"ფაილის წაკითხვა ვერ მოხერხდა: {e}")
        if not isinstance(data, list):
            raise StorageError("ფაილის სტრუქტურა არასწორია.")
        return data

    def save(self, data):
        """წერს მონაცემებს დროებით ფაილში და შემდეგ ანაცვლებს ძირითადს.

        ასე ჩაწერის შეწყვეტის შემთხვევაშიც ძველი ფაილი არ ზიანდება.
        """
        tmp_path = self.path + ".tmp"
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.path)
        except OSError as e:
            raise StorageError(f"შენახვა ვერ მოხერხდა: {e}")