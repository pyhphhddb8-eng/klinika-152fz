# Комплект 152-ФЗ для клиники — план работ

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Собрать демо-сайт вымышленной клиники: страница записи на приём с правильно устроенной формой плюс три документа отдельными адресами, выложенные на GitHub Pages.

**Architecture:** Четыре обычные HTML-страницы без единой зависимости в браузере. Собирает их скрипт `build.py` на стандартной библиотеке Python: один шаблон, один файл реквизитов, по файлу-фрагменту на текст каждой страницы. Реквизиты живут в одном месте и подставляются во все четыре страницы, поэтому разъехаться не могут. Шрифт подрезан и вшит в CSS строкой base64. Проверки — Playwright-скрипт `tools/check.mjs`, устроенный как в проекте `skuf-tur`.

**Tech Stack:** Python 3.9.6 (только стандартная библиотека), fontTools (разово, для подрезки шрифта), HTML + CSS + минимум ванильного JS, Node 24 + Playwright 1.63 (только проверки), GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-14-klinika-152fz-design.md`

## Global Constraints

Действуют во всех задачах без повторения.

- **Ни одной зависимости в браузере.** Ни CDN, ни внешних шрифтов, ни фреймворков, ни аналитики. Всё, что грузит страница, лежит рядом с ней.
- **Python 3.9.6, только стандартная библиотека** в `build.py`. Никакого npm-сборщика. `fontTools` вызывается один раз отдельным скриптом и в сборку не входит.
- **Node и Playwright — только для проверок.** В собранные страницы не попадают.
- **Собранные страницы лежат в корне репозитория:** `index.html`, `privacy.html`, `consent.html`, `terms.html`, папка `assets/`. Так GitHub Pages отдаёт их без настроек.
- **Реквизиты берутся только из `content/site.json`.** Руками в HTML не пишутся никогда. Это единственная причина, по которой они не разъедутся.
- **Все реквизиты условные и заведомо недействительные.** ООО «Клиника Ясень», ИНН `7700000000` (контрольная сумма не сходится), адрес «ул. Вымышленная». Реквизиты живой компании не берём.
- **Форма ничего не отправляет.** Ни `action`, ни `fetch`, ни почты. При отправке — сообщение о демонстрации.
- **В форме нет полей о здоровье.** Ни жалобы, ни симптома, ни диагноза, ни даты рождения, ни паспорта. Только имя, телефон, услуга, удобное время.
- **Информированное согласие на медицинское вмешательство (323-ФЗ) в комплект не входит.** Не добавлять ни страницей, ни ссылкой.
- **На каждой странице две оговорки:** «Демонстрационный сайт: клиника вымышленная, реквизиты условные, форма ничего не отправляет» и «Типовой комплект, а не юридическая консультация».
- **Все страницы закрыты от поисковиков:** `<meta name="robots" content="noindex, nofollow">` плюс `robots.txt`.
- **Тексты — адаптация готового комплекта** `~/Progects/tilda-yuridicheskie-dokumenty`, а не сочинение с нуля. Из `02-согласие.md` на страницу идёт **только часть после строки `## Полный текст согласия (отдельная страница)` и до строки `## Если появится рассылка`**. Первая половина файла — инструкция для исполнителя, на сайт ей нельзя.
- **Нормы проверки:** контраст текста по WCAG не ниже 4,5 (крупный — 3,0), нет горизонтальной прокрутки при ширине 360 px, консоль браузера чистая, документы читаемо печатаются в PDF.
- **Комментарии в коде и сообщения коммитов — по-русски**, как в соседних проектах.

---

## Структура файлов

```
klinika-152fz/
  build.py                     сборщик: реквизиты + шаблон + фрагменты → 4 страницы
  content/
    site.json                  реквизиты клиники и адреса документов — единственный источник
    template.html              общий шаблон страницы: голова, шапка, оговорки, подвал
    style.css                  общий стиль, включая правила печати
    pages/
      zapis.html               содержимое страницы записи: форма и объясняющие блоки
      politika.html            текст политики
      soglasie.html            текст согласия
      soglashenie.html         текст пользовательского соглашения
  assets/
    fonts/src/GolosText.ttf    исходный шрифт (OFL) и OFL.txt рядом
    fonts/golos-text.woff2     подрезанный шрифт
    fonts.css                  генерируется сборщиком: @font-face с base64
    style.css                  копия content/style.css, кладёт сборщик
  tools/
    make_font.py               разовая подрезка шрифта
    test_build.py              тесты сборщика (unittest, стандартная библиотека)
    check.mjs                  проверки в браузере (Playwright)
    shot.mjs                   скриншоты для показа
  index.html privacy.html consent.html terms.html   собранные страницы
  robots.txt  .nojekyll
  docs/superpowers/            спека и этот план
```

Почему так: правка одного ИНН должна быть одной правкой. Тексты документов отделены от разметки страницы, потому что меняться будут именно они. Проверки отделены от сборки, потому что запускаются в другой момент и другим инструментом.

---

### Task 1: Сборщик, реквизиты и шаблон

Каркас: четыре страницы собираются из одного шаблона, реквизиты подставляются из одного файла. Содержимого пока почти нет — появится в следующих задачах.

**Files:**
- Create: `build.py`
- Create: `content/site.json`
- Create: `content/template.html`
- Create: `content/pages/zapis.html`, `content/pages/politika.html`, `content/pages/soglasie.html`, `content/pages/soglashenie.html`
- Test: `tools/test_build.py`

**Interfaces:**
- Consumes: ничего, это первая задача.
- Produces:
  - `build.load_site(root: str) -> dict` — читает `content/site.json`, возвращает словарь замен.
  - `build.render(text: str, values: dict) -> str` — заменяет `{{КЛЮЧ}}` на значение.
  - `build.missing(text: str) -> list` — список незаполненных плейсхолдеров, в порядке появления, без повторов.
  - `build.PAGES` — список словарей с ключами `slug`, `content`, `title`, `descr`.
  - `build.build_all(root: str) -> list` — собирает всё, возвращает список записанных путей.

- [ ] **Step 1: Написать падающий тест**

Создать `tools/test_build.py`:

```python
# Тесты сборщика. Запуск: python3 tools/test_build.py -v
import os
import sys
import unittest

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, КОРЕНЬ)
import build


class ТестПодстановки(unittest.TestCase):
    def test_подставляет_значение(self):
        self.assertEqual(build.render("ИНН {{ИНН}}", {"ИНН": "7700000000"}), "ИНН 7700000000")

    def test_подставляет_во_всех_местах(self):
        self.assertEqual(build.render("{{A}} и {{A}}", {"A": "да"}), "да и да")

    def test_находит_незаполненные(self):
        self.assertEqual(build.missing("а {{X}} б {{Y}} в {{X}}"), ["X", "Y"])

    def test_на_заполненном_тексте_пусто(self):
        self.assertEqual(build.missing("всё на месте"), [])


class ТестСборки(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.пути = build.build_all(КОРЕНЬ)
        cls.страницы = {}
        for имя in ("index.html", "privacy.html", "consent.html", "terms.html"):
            путь = os.path.join(КОРЕНЬ, имя)
            with open(путь, encoding="utf-8") as ф:
                cls.страницы[имя] = ф.read()

    def test_собрались_четыре_страницы(self):
        self.assertEqual(len(self.пути), 4)

    def test_не_осталось_плейсхолдеров(self):
        for имя, текст in self.страницы.items():
            self.assertEqual(build.missing(текст), [], "незаполнено в " + имя)

    def test_реквизиты_совпадают_во_всех_страницах(self):
        данные = build.load_site(КОРЕНЬ)
        for поле in ("ОПЕРАТОР", "ИНН", "ОГРН", "АДРЕС", "ТЕЛЕФОН", "EMAIL"):
            for имя, текст in self.страницы.items():
                self.assertIn(данные[поле], текст, поле + " не найден в " + имя)

    def test_страницы_закрыты_от_поисковиков(self):
        for имя, текст in self.страницы.items():
            self.assertIn('name="robots" content="noindex, nofollow"', текст, имя)


if __name__ == "__main__":
    unittest.main(verbosity=2)
```

