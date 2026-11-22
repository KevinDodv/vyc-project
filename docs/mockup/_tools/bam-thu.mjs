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

// Quét mọi nút của mọi màn trong bản xem trước. Chạy trong trang vỏ. Nút data-act đếm riêng (đạt = không hint); phần còn lại như cũ.
// (Thay cho quet-nut.js, file đó nay không dùng nữa — nằm ngoài vùng sửa của #50.)
const QUET = `(async () => {
  const w = (ms) => new Promise((r) => setTimeout(r, ms));
  const S = JSON.parse(document.getElementById("data").textContent).screens;
  const out = { act: 0, actBy: {}, go: 0, pick: 0, disabled: [], hint: [], badTarget: [], goList: [], err: [] };
  const fr = () => document.querySelector("iframe");
  const open = async (key) => { location.hash = "#" + key; await w(220); };
  const ACTS = ["row-add", "row-del", "toggle", "save", "print", "file"];
  for (const s of S) {
    await open(s.key);
    const n = fr().contentDocument.querySelectorAll("button").length;
    for (let i = 0; i < n; i++) {
      if (location.hash !== "#" + s.key) await open(s.key);
      const b = fr().contentDocument.querySelectorAll("button")[i];
      if (!b) continue;
      const txt = b.textContent.trim().replace(/\\s+/g, " ").slice(0, 40);
      const go = b.getAttribute("data-go"), pk = b.hasAttribute("data-pick"), act = b.getAttribute("data-act");
      if (b.disabled) { out.disabled.push(s.key + " | " + txt + (go ? " [go " + go + "]" : "") + (act ? " [act " + act + "]" : "")); continue; }
      document.getElementById("hint").textContent = "";
      if (act === "print") fr().contentWindow.print = () => {}; // không mở hộp in thật khi quét
      b.click();
      await w(act === "save" ? 700 : 260);
      const h = document.getElementById("hint").textContent;
      const now = location.hash.slice(1);
      if (act !== null) {
        if (!ACTS.includes(act)) out.err.push("data-act lạ? " + s.key + " | " + txt + " act=" + act);
        else if (h) out.err.push("act ra hint: " + s.key + " | " + txt + " act=" + act + " hint=" + h);
        else { out.act++; out.actBy[act] = (out.actBy[act] || 0) + 1; }
        if (now === s.key) await open(s.key === S[0].key ? S[1].key : S[0].key); // DOM trong khung đã bị đổi: buộc nạp lại màn
      } else if (go) {
        if (now !== s.key) { out.go++; out.goList.push(s.key + " | " + txt + " -> " + now); }
        else if (h) out.hint.push(s.key + " | " + txt + " | " + b.className + " (data-go về chính màn này)");
        else out.badTarget.push(s.key + " | " + txt + " go=" + go + " hint=" + h);
      } else if (pk) {
        if (b.getAttribute("aria-pressed") === "true" && !h) out.pick++; else out.err.push("pick? " + s.key + " | " + txt + " hint=" + h);
      } else if (h) out.hint.push(s.key + " | " + txt + " | " + b.className + " type=" + (b.getAttribute("type") || ""));
      else if (now !== s.key) out.err.push("nav? " + s.key + " | " + txt + " -> " + now);
    }
  }
  return out;
})()`;

const cmd = process.argv[2];
let fail = 0;
try {
  if (cmd === "danh-muc") {
    const out = path.resolve(process.argv[3] ?? path.join(ROOT, "ux", "anh"));
    const DM = [["Địa bàn", "area", "area-edit", "dia-ban"], ["Loại hàng hóa", "goods-type", "goods-type-edit", "loai-hang"],
      ["Nguyên liệu & hạng", "material", "material-edit", "nguyen-lieu"], ["Khách & kênh bán", "customer-dm", "customer-dm-edit", "khach-hang"],
      ["Chứng nhận", "cert", "cert-edit", "chung-nhan"], ["Tài khoản", "account", "account-edit", "tai-khoan"]];
    const ok = (c, m) => { console.log((c ? "  ✔ " : "  ✘ ") + m); if (!c) fail++; };
    await open("admin");
    ok(!(await ev("document.querySelector('iframe').contentDocument.body.textContent.includes('chưa vẽ riêng')")), "31-admin không còn ghi chú «chưa vẽ riêng»");
    await shot(path.join(out, "danh-muc-0-menu-quan-ly.png"));
    for (const [ten, ds, form, slug] of DM) {
      console.log(ten);
      await open("admin");
      ok(await click("a.tile", ten.replace("&", "&")), `bấm ô «${ten}» ở Menu quản lý`);
      await sleep(700);
      ok((await hash()) === ds, `ra màn danh sách (#${await hash()})`);
      ok((await hintText()) === "", "không có hint");
      await shot(path.join(out, `danh-muc-${slug}-1-ds.png`));
      // mở form bằng bấm vào một dòng (tr[data-go]) — đúng chỗ Ha báo medium #584
      ok(await click("tr[data-go]"), "bấm một dòng của bảng");
      await sleep(700);
      ok((await hash()) === form, `mở form (#${await hash()})`);
      await shot(path.join(out, `danh-muc-${slug}-2-form.png`));
      ok(await click("button", "Lưu"), "bấm Lưu");
      await sleep(700);
      ok((await hash()) === ds, `Lưu → về danh sách (#${await hash()})`);
      ok(await click("#add"), "bấm «+ Thêm»");
      await sleep(700);
      ok((await hash()) === form, `«+ Thêm» → form (#${await hash()})`);
      ok(await click("button", "✕"), "bấm ✕");
      await sleep(700);
      ok((await hash()) === ds, `✕ → về danh sách (#${await hash()})`);
      ok(await click("a.back"), "bấm về Menu quản lý");
      await sleep(700);
      ok((await hash()) === "admin", `về menu (#${await hash()})`);
    }
    console.log(fail ? `CÓ ${fail} BƯỚC SAI` : "TẤT CẢ ĐẠT");
  } else if (cmd === "quet") {
    await open("login");
    const r = await ev(QUET);
    console.log(JSON.stringify({ act: r.act, actTheoLoai: r.actBy, go: r.go, pick: r.pick, disabled: r.disabled.length, hint: r.hint.length, badTarget: r.badTarget, err: r.err }, null, 1));
    console.log("--- hint ---" + "\n" + r.hint.join("\n"));
    console.log("--- disabled ---" + "\n" + r.disabled.join("\n"));
    fail = r.badTarget.length + r.err.length;
  } else { console.log("Dùng: node bam-thu.mjs danh-muc [thư-mục-ảnh] | quet"); fail = 1; }
} catch (e) { console.error("LỖI:", e.message); fail = 1; }
done(fail ? 1 : 0);
