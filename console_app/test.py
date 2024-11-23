import os

from typing import Iterable
import unittest

from .main import Library
from .exceptions import DataDoesNotExists, TheSameStatus


class mock_input:
    # не придумал ничего лучше как прерывать цепочку инпутов в скрипте =(
    def __init__(self, return_value: Iterable[str]) -> None:
        self.return_value = iter(return_value)
        self.outputs = []

    def __call__(self, string: str) -> str:
        self.outputs.append(string)
        value = next(self.return_value)
        return value


class catch_print:
    def __init__(self):
        self.catch_data = []

    def __call__(self, string: str) -> None:
        self.catch_data.clear()
        self.catch_data.append(string)


class TestLibraryIOCommand(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library = Library()

    def setUp(self):
        self.mock_print = catch_print()
        self.default_print = print
        __builtins__.print = self.mock_print
        self.library.archive._filename = "test_library.json"

    def tearDown(self) -> None:
        if os.path.exists(self.library.archive._filename):
            os.remove(self.library.archive._filename)

    def test_valid_input_command(self):
        expected_output = (
            "Введите название: ",
            "Введите идентификатор книги: ",
            "Введите название, автора или год книги: ",
            "",
            "Введите идентификатор книги: ",
            "",
            "",
        )
        for cmd, out in zip(self.library.VALID_COMMAND, expected_output):
            with self.subTest(cmd=cmd, out=out):
                try:
                    inp = mock_input([cmd])
                    __builtins__.input = inp
                    self.library.enter()
                except StopIteration:
                    if not out:
                        continue
                    self.assertIn(out, inp.outputs, f"Неожиданый ответ скрипта на команду '{cmd}'")
                except SystemExit:
                    if cmd != "leave":
                        raise

    def test_invalid_input_command(self):
        expected_output = (
            "Неизвестная команда: 'invalid_cmd'. Используйте "
            "команды из меню. Запросить меню команда 'cmd'."
        )
        invalid_cmd = "invalid_cmd"
        try:
            inp = mock_input([invalid_cmd])
            __builtins__.input = inp
            self.library.enter()
        except StopIteration:
            catch_msg = self.mock_print.catch_data.pop()
            if isinstance(catch_msg, Exception):
                catch_msg = catch_msg.args
            self.assertIn(
                expected_output, catch_msg, f"Неожиданый ответ скрипта на команду '{invalid_cmd}'"
            )

    def test_invalid_input_data(self):
        expected_output = "К сожалению неудалось корректно считать указаные вами данные."
        invalid_data = [
            ("add", "%4k&", "valid author", "1995"),
            ("add", "name book", "%4k&", "1995"),
            ("add", "name book", "name author", "%4k&"),
            ("change status", "t195a99y95", "unknown status"),
            ("delete", "1995"),
            ("delete", "x95a1y1"),
            ("delete", "t95i1y1"),
            ("delete", "t95a1k1"),
        ]
        for data in invalid_data:
            with self.subTest(data=data):
                try:
                    inp = mock_input(data)
                    __builtins__.input = inp
                    self.library.enter()
                except StopIteration:
                    catch_msg = self.mock_print.catch_data.pop()
                    if isinstance(catch_msg, Exception):
                        catch_msg = catch_msg.args
                    self.assertIn(
                        expected_output,
                        catch_msg,
                        f"Неожиданый ответ скрипта на данные '{data[1:]}' для команды {data[0]}",
                    )

    def test_valid_input_data(self):
        unexpected_output = "К сожалению неудалось корректно считать указаные вами данные."
        valid_data = [
            ("add", "valid author", "valid author", "1995"),
            ("delete", "t195a85y19"),
            ("delete", "t195a85y19d5"),
            ("change status", "t195a85y19", "выдана"),
            ("change status", "t195a85y19", "в наличии"),
        ]
        for data in valid_data:
            with self.subTest(data=data):
                try:
                    inp = mock_input(data)
                    __builtins__.input = inp
                    self.library.enter()
                except StopIteration:
                    catch_msg = self.mock_print.catch_data.pop()
                    if isinstance(catch_msg, Exception):
                        catch_msg = catch_msg.args
                    self.assertNotIn(
                        unexpected_output,
                        catch_msg,
                        f"Неожиданый ответ скрипта на данные '{data[1:]}' для команды {data[0]}",
                    )


class TesArchiveLogic(unittest.TestCase):
    def setUp(self):
        self.library = Library()
        self.archive = self.library.archive
        self.archive._filename = "test_library.json"
        self.archive.add(self.book_fixture())
        self.archive.add(self.book_registred_early())

    def tearDown(self) -> None:
        os.remove(self.archive._filename)

    def book_fixture(self):
        new_book = {
            "t888a1120y216": {
                "title": "cool book",
                "author": "cool author",
                "year": "1995",
                "status": "в наличии",
            }
        }
        return new_book

    def book_registred_early(self):
        book_registred_early = {
            "t1268a1500y289": {
                "title": "next new book",
                "author": "next new author",
                "year": "100000",
                "status": "выдана",
            }
        }
        return book_registred_early

    def test_add_book_logic(self):
        dublicate = self.book_fixture()
        book_registred_early = self.book_registred_early()
        book_registred_early["t1268a1500y289"]["status"] = "в наличии"
        new_book = {
            "t1219a1219y216": {
                "title": "valid author",
                "author": "valid author",
                "year": "1995",
                "status": "в наличии",
            }
        }
        test_data = (
            (
                dublicate,
                ["t888a1120y216d1", dublicate["t888a1120y216"]],
            ),
            (
                new_book,
                ["t1219a1219y216", new_book["t1219a1219y216"]],
            ),
            (
                book_registred_early,
                ["t1268a1500y289", book_registred_early["t1268a1500y289"]],
            ),
        )

        for add_data, expect_data in test_data:
            with self.subTest(add_data=add_data, expect_data=expect_data):
                cache = self.archive.cache
                expect_id, expect_body = expect_data
                self.archive.add(add_data)
                self.assertIsNotNone(cache.get(expect_id))
                self.assertDictEqual(cache[expect_id], expect_body)

    def test_all_book_logic(self):
        expected_book_id = ("t888a1120y216", "t1268a1500y289")
        for expect_id in expected_book_id:
            with self.subTest(expect_id=expect_id):
                cache = self.archive.all()
                self.assertIn(expect_id, cache)

    def test_change_status_book_logic(self):
        self.archive.add(self.book_fixture())
        test_data = [
            ("t1268a1500y289", "в наличии", "в наличии"),
            ("t888a1120y216", "выдана", "в наличии"),
            ("t888a1120y216d1", "выдана", DataDoesNotExists),
            ("t888a1120y216", "в наличии", TheSameStatus),
            ("t1111a2222y111", "выдана", DataDoesNotExists),
        ]

        for data in test_data:
            with self.subTest(data=data):
                id, new_status, expect_status = data
                try:
                    self.archive.change_status(id, new_status)
                    cache = self.archive.cache
                    self.assertIsNotNone(cache.get(id))
                    self.assertEqual(cache[id]["status"], expect_status)
                except (DataDoesNotExists, TheSameStatus) as exc:
                    self.assertIsInstance(exc, expect_status)

    def test_delete_book_logic(self):
        self.archive.add(self.book_fixture())
        self.archive.add(self.book_fixture())
        exists_data = {
            "title": "cool book",
            "author": "cool author",
            "year": "1995",
            "status": "в наличии",
        }
        test_data = [
            ("t1268a1500y289", None, None),
            ("t888a1120y216", exists_data, None),
            ("t888a1120y216d1", None, None),
            ("t1111a2222y111", None, DataDoesNotExists),
        ]
        for data in test_data:
            with self.subTest(data=data):
                id, after_delete, exc_type = data
                try:
                    self.archive.delete(id)
                    cache = self.archive.cache
                    self.assertEqual(cache.get(id), after_delete)
                except DataDoesNotExists as exc:
                    if not exc_type:
                        self.assertIsNotNone(
                            exc_type,
                            "При удалении книги, которая существует в архиве не должно возникать ошибки",
                        )
                    self.assertIsInstance(exc, exc_type)

    def test_search_book_logic(self):
        storage_data = self.archive.all()
        filter_attr = ["cool book", "cool author", "1995"]
        for attr in filter_attr:
            with self.subTest(attr=attr):
                res = self.library._match(storage_data, attr)
                self.assertEqual(len(res), 1, "При фильтрации должно вернуться 1 результат")
                self.assertIn(attr, res[0])


if __name__ == '__main__':
    unittest.main()
