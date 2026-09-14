#!/usr/bin/env python3
# Сборка страниц: реквизиты из content/site.json подставляются в общий шаблон.
# Запуск: python3 build.py
import json
import os
import re
import shutil
import sys

ПЛЕЙСХОЛДЕР = re.compile(r"\{\{([A-ZА-Я_]+)\}\}")

PAGES = [
    {
        "slug": "index",
        "content": "zapis.html",
        "title": "Запись на приём",
        "descr": "Демонстрационная страница записи на приём: форма без лишних полей и согласие на обработку данных.",
    },
    {
        "slug": "privacy",
        "content": "politika.html",
        "title": "Политика обработки персональных данных",
        "descr": "Политика обработки персональных данных демонстрационной клиники.",
    },
    {
        "slug": "consent",
        "content": "soglasie.html",
        "title": "Согласие на обработку персональных данных",
        "descr": "Текст согласия, на который ссылается галочка в форме записи.",
    },
    {
        "slug": "terms",
        "content": "soglashenie.html",
        "title": "Пользовательское соглашение",
        "descr": "Пользовательское соглашение демонстрационного сайта записи на приём.",
    },
]


def load_site(root):
    """Реквизиты клиники — единственный источник правды."""
    with open(os.path.join(root, "content", "site.json"), encoding="utf-8") as ф:
        return json.load(ф)


def render(text, values):
    """Заменяет {{КЛЮЧ}} на значение. Неизвестные ключи оставляет как есть —
    их поймает missing() и сборка остановится."""
    return ПЛЕЙСХОЛДЕР.sub(lambda м: values.get(м.group(1), м.group(0)), text)


def missing(text):
    """Незаполненные плейсхолдеры в порядке появления, без повторов."""
    найдено = []
    for ключ in ПЛЕЙСХОЛДЕР.findall(text):
        if ключ not in найдено:
            найдено.append(ключ)
    return найдено


def читать(путь):
    with open(путь, encoding="utf-8") as ф:
        return ф.read()


def build_all(root):
    данные = load_site(root)
    шаблон = читать(os.path.join(root, "content", "template.html"))
    записано = []

    os.makedirs(os.path.join(root, "assets"), exist_ok=True)
    shutil.copyfile(
        os.path.join(root, "content", "style.css"),
        os.path.join(root, "assets", "style.css"),
    )

    for страница in PAGES:
        содержимое = читать(os.path.join(root, "content", "pages", страница["content"]))
        значения = dict(данные)
        значения["ЗАГОЛОВОК"] = страница["title"]
        значения["ОПИСАНИЕ"] = страница["descr"]
        # Содержимое подставляем первым, чтобы плейсхолдеры внутри текстов тоже заполнились.
        текст = render(шаблон.replace("{{СОДЕРЖИМОЕ}}", содержимое), значения)
        осталось = missing(текст)
        if осталось:
            raise SystemExit(
                "Не заполнены плейсхолдеры на странице %s: %s" % (страница["slug"], ", ".join(осталось))
            )
        путь = os.path.join(root, страница["slug"] + ".html")
        with open(путь, "w", encoding="utf-8") as ф:
            ф.write(текст)
        записано.append(путь)
    return записано


if __name__ == "__main__":
    корень = os.path.dirname(os.path.abspath(__file__))
    for путь in build_all(корень):
        print("собрано:", os.path.basename(путь))
