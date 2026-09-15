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
            self.assertNotIn("https://fonts.", текст, имя)
        self.assertNotIn("http", self.css.replace("data:font", ""))

    def test_шрифт_не_раздут(self):
        размер = os.path.getsize(os.path.join(КОРЕНЬ, "assets", "fonts", "golos-text.woff2"))
        self.assertLess(размер, 120 * 1024, "подрезка не сработала, шрифт %d байт" % размер)


if __name__ == "__main__":
    unittest.main(verbosity=2)
