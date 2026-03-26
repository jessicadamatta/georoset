/**
 * georoset/docs/js/app.js
 * Lógica de UI: navegação, renderização de formulários, conversões, gráficos.
 */

// ─── Configurações por software ──────────────────────────────────────────────

const DISC_COLS = {
  'Leapfrog / Isatis.neo': ['Dip (°)', 'Dip Direction (°)'],
  'Vulcan': ['Bearing da normal (°)', 'Plunge da normal (°)'],
};

const VARIO_COLS = {
  'Leapfrog':   ['Bearing (°)', 'Plunge (°)', 'Rake (°)'],
  'Isatis.neo': ['Azimute (°)', 'Mergulho (°)', 'Rake (°)'],
  'Vulcan':     ['Bearing (°)', 'Plunge (°)', 'Dip (°)'],
};

const BLOCK_COLS = {
  'Leapfrog':   ['Bearing (°)', 'Plunge (°)', 'Dip (°)'],
  'Isatis.neo': ['Azimute (°)', 'Mergulho (°)', 'Rake (°)'],
  'Vulcan':     ['Bearing (°)', 'Plunge (°)', 'Dip (°)'],
};

// ─── Navegação entre páginas ─────────────────────────────────────────────────

function showPage(id, linkEl) {
  document.querySelectorAll('[id^="page-"]').forEach(el => el.classList.add('d-none'));
  document.getElementById('page-' + id).classList.remove('d-none');
  document.querySelectorAll('#mainTabs .nav-link').forEach(l => l.classList.remove('active'));
  linkEl.classList.add('active');

  // Inicializar página ao abrir
  if (id === 'discos') initDiscs();
  if (id === 'vario')  initVario();
  if (id === 'blocos') initBlocos();
  if (id === 'coords') initCoords();
  return false;
}

function switchMode(page, mode, linkEl) {
  // Esconder todos os modos da página
  document.querySelectorAll(`[id^="${page}-mode-"]`).forEach(el => el.classList.add('d-none'));
  document.getElementById(`${page}-mode-${mode}`).classList.remove('d-none');
  // Atualizar abas
  linkEl.closest('.mode-tabs').querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
  linkEl.classList.add('active');
  return false;
}

// ─── Helpers de formulário ───────────────────────────────────────────────────

function numInput(id, label, min, max, step, val) {
  return `
    <div class="mb-3">
      <label class="form-label fw-semibold small text-uppercase" style="letter-spacing:.5px;color:#555">${label}</label>
      <input type="number" class="form-control" id="${id}" min="${min}" max="${max}" step="${step}" value="${val}">
    </div>`;
}

function getVal(id) { return parseFloat(document.getElementById(id).value) || 0; }

function renderMetrics(containerId, metrics) {
  const el = document.getElementById(containerId);
  el.innerHTML = metrics.map(([label, value]) => `
    <div class="col">
      <div class="metric-box">
        <div class="metric-label">${label}</div>
        <div class="metric-value">${(+value).toFixed(3)}°</div>
      </div>
    </div>`).join('');
}

// ─── Tabela editável ─────────────────────────────────────────────────────────

function buildTableHeader(theadId, cols) {
  const thead = document.getElementById(theadId);
  thead.innerHTML = `<tr>${cols.map(c => `<th>${c}</th>`).join('')}<th></th></tr>`;
}

function addTableRow(tbodyId, cols, values) {
  const tbody = document.getElementById(tbodyId);
  const vals  = values || cols.map(() => '0');
  const tr    = document.createElement('tr');
  tr.innerHTML = cols.map((_, i) =>
    `<td><input type="number" step="0.001" value="${vals[i]}"></td>`
  ).join('') +
  `<td><button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="this.closest('tr').remove()">✕</button></td>`;
  tbody.appendChild(tr);
}

function getTableRows(tbodyId) {
  const rows = [];
  document.querySelectorAll(`#${tbodyId} tr`).forEach(tr => {
    const inputs = tr.querySelectorAll('input');
    rows.push([...inputs].map(i => parseFloat(i.value) || 0));
  });
  return rows;
}

function buildResultTable(tableId, headers, rows) {
  const table = document.getElementById(tableId);
  table.innerHTML = `<thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
    <tbody>${rows.map(r =>
      `<tr>${r.map(v => `<td>${typeof v === 'number' ? v.toFixed(4) : v}</td>`).join('')}</tr>`
    ).join('')}</tbody>`;
}

