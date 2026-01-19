/* static/script.js – you can inline it or keep it in a separate file */
function msJitter(baseMs, jitterMs = 2000) {
  // Returns a delay around `baseMs` ± `jitterMs/2`
  return baseMs + Math.floor(Math.random() * jitterMs) - Math.floor(jitterMs / 2);
}

async function refresh() {
  try {
    const r = await fetch('/followers');
    const d = await r.json();

    if (d.followers !== undefined) {
      document.getElementById('count').textContent = d.followers.toLocaleString();

      const now = new Date();
      const opts = { hour: '2-digit', minute: '2-digit', second: '2-digit',
                     day: 'numeric', month: 'short', year: 'numeric' };
      document.getElementById('updated').textContent =
        `Last update: ${now.toLocaleString(undefined, opts)}`;
    }
  } catch (e) {
    console.error('Fetch error:', e);
    document.getElementById('updated').textContent = 'Error loading data';
  }
}

/* Initial call */
refresh();

/* Schedule next call – 30 000 ms = 30 s, plus jitter */
function scheduleNext() {
  const delay = msJitter(30_000);
  setTimeout(() => {
    refresh().finally(scheduleNext);
  }, delay);
}
scheduleNext();