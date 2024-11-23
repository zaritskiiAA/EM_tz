class InvalidCommand(Exception):
    """Вызывается при получения от клиента невалидной команды."""

    pass


class InvalidInputData(ValueError):
    """Вызывается когда неудалось корректно распарсить данные от клиента."""

    pass


class DataDoesNotExists(Exception):
    """Вызывается когда клиент пробует удалить несущствующую книгу в архиве."""

    pass


class MaxDublicateInArchive(Exception):
    """Вызывается когда в архиве много дубликатов одной и тойже книги."""

    pass


class TheSameStatus(Exception):
    """
    Вызывается когда клиент пробует изменить один и тот же статус.
    По факту вызывается исключительно для прерывания метода data.change_status.
    """

    pass
