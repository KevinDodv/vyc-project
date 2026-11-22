// Bấm thử toggle Ngừng dùng/Dùng lại 6 lần trên ban-chinh.html (màn area (Địa bàn)), kiểm màu danger theo trạng thái, chụp anh/toggle-sau.png.
// Dùng: node docs/mockup/ux/toggle.mjs
import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TOOLS = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(TOOLS, "..");
const PAGE = process.env.PROTEAM_PAGE ?? "file:///" + path.join(ROOT, "ban-chinh.html").split(path.sep).join("/"); // PROTEAM_PAGE: URL trang khác (thử nghiệm)
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
await send("Page.enable"); await send("Emulation.setDeviceMetricsOverride", { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
await send("Page.navigate", { url: PAGE + "#area" });
await sleep(1500);
const q = `(()=>{const b=Array.from(document.querySelector("iframe").contentDocument.querySelectorAll("button")).find(x=>x.dataset.act==="toggle");return b?{t:b.textContent.trim(),d:b.classList.contains("danger"),s:b.dataset.state||null}:null})()`;
const click = `(()=>{const b=Array.from(document.querySelector("iframe").contentDocument.querySelectorAll("button")).find(x=>x.dataset.act==="toggle");b.click()})()`;
let ok = true; const log = [await ev(q)]; console.log("đầu", JSON.stringify(log[0]));
for (let i = 1; i <= 6; i++) { await ev(click); await sleep(150); const s = await ev(q); const want = s.t === "Ngừng dùng"; const good = s.d === want; ok = ok && good; console.log("bấm", i, JSON.stringify(s), good ? "đúng" : "SAI"); }
const shot = await send("Page.captureScreenshot", { format: "png" });
fs.writeFileSync(path.join(TOOLS, "anh", "toggle-sau.png"), Buffer.from(shot.result.data, "base64"));
console.log(ok ? "TẤT CẢ ĐẠT" : "CÓ LỖI");
done(ok ? 0 : 1);
