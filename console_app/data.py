import json

from .exceptions import DataDoesNotExists, TheSameStatus


class Archive:
    _filename = "library_storage.json"

    @property
    def cache(self):
        if hasattr(self, "_cache"):
            return self._cache
        try:
            self._cache = self._load()
            return self._cache
        except FileNotFoundError:
            self.refresh({})
            self._cache = self._load()
            return self._cache

    def clean_cache(self):
        delattr(self, "_cache")

    def refresh(self, storage_data: dict[str, dict[str]]) -> None:
        self._dump(storage_data)

    def _load(self) -> dict[str, dict[str]]:
        with open(self._filename, "r") as f:
            return json.load(f)

    def _dump(self, data: dict[str]) -> None:
        with open(self._filename, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _find_dublicate(self, id: str) -> list[str]:
        storage_data = self.cache
        dublicate = list(filter(lambda key: f"{id}d" in key, storage_data))
        dublicate.sort()
        return dublicate

    @staticmethod
    def _gen_actual_id(income_data_id: str, dublicate: str) -> str:
        if not dublicate:
            return f"{income_data_id}d1"
        last_dublicate = dublicate.pop()
        actual_num = int(last_dublicate.split("d")[-1]) + 1
        return f"{income_data_id}d{actual_num}"

    def add(self, data: dict[str]) -> int:
        """
        Если книги нет, она добавляется.
        Если книга есть в архиве, но статус 'выдана', то изменится статус.
        Если книга есть в архиве, добавляется дубликат с актуальным индексом.
        """
        income_data_id = tuple(data.keys())[0]
        storage_data = self.cache
        answer = 2
        if income_data_id in storage_data and storage_data[income_data_id]["status"] == "выдана":
            storage_data[income_data_id]["status"] = "в наличии"
            answer = 1
        if income_data_id in storage_data:
            dublicate = self._find_dublicate(income_data_id)
            id = self._gen_actual_id(income_data_id, dublicate)
            data = {id: data[income_data_id]}
        storage_data.update(data)
        self.clean_cache()
        self.refresh(storage_data)
        return answer

    def delete(self, id: int) -> None:
        """
        Если книги нет в архиве - выбрасывает исключение.
        Если книга есть и id книги ссылается на дублик - удаляет дубликат.
        Если книга есть и id книги ссылается на оригинал - удаляется дублик,
        если он имеется. Если нет - удаляется оригинал.
        """
        storage_data = self.cache
        if id not in storage_data:
            raise DataDoesNotExists(f"Книги с id: {id} в архиве нет.")
        if "d" not in id:
            if dublicate := self._find_dublicate(id):
                id = dublicate[-1]
        del storage_data[id]
        self.clean_cache()
        self.refresh(storage_data)

    def all(self) -> dict[str, dict[str]]:
        return self.cache

    def _check_status(self, id: str, new_status: str) -> None:
        storage_data = self.cache
        if storage_data[id]["status"].lower() == new_status.lower():
            raise TheSameStatus("Книга уже имеет этот статус.")

    def change_status(self, id: str, new_status: str) -> int:
        """
        Если у книги нет дубликатов - статус свободно изменяется.
        Если у книги есть дубликаты - удаляется дубликат статус не изменяется.
        Если id принадлежит дублику - дубликат удаляется.
        Если книги нет в архиве - ошибка.
        Если новый статус == старому - метод прерывается.
        """
        storage_data = self.cache
        if id not in storage_data:
            raise DataDoesNotExists(f"Книги с id: {id} в архиве нет.")

        self._check_status(id, new_status)
        if "d" not in id:
            if dublicate := self._find_dublicate(id):
                dublicate_id = dublicate[-1]
                del storage_data[dublicate_id]
                answer = 0
            else:
                storage_data[id]["status"] = new_status
                answer = 1
        else:
            del storage_data[id]
            answer = 2
        self.clean_cache()
        self.refresh(storage_data)
        return answer