// ─── Esteronet de Schmidt (Plotly) ───────────────────────────────────────────

function poleXY(dip, dd) {
  const r = Math.sqrt(2) * Math.sin(dip * D2R / 2);
  return [r * Math.sin(dd * D2R), r * Math.cos(dd * D2R)];
}

function plotStereonet(divId, dip_o, dd_o, dip_c, dd_c, srcLabel, dstLabel) {
  const traces = [];
  const t = Array.from({length: 361}, (_, i) => i * D2R);

  // borda
  traces.push({ x: t.map(Math.cos), y: t.map(Math.sin), mode:'lines',
    line:{color:'#555',width:2}, showlegend:false, hoverinfo:'skip' });
  // grade círculos
  [30, 60].forEach(d => {
    const r = Math.sqrt(2) * Math.sin(d * D2R / 2);
    traces.push({ x: t.map(a => r*Math.cos(a)), y: t.map(a => r*Math.sin(a)),
      mode:'lines', line:{color:'#ccc',width:.7,dash:'dot'}, showlegend:false, hoverinfo:'skip' });
  });
  // raios
  [0,45,90,135,180,225,270,315].forEach(az => {
    const a = az * D2R;
    traces.push({ x:[0,Math.sin(a)], y:[0,Math.cos(a)], mode:'lines',
      line:{color:'#ccc',width:.7,dash:'dot'}, showlegend:false, hoverinfo:'skip' });
  });

  const [xo, yo] = poleXY(dip_o, dd_o);
  const [xc, yc] = poleXY(dip_c, dd_c);

  traces.push({ x:[xo], y:[yo], mode:'markers',
    marker:{symbol:'triangle-up',size:16,color:'#1f77b4',line:{color:'#0a3d7a',width:1.5}},
    name:`Original (${srcLabel})`,
    hovertemplate:`Dip=${dip_o.toFixed(1)}°  Dir=${dd_o.toFixed(1)}°<extra>${srcLabel}</extra>` });
  traces.push({ x:[xc], y:[yc], mode:'markers',
    marker:{symbol:'circle',size:14,color:'#d62728',line:{color:'#8b0000',width:1.5}},
    name:`Convertido (${dstLabel})`,
    hovertemplate:`Dip=${dip_c.toFixed(1)}°  Dir=${dd_c.toFixed(1)}°<extra>${dstLabel}</extra>` });

  const annotations = [
    {x:0, y:1.12, text:'<b>N</b>', showarrow:false, font:{size:12,color:'#888'}},
    {x:1.14, y:0, text:'<b>E</b>', showarrow:false, font:{size:12,color:'#888'}},
    {x:0, y:-1.16, text:'<b>S</b>', showarrow:false, font:{size:12,color:'#888'}},
    {x:-1.18, y:0, text:'<b>W</b>', showarrow:false, font:{size:12,color:'#888'}},
  ];

  Plotly.react(divId, traces, {
    xaxis:{visible:false, range:[-1.3,1.3]},
    yaxis:{visible:false, range:[-1.3,1.3], scaleanchor:'x'},
    height:350, plot_bgcolor:'white', paper_bgcolor:'white',
    legend:{orientation:'h', x:0, y:-0.04, font:{size:11}},
    margin:{l:5,r:5,t:5,b:5}, annotations,
  }, {responsive:true, displayModeBar:false});
}

// ─── Elipsoide 3D (Plotly) ───────────────────────────────────────────────────

function ellipsoidXYZ(R, a1, a2, a3, n=25) {
  const u = Array.from({length:n}, (_,i) => i*2*Math.PI/(n-1));
  const v = Array.from({length:n}, (_,i) => i*Math.PI/(n-1));
  const X=[], Y=[], Z=[];
  for (let i=0; i<n; i++) {
    X.push([]); Y.push([]); Z.push([]);
    for (let j=0; j<n; j++) {
      const xs = Math.cos(u[i])*Math.sin(v[j])*a1;
      const ys = Math.sin(u[i])*Math.sin(v[j])*a2;
      const zs = Math.cos(v[j])*a3;
      X[i].push(R[0][0]*xs + R[0][1]*ys + R[0][2]*zs);
      Y[i].push(R[1][0]*xs + R[1][1]*ys + R[1][2]*zs);
      Z[i].push(R[2][0]*xs + R[2][1]*ys + R[2][2]*zs);
    }
  }
  return {X, Y, Z};
}

