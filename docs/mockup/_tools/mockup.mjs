// Tách / ghép mockup. Dùng: node docs/mockup/_tools/mockup.mjs tach|ghep
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const TOOLS = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(TOOLS, "..");
const GOC = path.join(ROOT, "goc", "mockup-goc.html");
const MAN = path.join(ROOT, "de-xuat", "man");
const OUT = path.join(ROOT, "de-xuat", "ban-xem-truoc.html");
const VO = path.join(TOOLS, "vo.html");
const MARK = "@@DATA@@";
const OPEN = '<script type="application/json" id="data">';
const CLOSE = "</script>";

// STT trong menu -> cụm
const CUM = {
  "a-nhap-xuat-kho": (n) => n >= 2 && n <= 14,
  "b-san-xuat": (n) => (n >= 15 && n <= 18) || [23, 24, 26].includes(n),
  "c-quan-ly-in-qr": () => true,
};
const cumOf = (n) => Object.keys(CUM).find((c) => CUM[c](n));
const pad = (n) => String(n).padStart(2, "0");
const w = (f, s) => (fs.mkdirSync(path.dirname(f), { recursive: true }), fs.writeFileSync(f, s));
// Cách viết giống bản gốc (kiểu Python: ", " và ": ", chữ Việt giữ nguyên, </ -> <\/)
const dumps = (v) => Array.isArray(v) ? "[" + v.map(dumps).join(", ") + "]"
  : v && typeof v === "object" ? "{" + Object.entries(v).map(([k, x]) => JSON.stringify(k) + ": " + dumps(x)).join(", ") + "}"
  : JSON.stringify(v);
const ser = (D) => dumps(D).replace(/<\//g, "<\\/");
const canon = (v) => Array.isArray(v) ? v.map(canon) : v && typeof v === "object"
  ? Object.fromEntries(Object.keys(v).sort().map((k) => [k, canon(v[k])])) : v;

function tach() {
  const src = fs.readFileSync(GOC, "utf8");
  const a = src.indexOf(OPEN);
  const b = src.indexOf(CLOSE, a);
  const D = JSON.parse(src.slice(a + OPEN.length, b));
  w(VO, src.slice(0, a) + OPEN + MARK + src.slice(b));
  w(path.join(MAN, "app.css"), D.css);
  const ds = {};
  D.screens.forEach((s, i) => {
    const n = i + 1, c = cumOf(n);
    (ds[c] ??= []).push({ stt: pad(n), key: s.key, title: s.title, group: s.group, kind: s.kind });
    w(path.join(MAN, c, `${pad(n)}-${s.key}.html`), s.html);
  });
  for (const c of Object.keys(ds)) w(path.join(MAN, c, "_ds.json"), JSON.stringify(ds[c], null, 2) + "\n");
  const extra = Object.keys(D).filter((k) => !["css", "screens"].includes(k));
  console.log(`tach: ${D.screens.length} màn, ${Object.keys(ds).length} cụm${extra.length ? "; khoá khác bị bỏ: " + extra : ""}`);
}

function docDs() {
  const all = [];
  for (const c of fs.readdirSync(MAN, { withFileTypes: true }).filter((d) => d.isDirectory()).map((d) => d.name).sort()) {
    const f = path.join(MAN, c, "_ds.json");
    if (!fs.existsSync(f)) continue;
    for (const e of JSON.parse(fs.readFileSync(f, "utf8"))) all.push({ ...e, cum: c });
  }
  const base = all.filter((e) => !e.sau).sort((x, y) => x.stt.localeCompare(y.stt, "en", { numeric: true }));
  const out = [...base];
  const pending = all.filter((e) => e.sau);
  while (pending.length) { // màn mới: chèn sau key đứng trước (có thể móc nối nhau)
    const before = pending.length;
    for (let i = 0; i < pending.length; i++) {
      const k = out.findIndex((e) => e.key === pending[i].sau);
      if (k >= 0) { out.splice(k + 1, 0, pending[i]); pending.splice(i--, 1); }
    }
    if (pending.length === before) throw new Error("`sau` không tìm thấy: " + pending.map((e) => e.key + "→" + e.sau));
  }
  return out;
}

function ghep() {
  const list = docDs();
  const screens = list.map((e) => ({
    title: e.title, group: e.group, kind: e.kind,
    html: fs.readFileSync(path.join(MAN, e.cum, e.file ?? `${e.stt}-${e.key}.html`), "utf8"), key: e.key,
  }));
  const D = { css: fs.readFileSync(path.join(MAN, "app.css"), "utf8"), screens };
  const vo = fs.readFileSync(VO, "utf8");
  w(OUT, vo.replace(MARK, () => ser(D)));
  console.log(`ghep: ${screens.length} màn -> ${path.relative(ROOT, OUT)}`);
  // so sánh với bản gốc
  const src = fs.readFileSync(GOC, "utf8");
  const a = src.indexOf(OPEN) + OPEN.length;
  const G = JSON.parse(src.slice(a, src.indexOf(CLOSE, a)));
  const same = JSON.stringify(canon(G)) === JSON.stringify(canon(D));
  console.log(same ? "OK: dữ liệu giống bản gốc" : `KHÁC bản gốc (gốc ${G.screens.length} màn, mới ${screens.length}) — bình thường nếu đã sửa/thêm màn`);
}

const cmd = process.argv[2];
if (cmd === "tach") tach(); else if (cmd === "ghep") ghep(); else { console.log("Dùng: node mockup.mjs tach|ghep"); process.exit(1); }
