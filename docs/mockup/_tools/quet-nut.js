(async () => {
  const w = (ms) => new Promise((r) => setTimeout(r, ms));
  const S = JSON.parse(document.getElementById("data").textContent).screens;
  const out = { go: 0, pick: 0, disabled: [], hint: [], badTarget: [], goList: [], err: [] };
  const fr = () => document.querySelector("iframe");
  const open = async (key) => { location.hash = "#" + key; await w(220); };
  for (const s of S) {
    await open(s.key);
    const n = fr().contentDocument.querySelectorAll("button").length;
    for (let i = 0; i < n; i++) {
      if (location.hash !== "#" + s.key) await open(s.key);
      const b = fr().contentDocument.querySelectorAll("button")[i];
      if (!b) continue;
      const txt = b.textContent.trim().replace(/\s+/g, " ").slice(0, 40);
      const go = b.getAttribute("data-go"), pk = b.hasAttribute("data-pick");
      if (b.disabled) { out.disabled.push(s.key + " | " + txt + (go ? " [go " + go + "]" : "")); continue; }
      document.getElementById("hint").textContent = "";
      b.click();
      await w(260);
      const h = document.getElementById("hint").textContent;
      const now = location.hash.slice(1);
      if (go) {
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
})()
