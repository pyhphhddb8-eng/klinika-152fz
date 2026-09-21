#!/usr/bin/env python3
# Разовая подрезка шрифта: оставляем кириллицу, латиницу и нужную пунктуацию.
# Запуск: python3 tools/make_font.py
# Нужен fontTools: python3 -m pip install --user fonttools brotli
import os
import subprocess
import sys

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ИСХОДНЫЙ = os.path.join(КОРЕНЬ, "assets", "fonts", "src", "GolosText.ttf")
ГОТОВЫЙ = os.path.join(КОРЕНЬ, "assets", "fonts", "golos-text.woff2")

# Латиница и цифры, неразрывный пробел, кавычки-ёлочки и лапки, тире,
# многоточие, кириллица с Ё, знак номера, знак рубля, копирайт, галочка.
ДИАПАЗОНЫ = (
    "U+0020-007E,U+00A0,U+00AB,U+00BB,U+00A9,U+2010-2015,"
    "U+2018-201F,U+2026,U+2116,U+20BD,U+2212,U+2713,U+0400-045F"
)

команда = [
    sys.executable, "-m", "fontTools.subset", ИСХОДНЫЙ,
    "--unicodes=" + ДИАПАЗОНЫ,
    "--layout-features=kern,liga",
    "--flavor=woff2",
    "--output-file=" + ГОТОВЫЙ,
]
subprocess.run(команда, check=True)
print("готово: %s, %d КБ" % (os.path.basename(ГОТОВЫЙ), os.path.getsize(ГОТОВЫЙ) // 1024))