- [ ] **Step 2: Запустить тест и убедиться, что он падает**

Запустить: `python3 tools/test_build.py -v`
Ожидается: `ModuleNotFoundError: No module named 'build'`

- [ ] **Step 3: Создать файл реквизитов**

Создать `content/site.json`. Все значения условные и заведомо недействительные — это часть задумки, а не заглушки, которые потом заменят.

```json
{
  "НАЗВАНИЕ": "Клиника «Ясень»",
  "ОПЕРАТОР": "Общество с ограниченной ответственностью «Клиника Ясень»",
  "ОПЕРАТОР_КРАТКО": "ООО «Клиника Ясень»",
  "ИНН": "7700000000",
  "ОГРН": "1000000000000",
  "АДРЕС": "000000, г. Москва, ул. Вымышленная, д. 1, пом. 1",
  "EMAIL": "info@klinika-yasen.example",
  "ТЕЛЕФОН": "+7 (495) 000-00-00",
  "САЙТ": "pyhphhddb8-eng.github.io/klinika-152fz",
  "ДАТА": "14 сентября 2026 г.",
  "ЛИЦЕНЗИЯ": "Л00-00000-00/00000000 (условный номер, лицензии не существует)",
  "ССЫЛКА_ПОЛИТИКА": "privacy.html",
  "ССЫЛКА_СОГЛАСИЕ": "consent.html",
  "ССЫЛКА_СОГЛАШЕНИЕ": "terms.html",
  "ГОД": "2026"
}
```

- [ ] **Step 4: Создать шаблон страницы**

Создать `content/template.html`. Подвал и оговорки появятся в задаче 3, сейчас только каркас.

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{{ЗАГОЛОВОК}} — {{НАЗВАНИЕ}}</title>
<meta name="description" content="{{ОПИСАНИЕ}}">
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="shapka">
  <a class="shapka__logo" href="index.html">{{НАЗВАНИЕ}}</a>
</header>
<main class="stranica">
{{СОДЕРЖИМОЕ}}
</main>
<footer class="podval">
  <p>{{ОПЕРАТОР}} ({{ОПЕРАТОР_КРАТКО}}), ИНН {{ИНН}}, ОГРН {{ОГРН}}. {{АДРЕС}}. {{ТЕЛЕФОН}}, {{EMAIL}}.</p>
