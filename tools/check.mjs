// Проверки в браузере. Запуск: npm run check
//
// Без аргумента проверяет локальную сборку и сам поднимает сервер: localStorage
// не работает при открытии файла с диска.
// С адресом первым аргументом проверяет уже выложенный сайт, ничего локально
// не поднимая:  node tools/check.mjs https://адрес-сайта/
import { chromium } from "playwright";
import { spawn } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const КОРЕНЬ = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const ПОРТ = 8765;
const аргумент = process.argv[2] || "";
const ЖИВОЙ = аргумент.startsWith("http");
const АДРЕС = ЖИВОЙ
  ? аргумент.endsWith("/")
    ? аргумент
    : аргумент + "/"
  : `http://127.0.0.1:${ПОРТ}/`;
// Список страниц используется и в цикле проверок, и в проверке ссылок —
// держим один источник правды.
const СТРАНИЦЫ = ["index.html", "privacy.html", "consent.html", "terms.html"];

// Свой сервер поднимаем только для локальной сборки. Для живого адреса его
// нет — и убивать в конце тоже нечего.
const сервер = ЖИВОЙ
  ? null
  : spawn(
      "python3",
      ["-m", "http.server", String(ПОРТ), "--bind", "127.0.0.1"],
      { cwd: КОРЕНЬ, stdio: "ignore" },
    );
if (!ЖИВОЙ) await new Promise((р) => setTimeout(р, 700));
console.log(
  (ЖИВОЙ ? "Проверяю выложенный сайт: " : "Проверяю локальную сборку: ") +
    АДРЕС,
);

const провалы = [];
const browser = await chromium.launch();

try {
  const page = await browser.newPage({ viewport: { width: 360, height: 800 } });
  // Консоль и ошибки страницы слушаем и здесь: именно на этом объекте
  // разыгрывается весь интерактивный сценарий (заполнение формы, клики,
  // галочка) — самый нагруженный код на сайте, и его тоже нужно проверять
  // на чистоту консоли, а не только начальную загрузку страницы.
  const шумИнтерактив = [];
  page.on("console", (м) => {
    if (м.type() === "error" || м.type() === "warning")
      шумИнтерактив.push(м.text());
  });
  page.on("pageerror", (е) => шумИнтерактив.push(String(е)));
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

  // 6. Консоль чистая и во время интерактивного сценария (клики, ввод,
  // галочка), а не только при загрузке страницы.
  if (шумИнтерактив.length)
    провалы.push(
      `index.html: сообщения в консоли во время интерактивного сценария (форма/галочка): ${шумИнтерактив.join(" | ")}`,
    );

  // 7. Расширенная проверка: контраст, прокрутка, ссылки, печать, консоль —
  // на всех четырёх страницах.
  for (const файл of СТРАНИЦЫ) {
    const стр = await browser.newPage({
      viewport: { width: 360, height: 800 },
    });
    const шум = [];
    стр.on("console", (м) => {
      if (м.type() === "error" || м.type() === "warning") шум.push(м.text());
    });
    стр.on("pageerror", (е) => шум.push(String(е)));
    await стр.goto(АДРЕС + файл, { waitUntil: "load" });
    await стр.evaluate(() => document.fonts.ready);

    // Горизонтальная прокрутка на 360 px
    const перелив = await стр.evaluate(() => {
      const d = document.documentElement;
      if (d.scrollWidth <= d.clientWidth) return null;
      const виноваты = [...document.querySelectorAll("*")]
        .filter((э) => э.getBoundingClientRect().right > d.clientWidth + 1)
        .slice(0, 5)
        .map(
          (э) =>
            э.tagName.toLowerCase() +
            (typeof э.className === "string" && э.className
              ? "." + э.className.split(" ")[0]
              : ""),
        );
      return { w: d.scrollWidth, c: d.clientWidth, виноваты };
    });
    if (перелив)
      провалы.push(
        `${файл}: горизонтальная прокрутка ${перелив.w}>${перелив.c}, виноваты: ${перелив.виноваты.join(", ")}`,
      );

    // Контраст по WCAG: 4.5 для обычного текста, 3.0 для крупного
    const слабые = await стр.evaluate(() => {
      const яркость = ([r, g, b]) => {
        const f = (v) => {
          v /= 255;
          return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
        };
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b);
      };
      const rgb = (s) =>
        (s.match(/[\d.]+/g) || [0, 0, 0]).slice(0, 3).map(Number);
      const фон = (э) => {
        for (let n = э; n; n = n.parentElement) {
          const c = getComputedStyle(n).backgroundColor;
          const части = c.match(/[\d.]+/g) || [];
          if (c && c !== "transparent" && части[3] !== "0") return rgb(c);
        }
        return [255, 255, 255];
      };
      const плохие = [];
      for (const э of document.querySelectorAll("body *")) {
        if (э.closest("[hidden]")) continue;
        const текст = [...э.childNodes]
          .filter((n) => n.nodeType === 3)
          .map((n) => n.textContent.trim())
          .join("");
        if (!текст) continue;
        const cs = getComputedStyle(э);
        if (
          cs.visibility === "hidden" ||
          cs.display === "none" ||
          +cs.opacity === 0
        )
          continue;
        const размер = parseFloat(cs.fontSize);
        const вес = parseInt(cs.fontWeight, 10) || 400;
        const норма = размер >= 24 || (размер >= 18.66 && вес >= 700) ? 3 : 4.5;
        const l1 = яркость(rgb(cs.color)),
          l2 = яркость(фон(э));
        const отношение = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
        if (отношение < норма)
          плохие.push(
            `«${текст.slice(0, 34)}…» — ${отношение.toFixed(2)} при норме ${норма}`,
          );
      }
      return плохие;
    });
    if (слабые.length)
      провалы.push(
        `${файл}: контраст ниже нормы:\n    ` + слабые.join("\n    "),
      );

    // Ссылки на все документы работают с каждой страницы
    for (const адрес of СТРАНИЦЫ) {
      const есть = await стр.locator(`a[href="${адрес}"]`).count();
      if (!есть) провалы.push(`${файл}: нет ссылки на ${адрес}`);
      else {
        const ответ = await стр.request.get(АДРЕС + адрес);
        if (!ответ.ok())
          провалы.push(`${файл}: ссылка на ${адрес} отдаёт ${ответ.status()}`);
      }
    }

    // Документы читаемо печатаются: в режиме печати виден текст, скрыт интерфейс
    await стр.emulateMedia({ media: "print" });
    const печать = await стр.evaluate(() => ({
      шапка:
        !!document.querySelector(".shapka") &&
        getComputedStyle(document.querySelector(".shapka")).display !== "none",
      текст: document.querySelector(".stranica").innerText.trim().length,
    }));
    if (печать.шапка) провалы.push(`${файл}: при печати не скрыта шапка`);
    if (печать.текст < 400 && файл !== "index.html")
      провалы.push(
        `${файл}: при печати почти нет текста (${печать.текст} знаков)`,
      );
    await стр.emulateMedia({ media: "screen" });

    if (шум.length)
      провалы.push(`${файл}: сообщения в консоли: ${шум.join(" | ")}`);
    await стр.close();
  }
} finally {
  await browser.close();
  if (сервер) сервер.kill();
}

if (провалы.length) {
  console.error("ПРОВЕРКА НЕ ПРОЙДЕНА:\n- " + провалы.join("\n- "));
  process.exit(1);
}
console.log(
  "Проверка пройдена: галочка блокирует отправку, лишних полей нет, контраст и прокрутка в норме, ссылки живые, консоль чистая.",
);
