function fmtReset(iso, useDays) {
  if (!iso) return { left: "", right: "" };
  const d = new Date(iso);
  const diffMs = d - new Date();
  const time = d.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  const when = useDays
    ? d.toLocaleDateString("en-GB", { weekday: "short" }).replace(".", "") + " · " +
      d.toLocaleDateString("en-GB", { day: "2-digit", month: "2-digit" }) + " · " + time
    : time;
  if (diffMs <= 0) return { left: "resetting", right: when };
  const totalH = Math.floor(diffMs / 3600000);
  const m = Math.floor((diffMs % 3600000) / 60000);
  let countdown;
  if (useDays && totalH >= 24) {
    const days = Math.floor(totalH / 24);
    const h = totalH % 24;
    countdown = h > 0 ? `${days}d ${h}h` : `${days}d`;
  } else {
    countdown = totalH > 0 ? `${totalH}h ${m}m` : `${m}m`;
  }
  return { left: `resets in ${countdown}`, right: when };
}

const SCREEN_HUE = { session: 15, week: 15, disk: 195, memory: 192, cpu: 24 };

function fillColor(pct, hue) {
  // same hue as the screen's icon; higher value = more saturated & less pastel
  const p = Math.min(pct, 100) / 100;
  const sat = 35 + p * 35;
  const light = 80 - p * 25;
  return `hsl(${hue}, ${sat}%, ${light}%)`;
}

async function refresh() {
  try {
    const r = await fetch("/api/usage");
    const data = await r.json();
    if (data.error) { document.getElementById("err").textContent = data.error; return; }
    document.getElementById("err").textContent = "";
    for (const [key, val] of [["session", data.session], ["week", data.week]]) {
      const pct = Math.round(val.pct);
      document.getElementById(`${key}-pct`).textContent = pct + "%";
      const fill = document.getElementById(`${key}-fill`);
      fill.style.width = pct + "%";
      fill.style.backgroundColor = fillColor(pct, SCREEN_HUE[key]);
      const reset = fmtReset(val.resets_at, key === "week");
      document.getElementById(`${key}-reset-left`).textContent = reset.left;
      document.getElementById(`${key}-reset-right`).textContent = reset.right;
    }
    if (data.weather && data.weather.temp != null) {
      document.getElementById("temp").textContent = Math.round(data.weather.temp) + "°";
      document.getElementById("humidity").textContent = Math.round(data.weather.humidity) + "%";
    }
    if (data.city) {
      document.getElementById("city").textContent = data.city;
    }
    const gb = b => (b / 1024 ** 3).toFixed(0);
    function setMeter(prefix, pct, hue, leftText, rightText) {
      const pctEl = document.getElementById(`${prefix}-pct`);
      if (!pctEl) return;
      pctEl.textContent = pct + "%";
      const fill = document.getElementById(`${prefix}-fill`);
      fill.style.width = pct + "%";
      fill.style.backgroundColor = fillColor(pct, hue);
      document.getElementById(`${prefix}-used-total`).textContent = leftText;
      document.getElementById(`${prefix}-free`).textContent = rightText;
    }
    for (const [key, val] of [["disk", data.disk], ["memory", data.memory]]) {
      if (!val) continue;
      const pct = Math.round(val.pct);
      const left = `${gb(val.used)}/${gb(val.total)} GB`;
      const right = `${gb(val.free)} GB free`;
      setMeter(`ov-${key}`, pct, SCREEN_HUE[key], left, right);
    }
    if (data.cpu) {
      const pct = Math.round(data.cpu.pct);
      const cores = data.cpu.cores;
      const usedCores = (pct / 100 * cores).toFixed(1);
      const freeCores = (cores - usedCores).toFixed(1);
      const left = `${usedCores}/${cores}`;
      const right = `${freeCores} free`;
      setMeter("ov-cpu", pct, SCREEN_HUE.cpu, left, right);
    }
  } catch (e) {
    document.getElementById("err").textContent = "Error fetching usage: " + e;
  }
}

function tickClock() {
  const now = new Date();
  document.getElementById("clock").textContent =
    now.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" });
  document.getElementById("weekday").textContent =
    now.toLocaleDateString("en-GB", { weekday: "short" }).replace(".", "");
}