</footer>
</body>
</html>
```

- [ ] **Step 5: Создать четыре файла содержимого**

Заглушки, чтобы сборка заработала. Настоящие тексты — задачи 4–6.

```bash
mkdir -p content/pages
printf '<h1>Запись на приём</h1>\n' > content/pages/zapis.html
printf '<h1>Политика обработки персональных данных</h1>\n' > content/pages/politika.html
printf '<h1>Согласие на обработку персональных данных</h1>\n' > content/pages/soglasie.html
printf '<h1>Пользовательское соглашение</h1>\n' > content/pages/soglashenie.html
```

- [ ] **Step 6: Написать сборщик**

Создать `build.py`:

```python
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
```

В этой задаче `content/style.css` ещё нет — создать пустой файл, чтобы копирование не падало:

```bash
touch content/style.css
```

- [ ] **Step 7: Запустить сборку и тесты**

Запустить: `python3 build.py && python3 tools/test_build.py -v`
Ожидается: печатает четыре собранных файла, все тесты PASS.

- [ ] **Step 8: Коммит**

```bash
git add build.py content tools/test_build.py index.html privacy.html consent.html terms.html assets
git commit -m "Сборщик страниц: один шаблон, один файл реквизитов, четыре страницы"
```

---

### Task 2: Вшитый шрифт и общий стиль

Шрифт подрезается один раз и вшивается в CSS строкой base64 — страница не делает ни одного запроса наружу. Плюс базовый стиль, на котором дальше держится всё остальное, включая печать документов в PDF.

**Files:**
- Create: `tools/make_font.py`
- Create: `assets/fonts/src/GolosText.ttf`, `assets/fonts/src/OFL.txt` (скачиваются), `assets/fonts/golos-text.woff2` (генерируется)
- Create: `content/style.css` (сейчас пустой — наполняется)
- Modify: `build.py` (добавляется генерация `assets/fonts.css`)
- Test: `tools/test_build.py` (добавляется класс `ТестШрифта`)

**Interfaces:**
- Consumes: `build.build_all`, `build.load_site` из задачи 1.
- Produces: `build.build_fonts_css(root: str) -> str` — читает `assets/fonts/golos-text.woff2`, пишет `assets/fonts.css` с `@font-face` и base64, возвращает путь. Вызывается из `build_all`.

- [ ] **Step 1: Написать падающий тест**

Дописать в конец `tools/test_build.py` перед блоком `if __name__`:

```python
class ТестШрифта(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build_all(КОРЕНЬ)
        with open(os.path.join(КОРЕНЬ, "assets", "fonts.css"), encoding="utf-8") as ф:
            cls.css = ф.read()

    def test_шрифт_вшит_строкой_base64(self):
        self.assertIn("data:font/woff2;base64,", self.css)

    def test_нет_запросов_наружу(self):
        for имя in ("index.html", "privacy.html", "consent.html", "terms.html"):
            with open(os.path.join(КОРЕНЬ, имя), encoding="utf-8") as ф:
                текст = ф.read()
            self.assertNotIn("http://", текст, имя)
            self.assertNotIn("https://fonts.", текст, имя)
        self.assertNotIn("http", self.css.replace("data:font", ""))

    def test_шрифт_не_раздут(self):
        размер = os.path.getsize(os.path.join(КОРЕНЬ, "assets", "fonts", "golos-text.woff2"))
        self.assertLess(размер, 120 * 1024, "подрезка не сработала, шрифт %d байт" % размер)
```

- [ ] **Step 2: Запустить тест и убедиться, что он падает**

Запустить: `python3 tools/test_build.py -v`
Ожидается: FAIL — `assets/fonts.css` не существует (`FileNotFoundError`).

- [ ] **Step 3: Скачать исходный шрифт и лицензию**

Golos Text — кириллический шрифт под лицензией OFL, её текст обязан лежать рядом.

```bash
mkdir -p assets/fonts/src
curl -sL -o assets/fonts/src/GolosText.ttf \
  'https://raw.githubusercontent.com/google/fonts/main/ofl/golostext/GolosText%5Bwght%5D.ttf'
curl -sL -o assets/fonts/src/OFL.txt \
  'https://raw.githubusercontent.com/google/fonts/main/ofl/golostext/OFL.txt'
ls -la assets/fonts/src
```

Ожидается: `.ttf` порядка 200–400 КБ, `OFL.txt` непустой.

- [ ] **Step 4: Написать скрипт подрезки**

Создать `tools/make_font.py`. Он запускается руками и только когда меняется набор символов — в обычную сборку не входит.

```python
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
```

Запустить: `python3 tools/make_font.py`
Ожидается: строка «готово: golos-text.woff2, N КБ», N меньше 120.

- [ ] **Step 5: Научить сборщик вшивать шрифт**

В `build.py` добавить `import base64` к остальным импортам и функцию перед `build_all`:

```python
def build_fonts_css(root):
    """Вшивает подрезанный шрифт в CSS строкой base64: страница не ходит наружу."""
    путь_шрифта = os.path.join(root, "assets", "fonts", "golos-text.woff2")
    with open(путь_шрифта, "rb") as ф:
        строка = base64.b64encode(ф.read()).decode("ascii")
    css = (
        "/* Golos Text, лицензия OFL — текст в assets/fonts/src/OFL.txt.\n"
        "   Файл создаётся сборщиком, править руками бессмысленно. */\n"
        "@font-face{\n"
        "  font-family:'Golos Text';\n"
        "  src:url(data:font/woff2;base64,%s) format('woff2');\n"
        "  font-weight:400 700;\n"
        "  font-display:swap;\n"
        "}\n" % строка
    )
    путь = os.path.join(root, "assets", "fonts.css")
    with open(путь, "w", encoding="utf-8") as ф:
        ф.write(css)
    return путь
```

И вызвать её в `build_all` сразу после `os.makedirs(...)`:

```python
    build_fonts_css(root)
```

- [ ] **Step 6: Написать общий стиль**

Записать `content/style.css`. Цвета подобраны так, чтобы контраст основного текста был выше 4,5 — это проверяется в задаче 7.

```css
/* Общий стиль всех четырёх страниц. Правится здесь, сборщик копирует в assets/. */
:root{
  --text:#1b1f23;
  --muted:#4a5560;
  --line:#dfe4e8;
  --bg:#ffffff;
  --bg-soft:#f4f7f9;
  --accent:#0b5c4b;
  --accent-dark:#084335;
  --warn-bg:#fff6e5;
  --warn-line:#e0b872;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{
  margin:0;
  font-family:'Golos Text',-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;
  font-size:17px;
  line-height:1.6;
  color:var(--text);
  background:var(--bg);
}
img{max-width:100%}
a{color:var(--accent-dark)}
a:hover{color:var(--accent)}

.shapka{border-bottom:1px solid var(--line);padding:16px 20px}
.shapka__logo{font-weight:700;font-size:19px;text-decoration:none;color:var(--text)}

.stranica{max-width:760px;margin:0 auto;padding:24px 20px 56px}
.stranica h1{font-size:30px;line-height:1.25;margin:0 0 16px}
.stranica h2{font-size:22px;line-height:1.3;margin:32px 0 10px}
.stranica h3{font-size:19px;margin:24px 0 8px}
.stranica p,.stranica li{color:var(--text)}
.stranica ul,.stranica ol{padding-left:22px}

.podval{border-top:1px solid var(--line);background:var(--bg-soft);padding:24px 20px;font-size:15px;color:var(--muted)}
.podval a{color:var(--accent-dark)}

@media (max-width:420px){
  .stranica h1{font-size:25px}
  .stranica{padding:20px 16px 40px}
}

/* Печать: документ должен читаться в PDF, интерфейс — нет. */
@media print{
  .shapka,.cookie,.zapis__forma,.demo-note{display:none !important}
  body{font-size:12pt;color:#000;background:#fff}
  .stranica{max-width:none;padding:0}
  .stranica h2{page-break-after:avoid}
  .stranica p,.stranica li{page-break-inside:avoid}
  a[href^="http"]::after{content:" (" attr(href) ")";font-size:10pt;color:#444}
}
```

- [ ] **Step 7: Собрать и прогнать тесты**

Запустить: `python3 build.py && python3 tools/test_build.py -v`
Ожидается: все тесты PASS, включая три новых про шрифт.

- [ ] **Step 8: Посмотреть глазами**

Запустить: `open index.html`
Ожидается: заголовок набран Golos Text, а не системным шрифтом.

- [ ] **Step 9: Коммит**

```bash
git add tools/make_font.py content/style.css build.py tools/test_build.py assets
git commit -m "Подрезанный шрифт вшит в CSS, общий стиль и правила печати"
```

---

### Task 3: Подвал с реквизитами, оговорки, cookie-баннер

Три вещи, общие для всех четырёх страниц, поэтому все три живут в шаблоне. Подвал с реквизитами — одно из четырёх решений, ради которых делается работа.

**Files:**
- Modify: `content/template.html`
- Modify: `content/style.css`
- Create: `robots.txt`, `.nojekyll`
- Test: `tools/test_build.py` (класс `ТестОбщихБлоков`)

**Interfaces:**
- Consumes: `build.build_all`, `build.load_site`, `build.PAGES`.
- Produces: разметку, на которую опираются проверки в задаче 7: `.demo-note`, `.pravovaya-ogovorka`, `.podval`, `.cookie`, `#cookie-soglasen`.

- [ ] **Step 1: Написать падающий тест**

Дописать в `tools/test_build.py`:

```python
class ТестОбщихБлоков(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build_all(КОРЕНЬ)
        cls.страницы = {}
        for стр in build.PAGES:
            имя = стр["slug"] + ".html"
            with open(os.path.join(КОРЕНЬ, имя), encoding="utf-8") as ф:
                cls.страницы[имя] = ф.read()

    def test_оговорка_про_демо_на_каждой_странице(self):
        for имя, текст in self.страницы.items():
            self.assertIn("клиника вымышленная", текст, имя)
            self.assertIn("форма ничего не отправляет", текст, имя)

    def test_оговорка_про_не_консультацию_на_каждой_странице(self):
        for имя, текст in self.страницы.items():
            self.assertIn("не юридическая консультация", текст, имя)

    def test_ссылки_на_все_документы_с_каждой_страницы(self):
        for имя, текст in self.страницы.items():
            for адрес in ("privacy.html", "consent.html", "terms.html", "index.html"):
                self.assertIn('href="' + адрес + '"', текст, адрес + " не найден в " + имя)

    def test_подвал_содержит_реквизиты(self):
        данные = build.load_site(КОРЕНЬ)
        for имя, текст in self.страницы.items():
            подвал = текст.split('<footer class="podval">')[1]
            for поле in ("ОПЕРАТОР_КРАТКО", "ИНН", "ОГРН", "АДРЕС", "ТЕЛЕФОН", "EMAIL"):
                self.assertIn(данные[поле], подвал, поле + " не в подвале " + имя)

    def test_cookie_баннер_есть_и_скрыт_по_умолчанию(self):
        for имя, текст in self.страницы.items():
            self.assertIn('class="cookie" hidden', текст, имя)
```

- [ ] **Step 2: Запустить тест и убедиться, что он падает**

Запустить: `python3 tools/test_build.py -v`
Ожидается: FAIL на `test_оговорка_про_демо_на_каждой_странице` и остальных новых.

- [ ] **Step 3: Дописать шаблон**

Заменить содержимое `content/template.html` на:

```html
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{{ЗАГОЛОВОК}} — {{НАЗВАНИЕ}}</title>
<meta name="description" content="{{ОПИСАНИЕ}}">
<link rel="stylesheet" href="assets/fonts.css">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<p class="demo-note">Демонстрационный сайт: клиника вымышленная, реквизиты условные, форма ничего не отправляет.</p>

<header class="shapka">
  <a class="shapka__logo" href="index.html">{{НАЗВАНИЕ}}</a>
</header>

<main class="stranica">
{{СОДЕРЖИМОЕ}}
<p class="pravovaya-ogovorka">Это типовой комплект документов, а не юридическая консультация. Требования меняются, спорные места и всё, что касается конкретной деятельности клиники, смотрит её юрист.</p>
</main>

<footer class="podval">
  <p class="podval__rekvizity">{{ОПЕРАТОР}}<br>
  ИНН {{ИНН}}, ОГРН {{ОГРН}}<br>
  {{АДРЕС}}<br>
  <a href="tel:+74950000000">{{ТЕЛЕФОН}}</a>, <a href="mailto:{{EMAIL}}">{{EMAIL}}</a><br>
  Медицинская лицензия: {{ЛИЦЕНЗИЯ}}</p>
  <nav class="podval__ssylki">
    <a href="index.html">Запись на приём</a>
    <a href="{{ССЫЛКА_ПОЛИТИКА}}">Политика обработки персональных данных</a>
    <a href="{{ССЫЛКА_СОГЛАСИЕ}}">Согласие на обработку</a>
    <a href="{{ССЫЛКА_СОГЛАШЕНИЕ}}">Пользовательское соглашение</a>
  </nav>
  <p class="podval__god">© {{ГОД}} {{ОПЕРАТОР_КРАТКО}}. Реквизиты условные: компании не существует.</p>
</footer>

<div class="cookie" hidden>
  <p>Сайт использует cookie, необходимые для его работы. Подробнее — в <a href="{{ССЫЛКА_ПОЛИТИКА}}">политике обработки персональных данных</a>.</p>
  <button type="button" id="cookie-soglasen">Понятно</button>
</div>

<script>
// Cookie-баннер: показываем один раз. Хранилище может быть недоступно
// (приватное окно, открытие файла с диска) — тогда просто не показываем.
(function () {
  var баннер = document.querySelector('.cookie');
  var кнопка = document.getElementById('cookie-soglasen');
  var КЛЮЧ = 'cookie-ok';
  var хранилище = null;
  try { хранилище = window.localStorage; хранилище.getItem(КЛЮЧ); } catch (e) { хранилище = null; }
  if (!хранилище || хранилище.getItem(КЛЮЧ) === '1') { return; }
  баннер.hidden = false;
  кнопка.addEventListener('click', function () {
    баннер.hidden = true;
    try { хранилище.setItem(КЛЮЧ, '1'); } catch (e) {}
  });
})();
</script>
</body>
</html>
```

- [ ] **Step 4: Дописать стиль**

Добавить в конец `content/style.css` **перед** блоком `@media print`:

```css
.demo-note{
  margin:0;padding:10px 20px;
  background:var(--warn-bg);border-bottom:1px solid var(--warn-line);
  font-size:15px;color:#4a3c1d;text-align:center;
}
.pravovaya-ogovorka{
  margin-top:40px;padding:14px 16px;
  background:var(--bg-soft);border-left:3px solid var(--accent);
  font-size:15px;color:var(--muted);
}
.podval__rekvizity{margin:0 0 16px}
.podval__ssylki{display:flex;flex-direction:column;gap:6px;margin-bottom:16px}
.podval__god{margin:0;font-size:14px}

.cookie{
  position:fixed;left:12px;right:12px;bottom:12px;z-index:10;
  display:flex;flex-wrap:wrap;align-items:center;gap:12px;
  max-width:760px;margin:0 auto;padding:14px 16px;
  background:#ffffff;border:1px solid var(--line);border-radius:10px;
  box-shadow:0 6px 24px rgba(20,30,40,.14);
  font-size:15px;
}
.cookie p{margin:0;flex:1 1 240px}
.cookie button{
  padding:9px 18px;border:0;border-radius:8px;
  background:var(--accent);color:#fff;font:inherit;cursor:pointer;
}
.cookie button:hover{background:var(--accent-dark)}
.cookie[hidden]{display:none}
```

- [ ] **Step 5: Создать robots.txt и .nojekyll**

```bash
printf 'User-agent: *\nDisallow: /\n' > robots.txt
touch .nojekyll
```

`.nojekyll` нужен, чтобы GitHub Pages отдавал файлы как есть; `robots.txt` — потому что демо с вымышленной клиникой в выдаче не место.

- [ ] **Step 6: Собрать и прогнать тесты**

Запустить: `python3 build.py && python3 tools/test_build.py -v`
Ожидается: все тесты PASS.

- [ ] **Step 7: Коммит**

```bash
git add content/template.html content/style.css robots.txt .nojekyll tools/test_build.py index.html privacy.html consent.html terms.html assets
git commit -m "Подвал с реквизитами, оговорки на каждой странице, cookie-баннер, закрытие от поисковиков"
```

---

### Task 4: Форма записи и галочка, которая действительно блокирует отправку

Главная проверяемая вещь во всей работе. Галочка пустая при загрузке, без неё отправка не проходит, рядом написано почему. С ней — сообщение, что это демонстрация.

**Files:**
- Modify: `content/pages/zapis.html`
- Modify: `content/style.css`
- Create: `tools/check.mjs`
- Create: `package.json`
- Test: `tools/check.mjs` (запускается `npm run check`), плюс класс `ТестФормы` в `tools/test_build.py`

**Interfaces:**
- Consumes: шаблон и стиль из задач 1–3; `{{ССЫЛКА_СОГЛАСИЕ}}`, `{{ССЫЛКА_ПОЛИТИКА}}` из `content/site.json`.
- Produces: разметку, на которую опираются проверки: форма `#zapis`, поля `#imya`, `#telefon`, `#usluga`, `#vremya`, галочка `#soglasie`, кнопка `#otpravit`, ошибка `#oshibka`, сообщение `#itog`.

- [ ] **Step 1: Завести package.json и написать падающую проверку**

Создать `package.json`:

```json
{
  "name": "klinika-152fz",
  "version": "1.0.0",
  "private": "true",
  "type": "module",
  "description": "Комплект 152-ФЗ для сайта с онлайн-записью",
  "scripts": {
    "build": "python3 build.py",
    "test": "python3 tools/test_build.py -v",
    "check": "node tools/check.mjs",
    "shot": "node tools/shot.mjs"
  },
  "devDependencies": {
    "playwright": "^1.63.0"
  }
}
```

Создать `tools/check.mjs` — в этой задаче только проверки формы, остальное добавится в задаче 7:

```javascript
// Проверки в браузере. Запуск: npm run check
// Поднимает локальный сервер, потому что localStorage не работает при открытии файла с диска.
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const КОРЕНЬ = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ПОРТ = 8765;
const АДРЕС = `http://127.0.0.1:${ПОРТ}/`;

const сервер = spawn('python3', ['-m', 'http.server', String(ПОРТ), '--bind', '127.0.0.1'],
  { cwd: КОРЕНЬ, stdio: 'ignore' });
await new Promise(р => setTimeout(р, 700));

const провалы = [];
const browser = await chromium.launch();

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 } });
  await page.goto(АДРЕС + 'index.html', { waitUntil: 'load' });

  // 1. Галочка при загрузке пустая. Предзаполненная согласием не считается.
  if (await page.isChecked('#soglasie')) провалы.push('Галочка согласия предзаполнена');

  // 2. Без галочки форма не отправляется.
  await page.fill('#imya', 'Иван Петров');
  await page.fill('#telefon', '+7 999 000-00-00');
  await page.selectOption('#usluga', { index: 1 });
  await page.fill('#vremya', 'Будни после 18:00');
  await page.click('#otpravit');
  if (await page.isVisible('#itog')) провалы.push('Форма отправилась без галочки согласия');
  if (!(await page.isVisible('#oshibka'))) провалы.push('Без галочки не показано объяснение, почему не отправляется');

  // 3. С галочкой — сообщение о демонстрации.
  await page.check('#soglasie');
  await page.click('#otpravit');
  const итог = (await page.textContent('#itog')) || '';
  if (!/демонстрац/i.test(итог)) провалы.push('С галочкой не показано сообщение о демонстрации: «' + итог.trim() + '»');

  // 4. Ссылка из галочки ведёт на согласие и открывается отдельной вкладкой.
  const ссылка = page.locator('.soglasie-stroka a[href="consent.html"]');
  if (!(await ссылка.count())) провалы.push('Рядом с галочкой нет ссылки на согласие');
  else if ((await ссылка.first().getAttribute('target')) !== '_blank') провалы.push('Ссылка на согласие открывается не отдельной вкладкой');

  // 5. В форме нет полей о здоровье.
  const поля = await page.$$eval('#zapis input, #zapis select, #zapis textarea',
    у => у.map(э => (э.id + ' ' + (э.name || '') + ' ' + (э.placeholder || '')).toLowerCase()));
  const запрещённые = ['жалоб', 'симптом', 'диагноз', 'болезн', 'рожден', 'паспорт', 'полис', 'снилс'];
  for (const поле of поля)
    for (const слово of запрещённые)
      if (поле.includes(слово)) провалы.push(`Поле о здоровье или документе в форме: «${поле.trim()}»`);
} finally {
  await browser.close();
  сервер.kill();
}