function plotEllipsoid(divId, R_orig, R_conv, a1, a2, a3, srcLabel, dstLabel) {
  const eo = ellipsoidXYZ(R_orig, a1, a2, a3);
  const ec = ellipsoidXYZ(R_conv, a1, a2, a3);
  const mx = Math.max(a1,a2,a3)*1.3;
  const traces = [
    { type:'surface', x:eo.X, y:eo.Y, z:eo.Z,
      colorscale:[[0,'#1f77b4'],[1,'#1f77b4']], opacity:.45,
      showscale:false, name:`Original (${srcLabel})`, hoverinfo:'skip' },
    { type:'surface', x:ec.X, y:ec.Y, z:ec.Z,
      colorscale:[[0,'#d62728'],[1,'#d62728']], opacity:.30,
      showscale:false, name:`Convertido (${dstLabel})`, hoverinfo:'skip' },
    { type:'scatter3d', x:[0,mx], y:[0,0], z:[0,0], mode:'lines+text',
      line:{color:'#d62728',width:3}, text:['','<b>E</b>'], textposition:'top center',
      showlegend:false, hoverinfo:'skip' },
    { type:'scatter3d', x:[0,0], y:[0,mx], z:[0,0], mode:'lines+text',
      line:{color:'#2ca02c',width:3}, text:['','<b>N</b>'], textposition:'top center',
      showlegend:false, hoverinfo:'skip' },
    { type:'scatter3d', x:[0,0], y:[0,0], z:[0,mx], mode:'lines+text',
      line:{color:'#1f77b4',width:3}, text:['','<b>Z</b>'], textposition:'top center',
      showlegend:false, hoverinfo:'skip' },
  ];
  Plotly.react(divId, traces, {
    scene:{xaxis_title:'Leste', yaxis_title:'Norte', zaxis_title:'Cima'},
    height:370, showlegend:true,
    legend:{orientation:'h', x:0, y:-0.05, font:{size:11}},
    margin:{l:0,r:0,t:5,b:0},
  }, {responsive:true});
}

// ─── Bloco 3D (Plotly) ──────────────────────────────────────────────────────

function blockCorners(R) {
  const local = [[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]].map(p => p.map(v=>v*.5));
  return local.map(p => [
    R[0][0]*p[0]+R[0][1]*p[1]+R[0][2]*p[2],
    R[1][0]*p[0]+R[1][1]*p[1]+R[1][2]*p[2],
    R[2][0]*p[0]+R[2][1]*p[1]+R[2][2]*p[2],
  ]);
}

function plotBlock(divId, R_orig, R_conv, srcLabel, dstLabel) {
  const traces = [];
  const configs = [
    [R_orig, srcLabel, '#aec7e8', .4],
    [R_conv, dstLabel, '#ffbb78', .25],
  ];
  configs.forEach(([R, label, color, opacity]) => {
    const c = blockCorners(R);
    const fi = [0,0,4,4,0,0,3,3,1,1,2,2];
    const fj = [1,3,5,7,4,1,7,4,5,2,6,3];
    const fk = [2,2,6,6,5,5,6,6,6,6,7,7];
    traces.push({ type:'mesh3d',
      x:c.map(p=>p[0]), y:c.map(p=>p[1]), z:c.map(p=>p[2]),
      i:fi, j:fj, k:fk, opacity, color, name:label, showlegend:true, hoverinfo:'skip' });
    const center = [0,0,0];
    const axColors = ['#d62728','#2ca02c','#ff7f0e'];
    const axNames  = ['U','V','W'];
    [0,1,2].forEach(a => {
      const vec = [R[0][a], R[1][a], R[2][a]];
      const sc  = .7;
      const end = vec.map(v => center[0]+v*sc);  // center is [0,0,0]
      traces.push({ type:'scatter3d',
        x:[0,vec[0]*sc], y:[0,vec[1]*sc], z:[0,vec[2]*sc],
        mode:'lines', line:{color:axColors[a],width:5},
        name:`${axNames[a]} (${label})`, showlegend:false, hoverinfo:'skip' });
    });
  });
  Plotly.react(divId, traces, {
    scene:{xaxis_title:'Leste',yaxis_title:'Norte',zaxis_title:'Cima',aspectmode:'cube'},
    height:370, showlegend:true,
    legend:{orientation:'h',x:0,y:-0.05,font:{size:11}},
    margin:{l:0,r:0,t:5,b:0},
  }, {responsive:true});
}

