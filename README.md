### console library app
Консольное приложение имитирующее работу книжной библиотеки. Роль библиотечного архива выполняет json файл.
Подробная документация в [doc](https://github.com/zaritskiiAA/EM_tz/blob/main/doc.md)

#### *Содержание*
1. [Пользовательский интерфейс](#user-interface)
2. [Описание основных сущностей и их интерфейсов](#object-interface)
3. [Запуск и тестирование](#dev)

<br>

### 1. Пользовательский интерфейс <a id="user-interface"></a>
![меню](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/menu.PNG)

### 2. Описание основных сущностей и их интерфейсов<a id="object-interface"></a>
В приложение присутствуюет 2 сущности:

#### Сущности

1. *Library* - представляет из себя представление (view), которое обрабатывает запросы пользователя и отправляет их архиву. Формирует в удобочитаемый формат данные полученные из архива.
2. *Archive* - имитирует работу архива библиотеки. По факту представляет из себя хранилище, в качестве ресурса хранения используется json файл, котороый храниться на жестком диске. Данные хранятся в следующем формате:

```json
{
  "t1120a1120y193": {
    "title": "cool author",
    "author": "cool author",
    "year": "1000",
    "status": "в наличии"
  },
  "t7578a1060y209": {
    "title": "Процесс",
    "author": "Франц Кафка",
    "year": "1925",
    "status": "в наличии"
  }
}
```

#### Основные интерфейсы

**add** - Добавление книги. Пользователь вводит "title", "author" и "year", после чего книга добавляется в библиотеку.

![add_cmd](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/add_cmd.PNG)

**delete** - Удаление книги. Пользователь вводит id книги, которую нужно удалить.

![delete_cmd](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/delete_cmd.PNG)

**search** - Поиск книги. Пользователь может искать книги по title, author или year

![search_cmd](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/search_cmd.PNG)

**all** - Отображение всех книг. Приложение выводит список всех книг с их id, title, author, year и status.

![all_cmd](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/all_cmd.PNG)

**change status** - Изменение статуса книги. Пользователь вводит id книги и новый статус (“в наличии” или “выдана”).

![change_status_cmd](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/change_status_cmd.PNG)

**cmd** - запросить меню с командами и описанием

![меню](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/menu.PNG)

**leave** - Выйти из библиотеки (прервать выполнение скрипта.)

![leave_cmd](https://github.com/zaritskiiAA/EM_tz/blob/main/console_app/image/leave_cmd.PNG)

### Запуск и тестирование<a id="dev"></a> 
#### Запуск
1. Иметь на машине заранее установленый интерпретатор CPython
2. Стянуть на мишану пакет с приложением по http или ssh
3. В ide или консоли открыть директорию Em_tz/
4. запустить скрипт в формате пакета `python -m console_app.main`

#### Тестирование
Сделать пункт 1-3 из подраздела Запуск
1. запустить скрипт в формате пакета `python -m console_app.test`
