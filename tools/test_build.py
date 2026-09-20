# Тесты сборщика. Запуск: python3 tools/test_build.py -v
import os
import shutil
import sys
import tempfile
import unittest

КОРЕНЬ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, КОРЕНЬ)
import build

# Файлы, которые создаёт сборщик и которые лежат в репозитории: именно они
# публикуются как сайт.
СОБРАННЫЕ = (
    "index.html",
    "privacy.html",
    "consent.html",
    "terms.html",
    "assets/style.css",
    "assets/fonts.css",
)


def _байты(путь):
    with open(путь, "rb") as ф:
        return ф.read()


def _первое_отличие(в_репозитории, из_сборки):
    """Первая разошедшаяся строка: сравнение побайтное, но читать удобнее так."""
    а = в_репозитории.decode("utf-8", "replace").splitlines()
    б = из_сборки.decode("utf-8", "replace").splitlines()
    for номер, (строка_а, строка_б) in enumerate(zip(а, б), 1):
        if строка_а != строка_б:
            return (
                "строка %d\n"
                "      в репозитории: %s\n"
                "      после сборки:  %s"
                % (номер, строка_а.strip()[:110], строка_б.strip()[:110])
            )
    return "разная длина: в репозитории %d строк, после сборки %d" % (len(а), len(б))


# Снимок делаем при импорте модуля, до первого теста: остальные классы
# вызывают build_all(КОРЕНЬ) и перезаписывают корень, после чего устаревание
# закоммиченных файлов увидеть уже невозможно.
СНИМОК = {имя: _байты(os.path.join(КОРЕНЬ, *имя.split("/"))) for имя in СОБРАННЫЕ}


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
            self.assertNotIn("https://", текст, имя)
        self.assertNotIn("http", self.css.replace("data:font", ""))

    def test_шрифт_не_раздут(self):
        размер = os.path.getsize(os.path.join(КОРЕНЬ, "assets", "fonts", "golos-text.woff2"))
        self.assertLess(размер, 120 * 1024, "подрезка не сработала, шрифт %d байт" % размер)


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
        # Регистр не учитываем: «СНИЛС», name="snils" и подпись «Снилс» — одно и то же.
        # Список слов держим таким же, как в tools/check.mjs.
        куски = self.текст.split("<form")[1].split("</form>")[0].lower()
        for слово in ("жалоб", "симптом", "диагноз", "болезн", "рожден", "паспорт", "снилс", "полис"):
            self.assertNotIn(слово, куски, "в форме встретилось «%s»" % слово)


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
        # Слайсим текст на две части по маркерам
        негодные = self.текст.split("Не годятся основным приёмником:", 1)[1].split("<strong>Годятся:</strong>", 1)[0]
        годные = self.текст.split("<strong>Годятся:</strong>", 1)[1].split("Telegram", 1)[0]

        for сервис in ("Google", "Zapier", "Airtable"):
            self.assertIn(сервис, негодные, сервис + " должен быть в списке негодных приёмников")
            self.assertNotIn(сервис, годные, сервис + " не должен быть в списке годных приёмников")

    def test_названы_годные_приёмники(self):
        # Слайсим текст на две части по маркерам
        негодные = self.текст.split("Не годятся основным приёмником:", 1)[1].split("<strong>Годятся:</strong>", 1)[0]
        годные = self.текст.split("<strong>Годятся:</strong>", 1)[1].split("Telegram", 1)[0]

        for сервис in ("amoCRM", "Битрикс24"):
            self.assertIn(сервис, годные, сервис + " должен быть в списке годных приёмников")
            self.assertNotIn(сервис, негодные, сервис + " не должен быть в списке негодных приёмников")

    def test_telegram_только_дублирующим(self):
        self.assertIn("Telegram", self.текст)
        self.assertIn("только дублирующим уведомлением", self.текст, "Telegram должен быть только дублирующим уведомлением")
        # Проверяем, что Telegram не может быть основным хранилищем (фраза может быть расколота на строки HTML)
        self.assertIn("Telegram основным хранилищем", self.текст, "должно быть сказано, что Telegram основным хранилищем")
        self.assertIn("заявок быть не может", self.текст, "должно быть сказано, что заявок быть не может")


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
            for поле in ("имя", "телефон", "вид приёма", "удобное время"):
                self.assertIn(поле, текст.lower(), "%s не перечисляет поле «%s»" % (имя, поле))

    def test_нет_согласия_на_медицинское_вмешательство(self):
        for имя, текст in self.тексты.items():
            self.assertNotIn("медицинское вмешательство", текст, имя)

    def test_соглашение_описывает_услугу_записи(self):
        self.assertIn("запис", self.тексты["terms.html"].lower())


class ТестСобранноеНеУстарело(unittest.TestCase):
    """Публикуется собранный файл из корня, а не content/. Если его забыли
    пересобрать после правки исходников, сайт уедет со старым текстом —
    остальные тесты этого не заметят, потому что сами пересобирают корень."""

    @classmethod
    def setUpClass(cls):
        cls.врем = tempfile.mkdtemp(prefix="klinika-sborka-")
        shutil.copytree(
            os.path.join(КОРЕНЬ, "content"), os.path.join(cls.врем, "content")
        )
        # Сборщик вшивает шрифт из assets/fonts — кладём его рядом.
        shutil.copytree(
            os.path.join(КОРЕНЬ, "assets", "fonts"),
            os.path.join(cls.врем, "assets", "fonts"),
        )
        build.build_all(cls.врем)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.врем, ignore_errors=True)

    def test_закоммиченные_файлы_совпадают_со_сборкой(self):
        for имя in СОБРАННЫЕ:
            свежий = _байты(os.path.join(self.врем, *имя.split("/")))
            if СНИМОК[имя] == свежий:
                continue
            self.fail(
                "%s разошёлся с исходниками в content/: %s\n"
                "    Выполните «npm run build» и закоммитьте пересобранные файлы."
                % (имя, _первое_отличие(СНИМОК[имя], свежий))
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