// ═══════════════════════════════════════════════════════════════════════════
// ── DISCOS ──
// ═══════════════════════════════════════════════════════════════════════════

let _discResultData = null;

function discSrc() { return document.getElementById('disc-src').value; }
function discDst() { return document.getElementById('disc-dst').value; }

function initDiscs() {
  renderDiscInputFields();
  buildDiscTable();
  document.getElementById('disc-src').onchange = () => { renderDiscInputFields(); buildDiscTable(); };
  document.getElementById('disc-dst').onchange = () => {};
}

function renderDiscInputFields() {
  const src  = discSrc();
  const cols = DISC_COLS[src];
  const fld  = document.getElementById('disc-input-fields');
  fld.innerHTML =
    numInput('disc-a', cols[0], 0, src === 'Vulcan' ? 360 : 90, 0.1, 0) +
    numInput('disc-b', cols[1], 0, 360, 0.1, 0) +
    `<button class="btn btn-convert w-100 mt-1" onclick="convertDiscSingle()">🔄 Converter</button>`;
  document.getElementById('disc-tbl-src-label').textContent = src;
}

function buildDiscTable() {
  const src  = discSrc();
  const cols = DISC_COLS[src];
  buildTableHeader('disc-input-thead', cols);
  document.getElementById('disc-input-tbody').innerHTML = '';
  const examples = [[0,0],[30,45],[45,90],[60,180],[90,270]];
  examples.forEach(v => addTableRow('disc-input-tbody', cols, v));
}

function discAddRow()   { addTableRow('disc-input-tbody', DISC_COLS[discSrc()]); }
function discLoadExample() { buildDiscTable(); }
function discPasteCSV()  { openCSVModal(rows => {
  document.getElementById('disc-input-tbody').innerHTML = '';
  rows.forEach(r => addTableRow('disc-input-tbody', DISC_COLS[discSrc()], r));
}); }

function convertDiscSingle() {
  const src = discSrc(), dst = discDst();
  const a = getVal('disc-a'), b = getVal('disc-b');

  let dip, dd;
  if (src === 'Vulcan') { [dip, dd] = vulcanToLeapfrogDisc(a, b); }
  else                  { [dip, dd] = [a, b]; }

  let v1, v2, dip_c, dd_c;
  if (dst === 'Vulcan') {
    [v1, v2] = leapfrogToVulcanDisc(dip, dd);
    [dip_c, dd_c] = vulcanToLeapfrogDisc(v1, v2);
  } else {
    [v1, v2] = [dip, dd];
    [dip_c, dd_c] = [dip, dd];
  }

  const dstCols = DISC_COLS[dst];
  renderMetrics('disc-metrics', [[dstCols[0], v1], [dstCols[1], v2]]);
  plotStereonet('stereonet-plot', dip, dd, dip_c, dd_c, src, dst);
  document.getElementById('disc-isatis-warn').classList.toggle('d-none', !dst.includes('Isatis'));
}

function convertDiscTable() {
  const src = discSrc(), dst = discDst();
  const srcCols = DISC_COLS[src], dstCols = DISC_COLS[dst];
  const inputRows = getTableRows('disc-input-tbody');
  const outRows = inputRows.map(([a, b]) => {
    let dip, dd;
    if (src === 'Vulcan') { [dip, dd] = vulcanToLeapfrogDisc(a, b); }
    else                  { [dip, dd] = [a, b]; }
    if (dst === 'Vulcan') return leapfrogToVulcanDisc(dip, dd);
    return [dip, dd];
  });
  _discResultData = { srcCols, dstCols, inputRows, outRows };
  buildResultTable('disc-result-in',  srcCols, inputRows);
  buildResultTable('disc-result-out', dstCols, outRows);
  document.getElementById('disc-result-card').classList.remove('d-none');
}