if (провалы.length) { console.error('ПРОВЕРКА НЕ ПРОЙДЕНА:\n- ' + провалы.join('\n- ')); process.exit(1); }
console.log('Проверка пройдена: галочка пустая и блокирует отправку, лишних полей нет.');
```

- [ ] **Step 2: Поставить Playwright и запустить проверку — она должна упасть**

```bash
npm install
npx playwright install chromium
npm run check
```

Ожидается: FAIL — на странице ещё нет формы, падает на `#soglasie` (таймаут поиска элемента).

- [ ] **Step 3: Написать форму**

Записать `content/pages/zapis.html`:

```html
<h1>Запись на приём</h1>

<p class="lid">Оставьте имя и телефон — администратор перезвонит, подберёт врача и подтвердит время. Ни жалоб, ни диагнозов на сайте: об этом поговорим на приёме.</p>

<form class="zapis__forma" id="zapis" novalidate>
  <div class="pole">
    <label for="imya">Как к вам обращаться</label>
    <input type="text" id="imya" name="imya" autocomplete="name" placeholder="Иван Петров" required>
  </div>

  <div class="pole">
    <label for="telefon">Телефон</label>
    <input type="tel" id="telefon" name="telefon" autocomplete="tel" placeholder="+7 900 000-00-00" required>
  </div>

  <div class="pole">
    <label for="usluga">Куда записываемся</label>
    <select id="usluga" name="usluga" required>
      <option value="">Выберите приём</option>
      <option>Приём терапевта</option>
      <option>Приём офтальмолога</option>
      <option>Приём дерматолога</option>
      <option>Профилактический осмотр</option>
      <option>Не знаю, нужна помощь администратора</option>
    </select>
  </div>

  <div class="pole">
    <label for="vremya">Когда вам удобно</label>
    <input type="text" id="vremya" name="vremya" placeholder="Будни после 18:00 или суббота утром">
  </div>

  <div class="soglasie-stroka">
    <input type="checkbox" id="soglasie" name="soglasie">
    <label for="soglasie">Я согласен на обработку моих персональных данных на условиях <a href="{{ССЫЛКА_СОГЛАСИЕ}}" target="_blank" rel="noopener">согласия</a> и ознакомился с <a href="{{ССЫЛКА_ПОЛИТИКА}}" target="_blank" rel="noopener">политикой обработки персональных данных</a>.</label>
  </div>

  <p class="podskazka">Галочка не стоит заранее. Предзаполненная галочка согласием не считается: согласие должно быть конкретным и осознанным действием посетителя, а не состоянием страницы по умолчанию.</p>

  <p class="oshibka" id="oshibka" hidden role="alert">Без согласия на обработку персональных данных заявку принять нельзя: имя и телефон — это персональные данные, и обрабатывать их без вашего согласия оператор не вправе.</p>

  <button type="submit" id="otpravit">Записаться на приём</button>

  <p class="itog" id="itog" hidden role="status"></p>
</form>

<script>
// Форма ничего никуда не отправляет: это демонстрация комплекта документов.
// Собирать персональные данные посетителей на странице про их защиту — плохая шутка.
(function () {
  var форма = document.getElementById('zapis');
  var галочка = document.getElementById('soglasie');
  var ошибка = document.getElementById('oshibka');
  var итог = document.getElementById('itog');

  галочка.addEventListener('change', function () {
    if (галочка.checked) { ошибка.hidden = true; }
  });

  форма.addEventListener('submit', function (событие) {
    событие.preventDefault();
    итог.hidden = true;
    if (!галочка.checked) {
      ошибка.hidden = false;
      галочка.focus();
      return;
    }
    ошибка.hidden = true;
    итог.textContent = 'Это демонстрация: заявка никуда не отправлена и нигде не сохранена. На рабочем сайте здесь стояла бы отправка в российскую CRM или на почту на российском домене.';
    итог.hidden = false;
  });
})();
</script>
```

