// Bấm thử bản xem trước bằng Chrome headless (một tiến trình, tự mở tự đóng) và chụp ảnh.
// Dùng: node docs/mockup/_tools/bam-thu.mjs danh-muc [thư-mục-ảnh]   luồng Quản lý → 6 danh mục → form → Lưu/✕
//       node docs/mockup/_tools/bam-thu.mjs quet                       quét mọi nút: đếm riêng data-act / go / pick, in danh sách còn hint
// Chỉ cần Node 22+ (fetch, WebSocket có sẵn) và Chrome hoặc Edge đã cài. Đặt PROTEAM_BROWSER để chọn trình duyệt khác.
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TOOLS = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(TOOLS, "..");
const PAGE = process.env.PROTEAM_PAGE ?? "file:///" + path.join(ROOT, "de-xuat", "ban-xem-truoc.html").split(path.sep).join("/"); // PROTEAM_PAGE: URL trang khác (thử nghiệm)
const CANDS = [process.env.PROTEAM_BROWSER,
  "C:/Program Files/Google/Chrome/Application/chrome.exe",
  "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
  "C:/Program Files/Microsoft/Edge/Application/msedge.exe"].filter(Boolean);
const exe = CANDS.find((p) => fs.existsSync(p)) ?? (console.error("không thấy Chrome/Edge"), process.exit(1));
const port = 9300 + Math.floor(Math.random() * 500);
const prof = fs.mkdtempSync(path.join(os.tmpdir(), "bam-thu-"));
const proc = spawn(exe, ["--headless=new", `--remote-debugging-port=${port}`, `--user-data-dir=${prof}`, "--window-size=1440,900",
  "--hide-scrollbars", "--no-first-run", "--allow-file-access-from-files", "about:blank"], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const done = (code) => { try { proc.kill(); } catch {} setTimeout(() => { try { fs.rmSync(prof, { recursive: true, force: true }); } catch {} process.exit(code); }, 400); };

async function connect() {
  for (let i = 0; i < 60; i++) {
    try {
      const l = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
      const t = l.find((x) => x.type === "page");
      if (t) return t.webSocketDebuggerUrl;
    } catch {}
    await sleep(250);
  }
  throw new Error("không nối được trình duyệt");
}
const ws = new WebSocket(await connect());
await new Promise((r) => (ws.onopen = r));
let id = 0; const wait = new Map();
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && wait.has(d.id)) { wait.get(d.id)(d); wait.delete(d.id); } };
const send = (method, params = {}) => new Promise((r) => { const i = ++id; wait.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); });
const ev = async (js) => {
  const r = await send("Runtime.evaluate", { expression: js, returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails.exception?.description ?? r.result.exceptionDetails));
  return r.result?.result?.value;
};
const shot = async (file) => {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const r = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(file, Buffer.from(r.result.data, "base64"));
  console.log("  ảnh", path.relative(process.cwd(), file));
};
await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
const open = async (key) => { await send("Page.navigate", { url: PAGE + "#" + key }); await sleep(900); };
const hash = () => ev("location.hash.slice(1)");
const hintText = () => ev("document.getElementById('hint').classList.contains('show') ? document.getElementById('hint').textContent : ''");
// bấm phần tử trong khung: theo chữ (a/button) hoặc selector
const click = (sel, text = "") => ev(`(() => { const d = document.querySelector('iframe').contentDocument;
  const els = [...d.querySelectorAll(${JSON.stringify(sel)})].filter(e => !${JSON.stringify(text)} || e.textContent.replace(/\\s+/g,' ').includes(${JSON.stringify(text)}));
  if (!els.length) return false; els[0].click(); return true; })()`);

// Bấm thử tay 7 nút ở bản xem trước, chụp ảnh tai-cho-*.png. Dùng: node docs/mockup/ux/tai-cho.mjs
const OUT = path.join(ROOT, "ux", "anh");
const D = (js) => ev(`(() => { const d = document.querySelector('iframe').contentDocument; return (${js})(d); })()`);
const ok = (t, c) => console.log(c ? "  ✔" : "  ✘", t);
let bad = 0; const chk = (t, c) => { ok(t, c); if (!c) bad++; };
const fixY = () => ev(`document.querySelector('iframe').contentWindow.scrollTo(0, 0)`);

