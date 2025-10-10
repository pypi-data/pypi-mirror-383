const roundsEl = document.getElementById('rounds');
const flightEl = document.getElementById('flight');
const statusEl = document.getElementById('status');
const summaryEl = document.getElementById('summary');
const promptEl = document.getElementById('prompt');
const eventsEl = document.getElementById('events');
const diffsEl = document.getElementById('diffs');
const commitsEl = document.getElementById('commits');

async function fetchIndex() {
  const res = await fetch('/api/index');
  const js = await res.json();
  return js.items || [];
}

function liFor(item) {
  const li = document.createElement('li');
  const title = document.createElement('div');
  title.className = 'round-title';
  const time = document.createElement('span');
  time.className = 'time';
  time.textContent = item.ts || '';
  const branch = document.createElement('span');
  branch.className = 'branch';
  branch.textContent = (item.git && item.git.branch) || 'no-branch';
  title.appendChild(time);
  title.appendChild(branch);
  li.appendChild(title);
  li.addEventListener('click', async () => {
    for (const sib of roundsEl.children) sib.classList.remove('active');
    li.classList.add('active');
    const path = item.path;
    const res = await fetch(`/api/round/${encodeURIComponent(path)}`);
    const js = await res.json();
    renderRound(js);
  });
  return li;
}

async function init() {
  statusEl.textContent = 'Loading…';
  try {
    const [items, flights] = await Promise.all([
      fetchIndex(),
      fetch('/api/flight-log').then(r => r.json()).then(j => j.items || []).catch(() => []),
    ]);
    roundsEl.textContent = '';
    for (const it of items) {
      roundsEl.appendChild(liFor(it));
    }
    flightEl.textContent = '';
    for (const fl of flights) {
      const li = document.createElement('li');
      const level = (fl.badge || '').toLowerCase();
      const badge = fl.badge ? `<span class="badge ${level}">${escapeHtml(fl.badge)}</span>` : '';
      const scope = fl.scope ? ` — ${escapeHtml(fl.scope)}` : '';
      li.innerHTML = `<span class="time">${escapeHtml(fl.date)} ${escapeHtml(fl.time)}</span> ${badge} ${escapeHtml(fl.headline)}${scope}`;
      if (Array.isArray(fl.details) && fl.details.length) {
        const ul = document.createElement('ul');
        for (const d of fl.details) {
          const di = document.createElement('li');
          di.textContent = d;
          ul.appendChild(di);
        }
        li.appendChild(ul);
      }
      flightEl.appendChild(li);
    }
    const recent = items.some(it => isRecent(it.ts, 10));
    statusEl.textContent = `${items.length} rounds${recent ? '' : ' · No recent logs'}`;
    if (items[0]) {
      roundsEl.firstChild.click();
    }
  } catch (e) {
    statusEl.textContent = 'Failed to load';
  }
}

init();

function renderRound(js) {
  const fields = [
    ['Time', js.recorded_at || ''],
    ['User', (js.user && js.user.name) || ''],
    ['Email', (js.user && js.user.email) || ''],
    ['Branch', (js.git && js.git.branch) || ''],
    ['Commit', (js.git && js.git.commit) || ''],
    ['Status', js.status || ''],
    ['Files', (js.diffs || []).length + ''],
    ['Events', (js.events || []).length + ''],
  ];
  summaryEl.innerHTML = '<div class="kv">' + fields.map(([k,v]) => `<div class="k">${k}</div><div class="v">${escapeHtml(v)}</div>`).join('') + '</div>';

  const p = js.prompt || {};
  const promptText = typeof p.text === 'string' ? p.text : JSON.stringify(p, null, 2);
  promptEl.textContent = promptText || '';

  eventsEl.textContent = '';
  for (const ev of (js.events || [])) {
    const li = document.createElement('li');
    li.textContent = `${ev.ts}  ${ev.type}${ev.path ? ' ' + ev.path : ''}${ev.name ? ' ' + ev.name : ''}`;
    eventsEl.appendChild(li);
  }

  commitsEl.textContent = '';
  if (Array.isArray(js.commits_since_last)) {
    for (const c of js.commits_since_last) {
      const li = document.createElement('li');
      li.textContent = `${c.sha.slice(0,7)} ${c.category.toUpperCase()} ${c.author} <${c.email}>: ${c.subject}`;
      commitsEl.appendChild(li);
    }
  }

  let diffOut = '';
  for (const d of (js.diffs || [])) {
    diffOut += `\n# ${d.path}\n`;
    diffOut += formatUnifiedDiff(d.unified_diff || '');
  }
  diffsEl.innerHTML = diffOut || '';
}

function isRecent(ts, minutes) {
  if (!ts) return false;
  const t = Date.parse(ts);
  if (Number.isNaN(t)) return false;
  const ageMs = Date.now() - t;
  return ageMs <= minutes * 60 * 1000;
}

function escapeHtml(s) {
  return String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
}

function formatUnifiedDiff(text) {
  const lines = (text || '').split(/\r?\n/);
  return lines.map(l => {
    if (l.startsWith('+') && !l.startsWith('+++')) return `<span class="add">${escapeHtml(l)}</span>`;
    if (l.startsWith('-') && !l.startsWith('---')) return `<span class="del">${escapeHtml(l)}</span>`;
    return escapeHtml(l);
  }).join('\n');
}

