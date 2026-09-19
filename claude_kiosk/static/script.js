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

const screens = ["screen-usage", "screen-overview"];
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