const screens = ["screen-usage", "screen-overview", "screen-pomodoro"];
const FAST_SCREENS = new Set(["screen-overview"]);
let screenIdx = 0;
function goToScreen(dir) {
  screenIdx = (screenIdx + dir + screens.length) % screens.length;
  const current = screens[screenIdx];
  screens.forEach(id => document.getElementById(id).classList.toggle("active", id === current));
  document.getElementById("top").dataset.screen = current;
  clearTimeout(refreshTimer);
  scheduleRefresh();
}
function handleClick(e) {
  if (e.target.closest(".pomo-ctls")) return;
  document.getElementById("pomo-menu").hidden = true;
  goToScreen(e.clientX > window.innerWidth / 2 ? 1 : -1);
}

tickClock();
setInterval(tickClock, 1000);

let refreshTimer;
function scheduleRefresh() {
  refresh();
  const interval = FAST_SCREENS.has(screens[screenIdx]) ? 3000 : 120000;
  refreshTimer = setTimeout(scheduleRefresh, interval);
}
scheduleRefresh();

const POMO = { focus: 25 * 60, short: 5 * 60, long: 15 * 60, every: 4 };
const POMO_LABEL = { focus: "Focus", short: "Break", long: "Long break" };
const pomo = { phase: "focus", done: 0, left: POMO.focus, endAt: null };
try { Object.assign(pomo, JSON.parse(localStorage.getItem("pomo"))); } catch (e) {}

function pomoLeft() {
  return pomo.endAt ? Math.max(0, Math.ceil((pomo.endAt - Date.now()) / 1000)) : pomo.left;
}
function pomoRender() {
  const s = pomoLeft();
  const pad = n => String(n).padStart(2, "0");
  document.getElementById("pomo-time").textContent = `${pad(Math.floor(s / 60))}:${pad(s % 60)}`;
  document.getElementById("pomo-label").textContent = POMO_LABEL[pomo.phase];
  const n = pomo.phase === "long" ? POMO.every : pomo.done % POMO.every;
  document.querySelectorAll("#pomo-dots i").forEach((d, i) => d.classList.toggle("on", i < n));
  document.getElementById("pomo-toggle").classList.toggle("running", !!pomo.endAt);
  document.getElementById("pomo-toggle-text").textContent = pomo.endAt ? "Pause" : "Start";
  try { localStorage.setItem("pomo", JSON.stringify(pomo)); } catch (e) {}
}
function pomoAlert() {
  document.body.classList.remove("pomo-flash");
  void document.body.offsetWidth;
  document.body.classList.add("pomo-flash");
  try {
    const ctx = new AudioContext();
    [0, .3, .6].forEach(t => {
      const o = ctx.createOscillator();
      o.frequency.value = 880;
      o.connect(ctx.destination);
      o.start(ctx.currentTime + t);
      o.stop(ctx.currentTime + t + .15);
    });
  } catch (e) {}
}
function pomoToggle() {
  if (pomo.endAt) { pomo.left = pomoLeft(); pomo.endAt = null; }
  else pomo.endAt = Date.now() + pomo.left * 1000;
  pomoRender();
}
function pomoNext() {
  if (pomo.phase === "focus") {
    pomo.done++;
    pomo.phase = pomo.done % POMO.every === 0 ? "long" : "short";
  } else {
    pomo.phase = "focus";
  }
  pomoResetTimer();
}
function pomoResetTimer() {
  pomo.left = POMO[pomo.phase];
  pomo.endAt = null;
  document.getElementById("pomo-menu").hidden = true;
  pomoRender();
}
function pomoResetSession() {
  pomo.phase = "focus";
  pomo.done = 0;
  pomoResetTimer();
}
function pomoMenu() {
  const m = document.getElementById("pomo-menu");
  m.hidden = !m.hidden;
}
setInterval(() => {
  if (pomo.endAt && pomoLeft() === 0) { pomoAlert(); pomoNext(); }
  else if (pomo.endAt) pomoRender();
}, 500);
pomoRender();
