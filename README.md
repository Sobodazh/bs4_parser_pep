# Проект парсинга PEP

## Технологии

[![Python](https://img.shields.io/badge/-Python-464646?style=flat&logo=Python&logoColor=ffffff&color=043A6B)](https://www.python.org/)
[![BeautifulSoup4](https://img.shields.io/badge/-BeautifulSoup4-464646?style=flat&logo=BeautifulSoup4&logoColor=ffffff&color=043A6B)](https://www.crummy.com/software/BeautifulSoup/)
[![Prettytable](https://img.shields.io/badge/-Prettytable-464646?style=flat&logo=Prettytable&logoColor=ffffff&color=043A6B)](https://github.com/jazzband/prettytable)
[![Logging](https://img.shields.io/badge/-Logging-464646?style=flat&logo=Logging&logoColor=ffffff&color=043A6B)](https://docs.python.org/3/library/logging.html)

## Описание проекта

Парсер имеет 4 режима работы:
- Whats New - (Показывает что нового есть в очередной версии языка програмирования Python)
- Latest Version - (Указывает на актуальные номера версий языка програмирования Python)
- Download - (Cкачивает архив с документацией Python на ваш локальный диск)
- PEP - (Сравнивает статусы актуальной документации, а также записывает их в файл)

## Документация

Использование: 
```
main.py [-h] [-c] {pep,whats-new,latest-versions,download} [-o {pretty,file}]
```

Обязательные аргументы:
```
  {pep,whats-new,latest-versions,download}    Режимы работы парсера
```

Необязательные аргументы:
```
  -h, --help            Показ документации
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}    Дополнительные способы вывода данных
```
