const { invoke } = window.__TAURI__.core;

let currentVariables = {};

// ── Toast ──
let toastTimer = null;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 2200);
}

// ── Variable substitution ──
function escapeRegex(str) {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function buildOutput() {
  let output = document.getElementById('template-editor').value;
  for (const [name, input] of Object.entries(currentVariables)) {
    const re = new RegExp('\\$' + escapeRegex(name) + '(?![a-zA-Z0-9_-])', 'g');
    output = output.replace(re, input.value);
  }
  return output;
}

// ── Scan variables ──
function scanVariables() {
  const template = document.getElementById('template-editor').value;
  const found = [...new Set((template.match(/\$([a-zA-Z0-9_-]+)/g) || []).map(v => v.slice(1)))].sort();

  const oldValues = {};
  for (const [name, input] of Object.entries(currentVariables)) {
    oldValues[name] = input.value;
  }

  const panel = document.getElementById('variables-panel');
  panel.innerHTML = '';
  currentVariables = {};

  if (found.length === 0) {
    panel.innerHTML = '<div class="no-vars">No variables found</div>';
    updatePreview();
    return;
  }

  found.forEach(name => {
    const row = document.createElement('div');
    row.className = 'var-row';

    const label = document.createElement('label');
    label.textContent = '$' + name;
    label.className = 'var-label';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'var-input';
    input.placeholder = name;
    input.value = oldValues[name] || '';
    input.addEventListener('input', updatePreview);

    row.appendChild(label);
    row.appendChild(input);
    panel.appendChild(row);
    currentVariables[name] = input;
  });

  updatePreview();
}

// ── Preview ──
function updatePreview() {
  document.getElementById('preview-output').value = buildOutput();
}

// ── Load templates into dropdown ──
async function loadTemplates() {
  const templates = await invoke('get_templates');
  const select = document.getElementById('template-select');
  select.innerHTML = '';

  if (templates.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No Templates Found';
    select.appendChild(opt);
    return;
  }

  templates.forEach(t => {
    const opt = document.createElement('option');
    opt.value = t;
    opt.textContent = t.replace(/\.txt$/, '');
    select.appendChild(opt);
  });

  await loadTemplate(templates[0]);
}

async function loadTemplate(name) {
  try {
    const content = await invoke('load_template', { name });
    document.getElementById('template-editor').value = content;
    scanVariables();
  } catch (e) {
    toast('Failed to load template: ' + e);
  }
}

// ── Tab switching ──
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('tab-' + tab.dataset.tab).classList.add('active');
    if (tab.dataset.tab === 'preview') updatePreview();
  });
});

// ── Event listeners ──
document.getElementById('template-select').addEventListener('change', async e => {
  if (e.target.value) await loadTemplate(e.target.value);
});

document.getElementById('template-editor').addEventListener('input', scanVariables);

document.getElementById('btn-rescan').addEventListener('click', scanVariables);

document.getElementById('btn-load-external').addEventListener('click', async () => {
  const result = await invoke('load_external_dialog');
  if (result) {
    document.getElementById('template-editor').value = result.content;
    scanVariables();
    toast('Template loaded');
  }
});

document.getElementById('btn-generate').addEventListener('click', async () => {
  const saved = await invoke('save_config_dialog', { content: buildOutput() });
  if (saved) toast('Config saved');
});

document.getElementById('btn-copy').addEventListener('click', async () => {
  await navigator.clipboard.writeText(buildOutput());
  toast('Copied to clipboard');
});

// ── Init ──
loadTemplates();