- [ ] **Step 4: Дописать стиль формы**

Добавить в `content/style.css` перед блоком `@media print`:

```css
.lid{font-size:19px;color:var(--muted);margin:0 0 28px}

.zapis__forma{
  padding:22px 20px;border:1px solid var(--line);border-radius:12px;background:var(--bg-soft);
}
.pole{margin-bottom:16px}
.pole label{display:block;margin-bottom:6px;font-weight:600;font-size:15px}
.pole input,.pole select{
  width:100%;padding:11px 12px;font:inherit;color:var(--text);
  background:#fff;border:1px solid #b9c3cb;border-radius:8px;
}
.pole input:focus,.pole select:focus,#soglasie:focus-visible,#otpravit:focus-visible{
  outline:2px solid var(--accent);outline-offset:2px;
}
.pole input::placeholder{color:#6b7680}

.soglasie-stroka{display:flex;gap:10px;align-items:flex-start;margin:22px 0 10px}
.soglasie-stroka input{margin-top:4px;width:18px;height:18px;flex:0 0 auto;accent-color:var(--accent)}
.soglasie-stroka label{font-size:15px;line-height:1.5}

.podskazka{margin:0 0 14px;font-size:14px;color:var(--muted)}
.oshibka{
  margin:0 0 14px;padding:11px 13px;font-size:15px;
  color:#7a1b1b;background:#fdecec;border:1px solid #e7b4b4;border-radius:8px;
}
.oshibka[hidden],.itog[hidden]{display:none}
#otpravit{
  width:100%;padding:13px 20px;font:inherit;font-weight:600;
  color:#fff;background:var(--accent);border:0;border-radius:9px;cursor:pointer;
}
#otpravit:hover{background:var(--accent-dark)}
.itog{
  margin:14px 0 0;padding:12px 14px;font-size:15px;
  color:#0f3d32;background:#e7f4ef;border:1px solid #9ccdbd;border-radius:8px;
}
```

- [ ] **Step 5: Собрать и прогнать проверку**

Запустить: `npm run build && npm run check`
Ожидается: «Проверка пройдена: галочка пустая и блокирует отправку, лишних полей нет.»

- [ ] **Step 6: Добавить тест разметки в питоновские тесты**

Дописать в `tools/test_build.py`:

```python
class ТестФормы(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build_all(КОРЕНЬ)
        with open(os.path.join(КОРЕНЬ, "index.html"), encoding="utf-8") as ф:
            cls.текст = ф.read()

    def test_галочка_не_предзаполнена_в_разметке(self):
        import re
        теги = re.findall(r"<input[^>]*type=\"checkbox\"[^>]*>", self.текст)
        self.assertEqual(len(теги), 1, "ожидалась ровно одна галочка, найдено %d" % len(теги))
        self.assertNotIn("checked", теги[0])

    def test_форма_никуда_не_отправляет(self):
        self.assertNotIn("action=", self.текст.split("<form")[1].split(">")[0])
        self.assertNotIn("fetch(", self.текст)

    def test_нет_полей_про_здоровье(self):
        for слово in ("жалоб", "симптом", "диагноз", "паспорт", "СНИЛС", "полис"):
            куски = self.текст.split("<form")[1].split("</form>")[0]
            self.assertNotIn(слово, куски, "в форме встретилось «%s»" % слово)
```

Запустить: `npm test`
Ожидается: все тесты PASS.

- [ ] **Step 7: Коммит**

```bash
git add package.json package-lock.json tools/check.mjs tools/test_build.py content/pages/zapis.html content/style.css index.html assets
git commit -m "Форма записи: четыре поля, непредзаполненная галочка, блокировка отправки без согласия"
```

---

### Task 5: Объясняющие блоки на странице записи

Работа ценна не текстами, а решениями. Два из них нужно назвать вслух прямо на странице: почему в форме нет лишних полей и куда физически падают заявки. Без этих блоков демо выглядит как обычный лендинг.

**Files:**
- Modify: `content/pages/zapis.html`
- Modify: `content/style.css`
- Test: `tools/test_build.py` (класс `ТестОбъясняющихБлоков`)

**Interfaces:**
- Consumes: страницу записи из задачи 4.
- Produces: секции `#pochemu-malo-poley` и `#kuda-padayut-zayavki`, на которые ссылаются проверки и скриншоты.

- [ ] **Step 1: Написать падающий тест**

Дописать в `tools/test_build.py`:

```python
class ТестОбъясняющихБлоков(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build_all(КОРЕНЬ)
        with open(os.path.join(КОРЕНЬ, "index.html"), encoding="utf-8") as ф:
            cls.текст = ф.read()

    def test_есть_блок_про_лишние_поля(self):
        self.assertIn('id="pochemu-malo-poley"', self.текст)

    def test_есть_блок_про_место_хранения_заявок(self):
        self.assertIn('id="kuda-padayut-zayavki"', self.текст)

    def test_названы_негодные_приёмники(self):
        for сервис in ("Google", "Zapier", "Airtable"):
            self.assertIn(сервис, self.текст, сервис + " не упомянут")

    def test_названы_годные_приёмники(self):
        for сервис in ("amoCRM", "Битрикс24"):
            self.assertIn(сервис, self.текст, сервис + " не упомянут")

    def test_telegram_только_дублирующим(self):
        self.assertIn("Telegram", self.текст)
        кусок = self.текст.split("Telegram", 1)[1][:400]
        self.assertIn("дубл", кусок, "про Telegram не сказано, что он только дублирующий")
```

- [ ] **Step 2: Запустить тест и убедиться, что он падает**

Запустить: `npm test`
Ожидается: FAIL на `test_есть_блок_про_лишние_поля` и остальных новых.

- [ ] **Step 3: Дописать блоки на страницу**

Добавить в конец `content/pages/zapis.html` **перед** тегом `<script>`:

```html
<section class="razbor" id="pochemu-malo-poley">
  <h2>Почему в форме всего четыре поля</h2>
  <p>Форма спрашивает имя, телефон, вид приёма и удобное время — и ничего больше. Это не экономия на вёрстке, а решение, принятое до начала работы.</p>
  <p>Как только сайт спрашивает про жалобу, симптом или диагноз, он начинает собирать сведения о состоянии здоровья. Это специальная категория персональных данных: к согласию, хранению и доступу к ним требования строже, а цена ошибки выше. Дата рождения, номер полиса и паспортные данные тоже лишние — их спросят в регистратуре, где для этого есть основания и защищённый контур.</p>
  <p><strong>Самый полезный совет клинике: не спрашивать на сайте то, что всё равно спросят на приёме.</strong> Каждое лишнее поле — это данные, которые придётся защищать, хранить и уметь удалить по требованию.</p>
</section>

<section class="razbor" id="kuda-padayut-zayavki">
  <h2>Куда физически падают заявки</h2>
  <p>Главный вопрос 152-ФЗ — не текст на странице, а место, куда попадает заявка. Персональные данные россиян должны <strong>первично записываться в базы на территории России</strong>. Форма может выглядеть безупречно, но если заявка первым делом уходит в чужую страну, нарушение уже произошло.</p>
  <p><strong>Не годятся основным приёмником:</strong> Google-таблицы и Google Формы, Zapier, Airtable, Notion, зарубежные почтовые и CRM-сервисы. Сюда же попадают конструкторы, которые сохраняют заявки на серверах за рубежом.</p>
  <p><strong>Годятся:</strong> почта на российском домене у российского провайдера, amoCRM, Битрикс24, собственная база на российском хостинге.</p>
  <p><strong>Telegram — только дублирующим уведомлением.</strong> Сообщение администратору «пришла заявка» удобно и допустимо, но первичной записью считается то, что легло в российскую базу. Telegram основным хранилищем заявок быть не может.</p>
  <p>На этом демонстрационном сайте форма не отправляет ничего и никуда: показывать защиту персональных данных, попутно собирая их с посетителей, было бы странно.</p>
</section>
```

- [ ] **Step 4: Дописать стиль**

Добавить в `content/style.css` перед блоком `@media print`:

```css
.razbor{
  margin-top:36px;padding:22px 20px;
  border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;
}
.razbor h2{margin-top:0}
.razbor p{margin:0 0 12px}
.razbor p:last-child{margin-bottom:0}
```

- [ ] **Step 5: Собрать, прогнать тесты и проверку**

Запустить: `npm run build && npm test && npm run check`
Ожидается: всё PASS.

- [ ] **Step 6: Коммит**

```bash
git add content/pages/zapis.html content/style.css tools/test_build.py index.html assets
git commit -m "Разборы на странице записи: почему нет лишних полей и куда падают заявки"
```

---

### Task 6: Тексты трёх документов

Тексты берутся из готового комплекта `~/Progects/tilda-yuridicheskie-dokumenty` и адаптируются под запись на приём в клинику. Из файла согласия на страницу идёт только вторая половина: первая — инструкция исполнителю, и однажды она чуть не уехала клиенту целиком.

**Files:**
- Modify: `content/pages/politika.html`, `content/pages/soglasie.html`, `content/pages/soglashenie.html`
- Test: `tools/test_build.py` (класс `ТестТекстов`)

**Interfaces:**
- Consumes: шаблон и плейсхолдеры из задач 1 и 3. В текстах используются `{{ОПЕРАТОР}}`, `{{ОПЕРАТОР_КРАТКО}}`, `{{ИНН}}`, `{{ОГРН}}`, `{{АДРЕС}}`, `{{EMAIL}}`, `{{ТЕЛЕФОН}}`, `{{САЙТ}}`, `{{ДАТА}}`, `{{ССЫЛКА_ПОЛИТИКА}}`, `{{ССЫЛКА_СОГЛАСИЕ}}`, `{{ССЫЛКА_СОГЛАШЕНИЕ}}`.
- Produces: готовые тексты документов; дальше их только проверяют.

- [ ] **Step 1: Написать падающий тест**

Дописать в `tools/test_build.py`:

```python
class ТестТекстов(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.build_all(КОРЕНЬ)
        cls.тексты = {}
        for имя in ("privacy.html", "consent.html", "terms.html"):
            with open(os.path.join(КОРЕНЬ, имя), encoding="utf-8") as ф:
                cls.тексты[имя] = ф.read()

    def test_политика_содержит_обязательные_разделы(self):
        текст = self.тексты["privacy.html"]
        for раздел in ("Сведения об Операторе", "Какие данные обрабатываются", "Цели обработки",
                       "Правовые основания", "Права Пользователя", "cookie"):
            self.assertIn(раздел, текст, "в политике нет раздела «%s»" % раздел)

    def test_политика_называет_место_хранения(self):
        self.assertIn("территории Российской Федерации", self.тексты["privacy.html"])

    def test_согласие_без_инструкции_исполнителю(self):
        текст = self.тексты["consent.html"]
        for мусор in ("Текст рядом с галочкой", "Где включить в Тильде", "Если появится рассылка",
                      "Тильд", "плейсхолдер"):
            self.assertNotIn(мусор, текст, "в согласие уехала инструкция: «%s»" % мусор)

    def test_согласие_содержит_обязательные_разделы(self):
        текст = self.тексты["consent.html"]
        for раздел in ("Состав персональных данных", "Цели обработки", "Срок действия согласия",
                       "Порядок отзыва согласия"):
            self.assertIn(раздел, текст, "в согласии нет раздела «%s»" % раздел)

    def test_политика_прямо_говорит_что_здоровье_не_собирается(self):
        текст = self.тексты["privacy.html"]
        self.assertIn("состоянии здоровья", текст)
        self.assertIn("не собираются", текст)

    def test_состав_данных_совпадает_с_формой(self):
        for имя in ("privacy.html", "consent.html"):
            текст = self.тексты[имя]
            for поле in ("имя", "телефон", "удобное время"):
                self.assertIn(поле, текст.lower(), "%s не перечисляет поле «%s»" % (имя, поле))

    def test_нет_согласия_на_медицинское_вмешательство(self):
        for имя, текст in self.тексты.items():
            self.assertNotIn("медицинское вмешательство", текст, имя)

    def test_соглашение_описывает_услугу_записи(self):
        self.assertIn("запис", self.тексты["terms.html"].lower())
```

- [ ] **Step 2: Запустить тест и убедиться, что он падает**

Запустить: `npm test`
Ожидается: FAIL — в файлах пока только заголовки-заглушки.

- [ ] **Step 3: Посмотреть исходные тексты**

```bash
ИСХ=~/Progects/tilda-yuridicheskie-dokumenty
sed -n '1,120p' "$ИСХ/01-политика.md"
```

Читать целиком, не по диагонали: дальше он переписывается под клинику, а не копируется.

