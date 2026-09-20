// Скриншоты для показа. Запуск: npm run shot
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { mkdirSync } from "node:fs";

const КОРЕНЬ = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ПАПКА = resolve(КОРЕНЬ, "tools/shots");
mkdirSync(ПАПКА, { recursive: true });

const ПОРТ = 8766;
const АДРЕС = `http://127.0.0.1:${ПОРТ}/`;
const сервер = spawn(
  "python3",
  ["-m", "http.server", String(ПОРТ), "--bind", "127.0.0.1"],
  { cwd: КОРЕНЬ, stdio: "ignore" },
);
await new Promise((р) => setTimeout(р, 700));

const browser = await chromium.launch();
for (const ширина of [1280, 360]) {
  for (const файл of [
    "index.html",
    "privacy.html",
    "consent.html",
    "terms.html",
  ]) {
    const стр = await browser.newPage({
      viewport: { width: ширина, height: 900 },
    });
    await стр.goto(АДРЕС + файл, { waitUntil: "load" });
    await стр.evaluate(() => document.fonts.ready);
    const имя = файл.replace(".html", "");
    await стр.screenshot({
      path: `${ПАПКА}/${имя}-${ширина}.png`,
      fullPage: файл !== "index.html",
    });
    await стр.close();
  }
}
// Отдельно: сообщение о демонстрации после отправки с галочкой.
const стр = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await стр.goto(АДРЕС + "index.html", { waitUntil: "load" });
await стр.fill("#imya", "Иван Петров");
await стр.fill("#telefon", "+7 900 000-00-00");
await стр.selectOption("#usluga", { index: 1 });
await стр.check("#soglasie");
await стр.click("#otpravit");
await стр.locator("#itog").scrollIntoViewIfNeeded();
await стр.screenshot({ path: `${ПАПКА}/forma-otpravlena-1280.png` });
await стр.close();

await browser.close();
сервер.kill();
console.log("Скриншоты в tools/shots");
