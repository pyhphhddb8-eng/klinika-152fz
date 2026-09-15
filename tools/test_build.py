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
        куски = self.текст.split("<form")[1].split("</form>")[0]
        for слово in ("жалоб", "симптом", "диагноз", "болезн", "рожден", "паспорт", "СНИЛС", "полис"):
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
        for сервис in ("Google", "Zapier", "Airtable"):
            self.assertIn(сервис, self.текст, сервис + " не упомянут")

    def test_названы_годные_приёмники(self):
        for сервис in ("amoCRM", "Битрикс24"):
            self.assertIn(сервис, self.текст, сервис + " не упомянут")

    def test_telegram_только_дублирующим(self):
        self.assertIn("Telegram", self.текст)
        кусок = self.текст.split("Telegram", 1)[1][:400]
        self.assertIn("дубл", кусок, "про Telegram не сказано, что он только дублирующий")


if __name__ == "__main__":
    unittest.main(verbosity=2)