- [ ] **Step 4: Перенести политику**

Записать `content/pages/politika.html`: перенести текст `01-политика.md` в HTML (`##` → `<h2>`, списки → `<ul><li>`), подставив плейсхолдеры вместо реквизитов. Адаптация под клинику:

- в разделе «Какие данные обрабатываются» перечислить ровно то, что собирает форма: имя, телефон, вид приёма, удобное время — и добавить абзац: «Сведения о состоянии здоровья через сайт не собираются. Форма записи не содержит полей о жалобах, симптомах и диагнозах.»;
- в целях обработки — «запись на приём и обратная связь с посетителем сайта», без маркетинга и рассылок, которых на сайте нет;
- в разделе о порядке обработки прямо написать: «Персональные данные, полученные через сайт, первично записываются и хранятся в базах данных, расположенных на территории Российской Федерации.» — тест ждёт именно эту формулировку;
- раздел про cookie оставить, он отвечает баннеру из задачи 3;
- шапка документа: «Действует с {{ДАТА}}» и «Оператор: {{ОПЕРАТОР}}, ИНН {{ИНН}}, ОГРН {{ОГРН}}, адрес {{АДРЕС}}».

Файл начинается с `<h1>Политика обработки персональных данных</h1>` — шаблон свой заголовок не добавляет.

- [ ] **Step 5: Перенести согласие — только вторую половину файла**

Посмотреть ровно тот кусок, который идёт на страницу:

```bash
sed -n '/^## Полный текст согласия/,/^## Если появится рассылка/p' \
  ~/Progects/tilda-yuridicheskie-dokumenty/02-согласие.md
```

Записать `content/pages/soglasie.html` из этого куска и **только из него**. Всё, что выше строки `## Полный текст согласия (отдельная страница)`, — инструкция для исполнителя и текст галочки; ниже `## Если появится рассылка` — заготовка на будущее. Ни то ни другое на страницу не идёт.

Адаптация: в составе данных перечислить имя, телефон, вид приёма и удобное время; в целях — запись на приём и подтверждение времени; в отзыве согласия указать `{{EMAIL}}` и `{{АДРЕС}}`. Начать файл с `<h1>Согласие на обработку персональных данных</h1>`.

- [ ] **Step 6: Перенести пользовательское соглашение**

Записать `content/pages/soglashenie.html` из `03-пользовательское-соглашение.md`. Предмет соглашения — услуга записи на приём через сайт: сайт передаёт заявку в клинику, время подтверждает администратор звонком, запись не является заключением договора об оказании медицинских услуг. Раздел «Обращение через форму обратной связи» переименовать в «Запись на приём через сайт». Начать с `<h1>Пользовательское соглашение</h1>`.

- [ ] **Step 7: Собрать и прогнать тесты**

Запустить: `npm run build && npm test`
Ожидается: все тесты PASS, в том числе `test_согласие_без_инструкции_исполнителю`.

- [ ] **Step 8: Прочитать собранные страницы глазами**

Запустить: `open privacy.html consent.html terms.html`
Проверить: нет обрывков markdown (`##`, `**`), нет `{{`, реквизиты на месте, текст говорит про клинику и запись, а не про интернет-магазин.

- [ ] **Step 9: Коммит**

```bash
git add content/pages tools/test_build.py privacy.html consent.html terms.html
git commit -m "Тексты политики, согласия и пользовательского соглашения под запись на приём"
```

---

### Task 7: Полная автопроверка и скриншоты

Всё, что спека требует проверить: контраст, прокрутка на 360 px, чистая консоль, ссылки на документы с каждой страницы, печать в PDF.

**Files:**
- Modify: `tools/check.mjs`
- Create: `tools/shot.mjs`
- Create: `tools/shots/` (скриншоты, в репозиторий попадают)

**Interfaces:**
- Consumes: все собранные страницы; функции проверки контраста и прокрутки переносятся из `~/Progects/skuf-tur/tools/check.mjs`.
- Produces: `npm run check` — зелёный прогон по всем четырём страницам; `npm run shot` — скриншоты в `tools/shots/`.

- [ ] **Step 1: Расширить проверку на все четыре страницы**

В `tools/check.mjs` заменить блок `try { ... }` на цикл по страницам, оставив проверки формы для `index.html`. Добавить перед `finally`:

```javascript
  const СТРАНИЦЫ = ['index.html', 'privacy.html', 'consent.html', 'terms.html'];
  for (const файл of СТРАНИЦЫ) {
    const стр = await browser.newPage({ viewport: { width: 360, height: 800 } });
    const шум = [];
    стр.on('console', м => { if (м.type() === 'error' || м.type() === 'warning') шум.push(м.text()); });
    стр.on('pageerror', е => шум.push(String(е)));
    await стр.goto(АДРЕС + файл, { waitUntil: 'load' });
    await стр.evaluate(() => document.fonts.ready);

    // Горизонтальная прокрутка на 360 px
    const перелив = await стр.evaluate(() => {
      const d = document.documentElement;
      if (d.scrollWidth <= d.clientWidth) return null;
      const виноваты = [...document.querySelectorAll('*')]
        .filter(э => э.getBoundingClientRect().right > d.clientWidth + 1)
        .slice(0, 5)
        .map(э => э.tagName.toLowerCase() + (typeof э.className === 'string' && э.className ? '.' + э.className.split(' ')[0] : ''));
      return { w: d.scrollWidth, c: d.clientWidth, виноваты };
    });
    if (перелив) провалы.push(`${файл}: горизонтальная прокрутка ${перелив.w}>${перелив.c}, виноваты: ${перелив.виноваты.join(', ')}`);

    // Контраст по WCAG: 4.5 для обычного текста, 3.0 для крупного
    const слабые = await стр.evaluate(() => {
      const яркость = ([r, g, b]) => {
        const f = v => { v /= 255; return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4); };
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
      };
      const rgb = s => (s.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
      const фон = э => {
        for (let n = э; n; n = n.parentElement) {
          const c = getComputedStyle(n).backgroundColor;
          const части = c.match(/[\d.]+/g) || [];
          if (c && c !== 'transparent' && части[3] !== '0') return rgb(c);
        }
        return [255, 255, 255];
      };
      const плохие = [];
      for (const э of document.querySelectorAll('body *')) {
        if (э.closest('[hidden]')) continue;
        const текст = [...э.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join('');
        if (!текст) continue;
        const cs = getComputedStyle(э);
        if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
        const размер = parseFloat(cs.fontSize);
        const вес = parseInt(cs.fontWeight, 10) || 400;
        const норма = (размер >= 24 || (размер >= 18.66 && вес >= 700)) ? 3 : 4.5;
        const l1 = яркость(rgb(cs.color)), l2 = яркость(фон(э));
        const отношение = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        if (отношение < норма) плохие.push(`«${текст.slice(0, 34)}…» — ${отношение.toFixed(2)} при норме ${норма}`);
      }
      return плохие;
    });
    if (слабые.length) провалы.push(`${файл}: контраст ниже нормы:\n    ` + слабые.join('\n    '));

    // Ссылки на все документы работают с каждой страницы
    for (const адрес of ['index.html', 'privacy.html', 'consent.html', 'terms.html']) {
      const есть = await стр.locator(`a[href="${адрес}"]`).count();
      if (!есть) провалы.push(`${файл}: нет ссылки на ${адрес}`);
      else {
        const ответ = await стр.request.get(АДРЕС + адрес);
        if (!ответ.ok()) провалы.push(`${файл}: ссылка на ${адрес} отдаёт ${ответ.status()}`);
      }
    }

    // Документы читаемо печатаются: в режиме печати виден текст, скрыт интерфейс
    await стр.emulateMedia({ media: 'print' });
    const печать = await стр.evaluate(() => ({
      шапка: !!document.querySelector('.shapka') && getComputedStyle(document.querySelector('.shapka')).display !== 'none',
      текст: document.querySelector('.stranica').innerText.trim().length,
    }));
    if (печать.шапка) провалы.push(`${файл}: при печати не скрыта шапка`);
    if (печать.текст < 400 && файл !== 'index.html') провалы.push(`${файл}: при печати почти нет текста (${печать.текст} знаков)`);
    await стр.emulateMedia({ media: 'screen' });

    if (шум.length) провалы.push(`${файл}: сообщения в консоли: ${шум.join(' | ')}`);
    await стр.close();
  }
```

