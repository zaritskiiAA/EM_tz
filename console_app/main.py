import re
import sys
from typing import Any
from collections import defaultdict

from .data import Archive
from .exceptions import (
    InvalidCommand,
    InvalidInputData,
    DataDoesNotExists,
    TheSameStatus,
)


class Library:
    VALID_COMMAND = ("add", "delete", "search", "all", "change_status", "cmd", "leave")
    COMMAND_DESCRIPTIONS = (
        "Добавляет книгу в библиотеку",
        "Удаляет книгу из библиотеки",
        "Поиск книги по заданному атрибуту",
        "Посмотреть все книги в библиотеке",
        "Изменить статус книги в библиотеке",
        "Уйти из библиотеки. Остановить работу скрипта",
        "Запросить список команд",
    )

    @property
    def archive(self):
        if hasattr(self, "_archive"):
            return self._archive
        self._archive = Archive()
        return self._archive

    def formatted_style(self, head: tuple[str], body: list[tuple[Any]]) -> str:
        # с prettytable было бы веселее :)
        table = []
        body.insert(0, head)
        bound_table = defaultdict(int)
        for data in body:
            row = []
            for idx, d in enumerate(data):
                row.append(f"{d}")
                bound_table[idx] = max(bound_table[idx], len(d))
            table.append(row)
        return self._smooth_table(table, bound_table)

    def _smooth_table(self, table: list, bound_table: defaultdict[int, int]) -> str:
        smooth_table = []
        for row in table:
            col_res = []
            for idx, col in enumerate(row):
                bound_col = bound_table[idx]
                if not idx:
                    col_res.append(f"| {col + '|':>{bound_col}}")
                else:
                    col_res.append(f" {col:>{bound_col}} |")
            row_net = "".join(["-" * (bound + bound // 10) for bound in bound_table.values()])
            smooth_table.append(row_net + "\n")
            smooth_table.append("".join(col_res) + "\n")
        return "".join(smooth_table)

    def check_command(self, cmd: str) -> bool:
        cmd = re.sub("\\s", "_", cmd)
        if cmd in self.VALID_COMMAND:
            self._current_cmd = cmd
            return True
        raise InvalidCommand(
            f"Неизвестная команда: '{cmd}'. Используйте команды из меню. Запросить меню команда 'cmd'."
        )

    def command_execute(self):
        getattr(self, self._current_cmd)()

    @staticmethod
    def _parse_input(data, pattern: str):
        parsed_data = re.findall(pattern, data)
        if not parsed_data:
            return
        match = parsed_data[0]
        if isinstance(match, tuple):
            return match[0]
        return " ".join(parsed_data)

    @staticmethod
    def _gen_id(mask_data: dict[str]) -> int:
        id = "t{t}a{a}y{y}"
        return id.format(
            t=f'{sum(map(ord, mask_data["t"]))}',
            a=f'{sum(map(ord, mask_data["a"]))}',
            y=f'{sum(map(ord, mask_data["y"]))}',
        )

    @staticmethod
    def validate_input_data(data: list[str]) -> None:
        for d in data:
            if not d:
                raise InvalidInputData(
                    "К сожалению неудалось корректно считать указаные вами данные."
                )

    def add(self):
        title = self._parse_input(input("Введите название: "), r"(?<!\S)[\w]+")
        author = self._parse_input(input("Введите автора: "), r"(?<!\S)[\w]+")
        year = self._parse_input(input("Введите год релиза: "), r"(?<!\S)[\d]+(?!\S)")
        result_map_msg = {
            1: f"Книга {title} ранее регистрировалась, Изменен статус.",
            2: f"Книга {title} добавлена в архив.",
        }
        self.validate_input_data([title, author, year])
        id = self._gen_id({"t": title, "a": author, "y": year})
        data_to_save = {id: {"title": title, "author": author, "year": year, "status": "в наличии"}}
        res = self.archive.add(data_to_save)
        print(result_map_msg.get(res))

    def delete(self):
        id = input("Введите идентификатор книги: ")
        # заменить дублирование групп на именовaные
        id = self._parse_input(id, r"(?<!\S)(t[0-9]+a[0-9]+y[0-9]+(d[0-9]+)?)(?!\S)")
        self.validate_input_data([id])
        print(id)
        self.archive.delete(id)
        print("Книга успешно удалена из архива.")

    def cmd(self):
        menu = self.formatted_style(
            ("КОМАНДА", "ОПИСАНИЕ"),
            [(cmd, desc) for cmd, desc in zip(self.VALID_COMMAND, self.COMMAND_DESCRIPTIONS)],
        )
        print(menu)

    def change_status(self):
        id, new_status = input("Введите идентификатор книги: "), input(
            "Введите Новый статус книги: "
        )
        result_map_msg = {
            0: "Изъяли дубликат книги, книга по прежнему доступна в архиве.",
            1: "Статус успешно изменен.",
            2: "Дубликат изъят.",
        }
        id = self._parse_input(id, r"(?<!\S)(t[0-9]+a[0-9]+y[0-9]+(d[0-9]+)?)(?!\S)")
        new_status = self._parse_input(new_status.lower(), r"(?<!\S)(в наличии|выдана)(?!\S)")
        self.validate_input_data([id, new_status])
        res = self.archive.change_status(id, new_status)
        print(result_map_msg[res])

    @staticmethod
    def leave():
        print("ВЫ ВЫШЛИ ИЗ БИБЛИОТЕКИ, РАБОТА СКРИПТА ПРИОСТАНОВЛЕНА!!!")
        sys.exit()

    def all(self) -> None:
        storage_data = [
            (id, book["title"], book["author"], book["year"])
            for id, book in self.archive.all().items()
            if "d" not in id
        ]
        print("АРХИВ:\n")
        print(self.formatted_style(("ID", "TITLE", "AUTHOR", "YEAR"), storage_data))

    @staticmethod
    def _match(storage_data: dict[str, dict[str]], filter_attr: str) -> list[tuple[str]]:
        filtered_data = []
        encoded_attr = sum(map(ord, filter_attr))
        for id in storage_data:
            if "d" in id:
                continue
            match = re.findall(fr"(?<=t|a|y){encoded_attr}(?=a|y|d?)", id)
            if match:
                book = storage_data[id]
                filtered_data.append((id, book["title"], book["author"], book["year"]))
        return filtered_data

    def search(self) -> None:
        filter_attr = input("Введите название, автора или год книги: ")
        if result := self._match(self.archive.all(), filter_attr):
            print("РЕЗУЛЬТАТ ПОИСКА.")
            print(self.formatted_style(("ID", "TITLE", "AUTHOR", "YEAR"), result))
        else:
            print(f"Ничего не найдено для '{filter_attr}'")

    def enter(self):
        print("\nДОБРО ПОЖАЛОВАТЬ В БИБЛИОТЕКУ!!!\n")
        self.cmd()
        while True:
            cmd = input("Введите команду: ")
            try:
                self.check_command(cmd.lower().strip())
            except InvalidCommand as exc:
                print(exc)
            else:
                try:
                    self.command_execute()
                except (InvalidInputData, TheSameStatus, DataDoesNotExists) as exc:
                    print(exc)


if __name__ == "__main__":
    library = Library()
    library.enter()