function downloadDiscResult() {
  if (!_discResultData) return;
  const { srcCols, dstCols, inputRows, outRows } = _discResultData;
  downloadCSV(
    inputRows.map((r,i) => [...r, ...outRows[i]]),
    [...srcCols, ...dstCols],
    'discos_convertidos.csv'
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// ── VARIOGRAMA ──
// ═══════════════════════════════════════════════════════════════════════════

let _varioResultData = null;

function varioSrc() { return document.getElementById('vario-src').value; }
function varioDst() { return document.getElementById('vario-dst').value; }

function initVario() {
  renderVarioInputFields();
  buildVarioTable();
  document.getElementById('vario-src').onchange = () => { renderVarioInputFields(); buildVarioTable(); };
}

function renderVarioInputFields() {
  const src  = varioSrc();
  const cols = VARIO_COLS[src];
  const fld  = document.getElementById('vario-input-fields');
  fld.innerHTML =
    numInput('vario-a', cols[0], -360, 360, 0.1, 0) +
    numInput('vario-b', cols[1], 0, 90, 0.1, 0) +
    numInput('vario-c', cols[2], -360, 360, 0.1, 0) +
    `<hr class="my-2"><small class="text-muted fw-semibold">ALCANCES (semieixos)</small>` +
    numInput('vario-a1', 'a₁ — maior alcance', 0.1, 99999, 1, 100) +
    numInput('vario-a2', 'a₂ — intermediário', 0.1, 99999, 1, 60) +
    numInput('vario-a3', 'a₃ — menor alcance', 0.1, 99999, 1, 20) +
    `<button class="btn btn-convert w-100 mt-1" onclick="convertVarioSingle()">🔄 Converter</button>`;
}

function buildVarioTable() {
  const src  = varioSrc();
  const cols = VARIO_COLS[src];
  buildTableHeader('vario-input-thead', cols);
  document.getElementById('vario-input-tbody').innerHTML = '';
  [[0,0,0],[30,20,10],[90,45,30]].forEach(v => addTableRow('vario-input-tbody', cols, v));
}

function varioAddRow()    { addTableRow('vario-input-tbody', VARIO_COLS[varioSrc()]); }
function varioLoadExample() { buildVarioTable(); }
function varioPasteCSV() { openCSVModal(rows => {
  document.getElementById('vario-input-tbody').innerHTML = '';
  rows.forEach(r => addTableRow('vario-input-tbody', VARIO_COLS[varioSrc()], r));
}); }

function getVarioMatrix(src, a, b, c) {
  if (src === 'Leapfrog')   return leapfrogVarioMatrix(a, b, c);
  if (src === 'Isatis.neo') return isatisVarioMatrix(a, b, c);
  return vulcanVarioMatrix(a, b, c);
}
function decompose(dst, R) {
  if (dst === 'Leapfrog')   return matrixToLeapfrogVario(R);
  if (dst === 'Isatis.neo') {
    // Aproximação: usar decomposição Leapfrog-like como base
    const [a,b,c] = matrixToLeapfrogVario(R);
    return [a, b, c]; // TODO: implementar decomposição Isatis exata
  }
  return matrixToVulcanVario(R);
}
function decomposeBlock(dst, R) {
  if (dst === 'Leapfrog')   return matrixToLeapfrogBlock(R);
  if (dst === 'Isatis.neo') return matrixToIsatisBlock(R);
  return matrixToVulcanBlock(R);
}
function getBlockMatrix(src, a, b, c) {
  if (src === 'Leapfrog')   return leapfrogBlockMatrix(a, b, c);
  if (src === 'Isatis.neo') return isatisBlockMatrix(a, b, c);
  return vulcanBlockMatrix(a, b, c);
}
function getVarioMatrixFromAngles(src, a, b, c) { return getVarioMatrix(src, a, b, c); }

function convertVarioSingle() {
  const src = varioSrc(), dst = varioDst();
  const a = getVal('vario-a'), b = getVal('vario-b'), c = getVal('vario-c');
  const a1 = getVal('vario-a1'), a2 = getVal('vario-a2'), a3 = getVal('vario-a3');

  const R = getVarioMatrix(src, a, b, c);
  const [v1, v2, v3] = decompose(dst, R);

  const R_dst = getVarioMatrix(dst, v1, v2, v3);

  const dstCols = VARIO_COLS[dst];
  renderMetrics('vario-metrics', [[dstCols[0], v1],[dstCols[1], v2],[dstCols[2], v3]]);
  plotEllipsoid('vario-plot', R, R_dst, a1, a2, a3, src, dst);
  document.getElementById('vario-isatis-warn').classList.toggle('d-none', dst !== 'Isatis.neo');
}

function convertVarioTable() {
  const src = varioSrc(), dst = varioDst();
  const srcCols = VARIO_COLS[src], dstCols = VARIO_COLS[dst];
  const inputRows = getTableRows('vario-input-tbody');
  const outRows = inputRows.map(([a, b, c]) => {
    const R = getVarioMatrix(src, a, b, c);
    return decompose(dst, R).map(v => +v.toFixed ? v : 0);
  });
  _varioResultData = { srcCols, dstCols, inputRows, outRows };
  buildResultTable('vario-result-in',  srcCols, inputRows);
  buildResultTable('vario-result-out', dstCols, outRows);
  document.getElementById('vario-result-card').classList.remove('d-none');
}

function downloadVarioResult() {
  if (!_varioResultData) return;
  const { srcCols, dstCols, inputRows, outRows } = _varioResultData;
  downloadCSV(inputRows.map((r,i) => [...r, ...outRows[i]]),
    [...srcCols, ...dstCols], 'variograma_convertido.csv');
}

// ═══════════════════════════════════════════════════════════════════════════
// ── BLOCOS ──
// ═══════════════════════════════════════════════════════════════════════════

let _blkResultData = null;

function blkSrc() { return document.getElementById('blk-src').value; }
function blkDst() { return document.getElementById('blk-dst').value; }

function initBlocos() {
  renderBlkInputFields();
  buildBlkTable();
  document.getElementById('blk-src').onchange = () => { renderBlkInputFields(); buildBlkTable(); };
}

function renderBlkInputFields() {
  const src  = blkSrc();
  const cols = BLOCK_COLS[src];
  const fld  = document.getElementById('blk-input-fields');
  fld.innerHTML =
    numInput('blk-a', cols[0], -360, 360, 0.1, 0) +
    numInput('blk-b', cols[1], 0, 90, 0.1, 0) +
    numInput('blk-c', cols[2], -360, 360, 0.1, 0) +
    `<button class="btn btn-convert w-100 mt-1" onclick="convertBlkSingle()">🔄 Converter</button>`;
}

function buildBlkTable() {
  const src  = blkSrc();
  const cols = BLOCK_COLS[src];
  buildTableHeader('blk-input-thead', cols);
  document.getElementById('blk-input-tbody').innerHTML = '';
  [[0,0,0],[45,30,15],[90,45,30]].forEach(v => addTableRow('blk-input-tbody', cols, v));
}

function blkAddRow()    { addTableRow('blk-input-tbody', BLOCK_COLS[blkSrc()]); }
function blkLoadExample() { buildBlkTable(); }
function blkPasteCSV() { openCSVModal(rows => {
  document.getElementById('blk-input-tbody').innerHTML = '';
  rows.forEach(r => addTableRow('blk-input-tbody', BLOCK_COLS[blkSrc()], r));
}); }

function convertBlkSingle() {
  const src = blkSrc(), dst = blkDst();
  const a = getVal('blk-a'), b = getVal('blk-b'), c = getVal('blk-c');
  const R = getBlockMatrix(src, a, b, c);
  const [v1, v2, v3] = decomposeBlock(dst, R);
  const R_dst = getBlockMatrix(dst, v1, v2, v3);

  const dstCols = BLOCK_COLS[dst];
  renderMetrics('blk-metrics', [[dstCols[0], v1],[dstCols[1], v2],[dstCols[2], v3]]);
  plotBlock('block-plot', R, R_dst, src, dst);
  document.getElementById('blk-isatis-warn').classList.toggle('d-none', dst !== 'Isatis.neo');
}

function convertBlkTable() {
  const src = blkSrc(), dst = blkDst();
  const srcCols = BLOCK_COLS[src], dstCols = BLOCK_COLS[dst];
  const inputRows = getTableRows('blk-input-tbody');
  const outRows = inputRows.map(([a, b, c]) => decomposeBlock(dst, getBlockMatrix(src, a, b, c)));
  _blkResultData = { srcCols, dstCols, inputRows, outRows };
  buildResultTable('blk-result-in',  srcCols, inputRows);
  buildResultTable('blk-result-out', dstCols, outRows);
  document.getElementById('blk-result-card').classList.remove('d-none');
}

function downloadBlkResult() {
  if (!_blkResultData) return;
  const { srcCols, dstCols, inputRows, outRows } = _blkResultData;
  downloadCSV(inputRows.map((r,i) => [...r, ...outRows[i]]),
    [...srcCols, ...dstCols], 'blocos_convertidos.csv');
}

// ═══════════════════════════════════════════════════════════════════════════
// ── COORDENADAS ──
// ═══════════════════════════════════════════════════════════════════════════

let _coordResultData = null;

function initCoords() {
  coordLoadExample();
  document.getElementById('coord-src').onchange = updateCoordZHeader;
  updateCoordZHeader();
}

function updateCoordZHeader() {
  const src = document.getElementById('coord-src').value;
  const lbl = src.includes('sondagens') ? 'Z (profundidade)' : 'Z (cota)';
  document.getElementById('coord-z-header').textContent = lbl;
}

function coordAddRow() {
  const tbody = document.getElementById('coord-tbody');
  const tr = document.createElement('tr');
  tr.innerHTML = `<td><input type="number" step=".001" value="0"></td>
    <td><input type="number" step=".001" value="0"></td>
    <td><input type="number" step=".001" value="0"></td>
    <td><button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="this.closest('tr').remove()">✕</button></td>`;
  tbody.appendChild(tr);
}

function coordLoadExample() {
  const tbody = document.getElementById('coord-tbody');
  tbody.innerHTML = '';
  [[350000,7500000,800],[350010,7500015,785],[350020,7500030,770]].forEach(v => {
    const tr = document.createElement('tr');
    tr.innerHTML = v.map(val => `<td><input type="number" step=".001" value="${val}"></td>`).join('') +
      `<td><button class="btn btn-sm btn-outline-danger py-0 px-2" onclick="this.closest('tr').remove()">✕</button></td>`;
    tbody.appendChild(tr);
  });
}

function _runCoordConvert(rows) {
  const src      = document.getElementById('coord-src').value;
  const flipZ    = src.includes('sondagens');
  const outRows  = rows.map(([x, y, z]) => [x, y, flipZ ? -z : z]);
  _coordResultData = { rows, outRows, flipZ };
  buildResultTable('coord-result-in',  ['X', 'Y', flipZ ? 'Z (profundidade)' : 'Z'], rows);
  buildResultTable('coord-result-out', ['X', 'Y', 'Z (cota)'], outRows);
  document.getElementById('coord-result-card').classList.remove('d-none');
  document.getElementById('coord-flip-notice').classList.toggle('d-none', !flipZ);
}

function convertCoords() {
  const rows = [];
  document.querySelectorAll('#coord-tbody tr').forEach(tr => {
    const inputs = tr.querySelectorAll('input');
    rows.push([...inputs].map(i => parseFloat(i.value)||0));
  });
  _runCoordConvert(rows);
}

function convertCoordsCSV() {
  const text = document.getElementById('coord-csv-text').value.trim();
  if (!text) return;
  const { headers, rows } = parseCSV(text);
  const xiX = headers.findIndex(h => /^x$/i.test(h));
  const xiY = headers.findIndex(h => /^y$/i.test(h));
  const xiZ = headers.findIndex(h => /^z/i.test(h));
  if (xiX < 0 || xiY < 0 || xiZ < 0) {
    alert('CSV deve ter colunas X, Y e Z (ou Z_profundidade).'); return;
  }
  _runCoordConvert(rows.map(r => [parseFloat(r[xiX])||0, parseFloat(r[xiY])||0, parseFloat(r[xiZ])||0]));
}

function downloadCoordsResult() {
  if (!_coordResultData) return;
  const { rows, outRows, flipZ } = _coordResultData;
  const hIn  = ['X', 'Y', flipZ ? 'Z_profundidade' : 'Z'];
  const hOut = ['X_out', 'Y_out', 'Z_cota'];
  downloadCSV(rows.map((r,i) => [...r, ...outRows[i]]), [...hIn, ...hOut], 'coordenadas_convertidas.csv');
}

// ═══════════════════════════════════════════════════════════════════════════
// ── Modal de CSV ──
// ═══════════════════════════════════════════════════════════════════════════

let _csvCallback = null;

function openCSVModal(callback) {
  _csvCallback = callback;
  document.getElementById('csv-paste-area').value = '';
  new bootstrap.Modal(document.getElementById('csvModal')).show();
}

document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('csv-paste-confirm').addEventListener('click', () => {
    const text = document.getElementById('csv-paste-area').value;
    const { rows } = parseCSV(text);
    if (_csvCallback && rows.length) _csvCallback(rows);
    bootstrap.Modal.getInstance(document.getElementById('csvModal')).hide();
  });
  // Inicializar a página home
  initDiscs();
});