И поправить итоговую строку успеха:

```javascript
console.log('Проверка пройдена: галочка блокирует отправку, лишних полей нет, контраст и прокрутка в норме, ссылки живые, консоль чистая.');
```

- [ ] **Step 2: Запустить проверку и починить найденное**

Запустить: `npm run check`
Если что-то падает — править `content/style.css` или разметку, пересобирать `npm run build` и запускать снова, пока не станет зелено. Контраст чинится подбором цвета в `:root`, а не отключением проверки.

- [ ] **Step 3: Написать скрипт скриншотов**

Создать `tools/shot.mjs`:

```javascript
// Скриншоты для показа. Запуск: npm run shot
import { chromium } from 'playwright';
import { spawn } from 'node:child_process';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mkdirSync } from 'node:fs';

const КОРЕНЬ = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const ПАПКА = resolve(КОРЕНЬ, 'tools/shots');
mkdirSync(ПАПКА, { recursive: true });

const ПОРТ = 8766;
const АДРЕС = `http://127.0.0.1:${ПОРТ}/`;
const сервер = spawn('python3', ['-m', 'http.server', String(ПОРТ), '--bind', '127.0.0.1'],
  { cwd: КОРЕНЬ, stdio: 'ignore' });
await new Promise(р => setTimeout(р, 700));

const browser = await chromium.launch();
for (const ширина of [1280, 360]) {
  for (const файл of ['index.html', 'privacy.html', 'consent.html', 'terms.html']) {
    const стр = await browser.newPage({ viewport: { width: ширина, height: 900 } });
    await стр.goto(АДРЕС + файл, { waitUntil: 'load' });
    await стр.evaluate(() => document.fonts.ready);
    const имя = файл.replace('.html', '');
    await стр.screenshot({ path: `${ПАПКА}/${имя}-${ширина}.png`, fullPage: файл !== 'index.html' });
    await стр.close();
  }
}
// Отдельно: сообщение о демонстрации после отправки с галочкой.
const стр = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await стр.goto(АДРЕС + 'index.html', { waitUntil: 'load' });
await стр.fill('#imya', 'Иван Петров');
await стр.fill('#telefon', '+7 900 000-00-00');
await стр.selectOption('#usluga', { index: 1 });
await стр.check('#soglasie');
await стр.click('#otpravit');
await стр.locator('#itog').scrollIntoViewIfNeeded();
await стр.screenshot({ path: `${ПАПКА}/forma-otpravlena-1280.png` });
await стр.close();

await browser.close();
сервер.kill();
console.log('Скриншоты в tools/shots');
```

- [ ] **Step 4: Снять скриншоты и посмотреть их**

Запустить: `npm run shot && open tools/shots`
Ожидается: девять картинок, на мобильных ничего не уезжает за экран, сообщение о демонстрации видно.

- [ ] **Step 5: Показать результат заказчику работы**

Отправить скриншоты страницы записи (1280 и 360) и сообщения после отправки. Дождаться правок. Правки вносить в `content/`, после каждой — `npm run build && npm test && npm run check`.

- [ ] **Step 6: Коммит**

```bash
git add tools/check.mjs tools/shot.mjs tools/shots content assets index.html privacy.html consent.html terms.html
git commit -m "Полная автопроверка: контраст, прокрутка, ссылки, печать, консоль. Скриншоты"
```

---

### Task 8: Материалы для клиники и выкладка на GitHub Pages

Работа заканчивается не вёрсткой, а двумя вещами: инструкцией владельцу о том, что он обязан сделать сам, и живым адресом, по которому галочку можно нажать.

**Files:**
- Create: `docs/что-делает-владелец-сайта.md`
- Modify: `README.md`
- Modify: `~/Obsidian/Brain/index.md`, `~/Obsidian/Brain/decisions.md`

**Interfaces:**
- Consumes: готовый собранный сайт из задач 1–7.
- Produces: живой адрес `https://pyhphhddb8-eng.github.io/klinika-152fz/`.

- [ ] **Step 1: Написать инструкцию владельцу**

Создать `docs/что-делает-владелец-сайта.md` — то, что исполнитель сделать за клиента не может и не должен:

- **Уведомление в Роскомнадзор** подаёт сам оператор из своей учётной записи на портале ведомства. Исполнитель не заходит в чужой кабинет. В инструкции: что уведомление подаётся до начала обработки, какие сведения из политики в него переносятся (цели, категории данных, место хранения), и что состав данных в уведомлении должен совпадать с политикой на сайте.
- **Куда подключить приём заявок**: почта на российском домене, amoCRM или Битрикс24; Telegram — только дублирующим уведомлением. Повторить коротко, со ссылкой на блок на странице записи.
- **Реквизиты в подвале** заменить на настоящие и сверить с выпиской ЕГРЮЛ на `egrul.nalog.ru`.
- **Что проверить после подключения формы**: тестовая заявка дошла; без галочки форма не отправляется; галочка при загрузке пустая; ссылки из галочки открываются.
- **Что смотрит юрист клиники**: всё, что касается медицинской деятельности, лицензии и работы с данными пациентов в самой клинике. Комплект типовой, а не индивидуальный.

- [ ] **Step 2: Обновить README**

Заменить раздел «Состояние на 14.09.2026» на текущее: что собрано, чем собирается (`npm run build`), чем проверяется (`npm test`, `npm run check`), где живой адрес. Добавить строку про то, что реквизиты правятся только в `content/site.json`.

- [ ] **Step 3: Создать репозиторий и залить**

```bash
gh repo create pyhphhddb8-eng/klinika-152fz --public --source=. --remote=origin --push
```

Если репозиторий уже существует — `git remote add origin https://github.com/pyhphhddb8-eng/klinika-152fz.git && git push -u origin main`.

- [ ] **Step 4: Включить GitHub Pages**

```bash
gh api -X POST repos/pyhphhddb8-eng/klinika-152fz/pages \
  -f 'source[branch]=main' -f 'source[path]=/' 2>&1 | head -5
```

Подождать минуту и проверить состояние: `gh api repos/pyhphhddb8-eng/klinika-152fz/pages --jq '.status, .html_url'`
Ожидается: `built` и адрес `https://pyhphhddb8-eng.github.io/klinika-152fz/`.

- [ ] **Step 5: Проверить живой адрес запросами**

```bash
АДРЕС=https://pyhphhddb8-eng.github.io/klinika-152fz
for с in "" privacy.html consent.html terms.html robots.txt; do
  printf '%s %s\n' "$(curl -s -o /dev/null -w '%{http_code}' "$АДРЕС/$с")" "$АДРЕС/$с"
done
curl -s "$АДРЕС/" | grep -c 'noindex, nofollow'
```

Ожидается: пять строк с кодом `200` и `1` в последней строке.

- [ ] **Step 6: Прогнать проверку по живому адресу**

Запустить: `node tools/check.mjs https://pyhphhddb8-eng.github.io/klinika-152fz/`

Для этого в `tools/check.mjs` добавить в начало: если `process.argv[2]` начинается с `http`, использовать его как `АДРЕС` и не поднимать локальный сервер.

Ожидается: проверка пройдена, консоль на живом адресе чистая.

- [ ] **Step 7: Коммит и обновление журнала**

```bash
git add README.md docs tools/check.mjs
git commit -m "Инструкция владельцу сайта, README и выкладка на GitHub Pages"
git push
```

Затем дописать в `~/Obsidian/Brain/index.md`: что сделано, живой адрес, дата. В `~/Obsidian/Brain/decisions.md` — два решения, которые стоит помнить: форма клиники не собирает данные о здоровье (специальная категория), и информированное согласие по 323-ФЗ в комплект для сайта не входит.