console.log("04 «+ Thêm dòng»");
await open("receipt-2");
const n0 = await D((d) => d.querySelector("[data-rows]").children.length);
await shot(path.join(OUT, "tai-cho-04-truoc.png"));
await click("button", "+ Thêm dòng"); await sleep(300);
const n1 = await D((d) => d.querySelector("[data-rows]").children.length);
chk(`số dòng ${n0} → ${n1}`, n1 === n0 + 1);
chk("không hint", (await hintText()) === "");
await shot(path.join(OUT, "tai-cho-04-sau.png"));

console.log("16 «Bỏ dòng này»");
await open("prod-order");
const ing = () => D((d) => d.querySelectorAll(".ing").length); const i0 = await ing(); const c0 = await D((d) => [...d.querySelectorAll("button")].filter((b) => b.textContent.includes("Bỏ dòng này")).length);
await shot(path.join(OUT, "tai-cho-16-truoc.png"));
await click("button", "Bỏ dòng này"); await sleep(300);
const c1 = await D((d) => [...d.querySelectorAll("button")].filter((b) => b.textContent.includes("Bỏ dòng này")).length);
chk(`số nút «Bỏ dòng này» ${c0} → ${c1}; .ing ${i0} → ${await ing()}`, c1 === c0 - 1);
chk("không hint", (await hintText()) === "");
await shot(path.join(OUT, "tai-cho-16-sau.png"));

console.log("45 «Ngừng dùng»");
await open("area");
const st = () => D((d) => { const b = [...d.querySelectorAll("button")].find((x) => x.textContent.trim() === "Ngừng dùng" || x.textContent.trim() === "Dùng lại"); const tr = b.closest("tr"); return [b.textContent.trim(), (tr.querySelector("[data-status],.tag,.badge") || {}).textContent]; });
const s0 = await st();
await shot(path.join(OUT, "tai-cho-45-truoc.png"));
await click("button", "Ngừng dùng"); await sleep(300);
const s1 = await st();
chk(`dòng đầu: ${JSON.stringify(s0)} → ${JSON.stringify(s1)}`, s0[0] === "Ngừng dùng" && s1[0] === "Dùng lại" && s1[1].includes("Ngừng"));
chk("không hint", (await hintText()) === "");
await shot(path.join(OUT, "tai-cho-45-sau.png"));

console.log("20 «Lưu bảng giá»");
await open("prices");
await click("button", "Lưu bảng giá"); await sleep(250);
const t = await ev(`document.getElementById('toast').textContent + '|' + document.getElementById('toast').classList.contains('show')`);
chk(`thông báo ${t}`, t === "Đã lưu|true");
await shot(path.join(OUT, "tai-cho-20-sau.png"));

console.log("47b «Chọn ảnh»");
await open("material-edit");
await send("Page.setInterceptFileChooserDialog", { enabled: true });
let opened = false;
const prev = ws.onmessage;
ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.method === "Page.fileChooserOpened") opened = true; prev(m); };
await ev(`(() => { const d = document.querySelector('iframe').contentDocument; [...d.querySelectorAll('button')].find(b => b.textContent.includes('Chọn ảnh')).click(); })()`).catch(() => {});
await sleep(400);
if (!opened) { // click không có thao tác người dùng: thử lại có userGesture
  await send("Runtime.evaluate", { expression: `(() => { const d = document.querySelector('iframe').contentDocument; [...d.querySelectorAll('button')].find(b => b.textContent.includes('Chọn ảnh')).click(); })()`, userGesture: true });
  await sleep(400);
}
chk("hộp chọn file mở (Page.fileChooserOpened)", opened);
chk("không hint", (await hintText()) === "");
await shot(path.join(OUT, "tai-cho-47b.png"));
for (const [key, label, file] of [["products", "+ Thêm mới", "23"], ["scent-trial", "+ Đợt thử mới", "26d"]]) {
  console.log(`${file} «${label}»`);
  await open(key);
  const rows = () => D((d) => [...d.querySelectorAll("tbody,ul,ol")].reduce((a, l) => a + l.children.length, 0));
  const r0 = await rows();
  await shot(path.join(OUT, `tai-cho-${file}-truoc.png`));
  await click("button", label); await sleep(300);
  const r1 = await rows();
  chk(`số dòng ${r0} → ${r1}`, r1 === r0 + 1);
  chk("không hint", (await hintText()) === "");
  await shot(path.join(OUT, `tai-cho-${file}-sau.png`));
}
console.log(bad ? `CÓ ${bad} LỖI` : "TẤT CẢ ĐẠT");
done(bad ? 1 : 0);
