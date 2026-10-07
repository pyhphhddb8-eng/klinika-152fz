#!/usr/bin/env python3
# Разовая подрезка шрифтов: оставляем кириллицу, латиницу и нужную пунктуацию.
# Запуск: python3 tools/make_font.py
# Нужен fontTools: python3 -m pip install --user fonttools brotli
#
# Wix Madefor — пара Text и Display одного семейства: спокойный текст для
# документов и плотные заголовки. Переменные файлы сужаются до нужных толщин.
import os
import subprocess
import sys
import tempfile

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ИСХОДНИКИ = os.path.join(КОРЕНЬ, "assets", "fonts", "src")
ГОТОВЫЕ = os.path.join(КОРЕНЬ, "assets", "fonts")

# (исходный файл, готовый файл, толщины после сужения)
ШРИФТЫ = (
    ("WixMadeforText.ttf", "wix-madefor-text.woff2", "wght=400:600"),
    ("WixMadeforDisplay.ttf", "wix-madefor-display.woff2", "wght=700"),
)

# Латиница и цифры, неразрывный пробел, кавычки-ёлочки и лапки, тире,
# многоточие, кириллица с Ё, знак номера, знак рубля, копирайт, галочка.
ДИАПАЗОНЫ = (
    "U+0020-007E,U+00A0,U+00AB,U+00BB,U+00A9,U+2010-2015,"
    "U+2018-201F,U+2026,U+2116,U+20BD,U+2212,U+2713,U+0400-045F"
)

for исходный, готовый, оси in ШРИФТЫ:
    with tempfile.TemporaryDirectory() as врем:
        суженный = os.path.join(врем, "suzhennyj.ttf")
        subprocess.run(
            [sys.executable, "-m", "fontTools.varLib.instancer",
             os.path.join(ИСХОДНИКИ, исходный), оси, "-o", суженный],
            check=True, stdout=subprocess.DEVNULL,
        )
        путь = os.path.join(ГОТОВЫЕ, готовый)
        subprocess.run(
            [sys.executable, "-m", "fontTools.subset", суженный,
             "--unicodes=" + ДИАПАЗОНЫ,
             "--layout-features=kern,liga",
             "--flavor=woff2",
             "--output-file=" + путь],
            check=True,
        )
    print("готово: %s, %d КБ" % (готовый, os.path.getsize(путь) // 1024))
