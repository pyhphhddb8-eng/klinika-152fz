// Проверки в браузере. Запуск: npm run check
// Поднимает локальный сервер, потому что localStorage не работает при открытии файла с диска.
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const КОРЕНЬ = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ПОРТ = 8765;
const АДРЕС = `http://127.0.0.1:${ПОРТ}/`;

const сервер = spawn(
  "python3",
  ["-m", "http.server", String(ПОРТ), "--bind", "127.0.0.1"],
  { cwd: КОРЕНЬ, stdio: "ignore" },
);
await new Promise((р) => setTimeout(р, 700));

const провалы = [];
const browser = await chromium.launch();

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 } });
  await page.goto(АДРЕС + "index.html", { waitUntil: "load" });

  // 1. Галочка при загрузке пустая. Предзаполненная согласием не считается.
  if (await page.isChecked("#soglasie"))
    провалы.push("Галочка согласия предзаполнена");

  // 2. Без галочки форма не отправляется.
  await page.fill("#imya", "Иван Петров");
  await page.fill("#telefon", "+7 999 000-00-00");
  await page.selectOption("#usluga", { index: 1 });
  await page.fill("#vremya", "Будни после 18:00");
  await page.click("#otpravit");
  if (await page.isVisible("#itog"))
    провалы.push("Форма отправилась без галочки согласия");
  if (!(await page.isVisible("#oshibka")))
    провалы.push("Без галочки не показано объяснение, почему не отправляется");

  // 3. С галочкой — сообщение о демонстрации.
  await page.check("#soglasie");
  await page.click("#otpravit");
  const итог = (await page.textContent("#itog")) || "";
  if (!/демонстрац/i.test(итог))
    провалы.push(
      "С галочкой не показано сообщение о демонстрации: «" + итог.trim() + "»",
    );

  // 4. Ссылка из галочки ведёт на согласие и открывается отдельной вкладкой.
  const ссылка = page.locator('.soglasie-stroka a[href="consent.html"]');
  if (!(await ссылка.count()))
    провалы.push("Рядом с галочкой нет ссылки на согласие");
  else if ((await ссылка.first().getAttribute("target")) !== "_blank")
    провалы.push("Ссылка на согласие открывается не отдельной вкладкой");

  // 5. В форме нет полей о здоровье.
  const поля = await page.$$eval(
    "#zapis input, #zapis select, #zapis textarea",
    (у) =>
      у.map((э) =>
        (
          э.id +
          " " +
          (э.name || "") +
          " " +
          (э.placeholder || "")
        ).toLowerCase(),
      ),
  );
  const запрещённые = [
    "жалоб",
    "симптом",
    "диагноз",
    "болезн",
    "рожден",
    "паспорт",
    "полис",
    "снилс",
  ];
  for (const поле of поля)
    for (const слово of запрещённые)
      if (поле.includes(слово))
        провалы.push(`Поле о здоровье или документе в форме: «${поле.trim()}»`);
} finally {
  await browser.close();
  сервер.kill();
}

if (провалы.length) {
  console.error("ПРОВЕРКА НЕ ПРОЙДЕНА:\n- " + провалы.join("\n- "));
  process.exit(1);
}
console.log(
  "Проверка пройдена: галочка пустая и блокирует отправку, лишних полей нет.",
);
