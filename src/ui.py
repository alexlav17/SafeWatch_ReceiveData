INDEX_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>ESP32 — Live</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body{font-family:Arial,Helvetica,sans-serif;margin:18px;color:#222}
.header{display:flex;align-items:center;justify-content:space-between}
.card{border:1px solid #ddd;padding:12px;border-radius:6px;margin-top:12px;background:#fff}
.kv{margin:6px 0}
.label{font-weight:700;margin-right:8px}
.value{color:#007acc}
#log{font-family:monospace;white-space:pre-wrap;max-height:160px;overflow:auto;background:#f7f7f7;padding:8px}
.table{width:100%;border-collapse:collapse;margin-top:8px}
.table th,.table td{border:1px solid #eee;padding:6px;font-size:13px}
.controls{margin-top:8px}
button{padding:6px 10px;border-radius:4px;border:1px solid #bbb;background:#f4f4f4}
.charts-container{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:1200px){.charts-container{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="header">
  <h2>ESP32 — Mesures (live)</h2>
  <div>
    <span id="status">connecting...</span>
    <button id="pauseBtn">Pause</button>
    <button id="clearLog">Clear</button>
  </div>
</div>

<div class="card">
  <div class="kv"><span class="label">Dernière lecture :</span><span id="ts" class="value">—</span></div>
  <div class="kv"><span class="label">Device:</span><span id="dev" class="value">—</span></div>
  <div class="kv"><span class="label">Type:</span><span id="type" class="value">—</span></div>
  <div style="display:flex;gap:12px;margin-top:8px">
    <div><span class="label">X</span><div id="x" class="value">—</div></div>
    <div><span class="label">Y</span><div id="y" class="value">—</div></div>
    <div><span class="label">Z</span><div id="z" class="value">—</div></div>
  </div>
</div>

<div class="charts-container">
  <div class="card">
    <h4>Graphique 3D (Accéléromètre)</h4>
    <canvas id="chart" height="120"></canvas>
    <div class="controls">
      <label>Max points: <input id="maxPoints" type="number" value="200" min="10" max="2000" style="width:80px"></label>
    </div>
  </div>

  <div class="card">
    <h4>ECG (Cardiogramme)</h4>
    <canvas id="ecgChart" height="120"></canvas>
    <div class="controls">
      <label>Max points: <input id="maxPointsECG" type="number" value="500" min="10" max="2000" style="width:80px"></label>
    </div>
  </div>
</div>

<div class="card">
  <h4>Historique récent</h4>
  <div id="log">waiting for data...</div>
  <table class="table" id="historyTable">
    <thead><tr><th>#</th><th>ts</th><th>id</th><th>x</th><th>y</th><th>z</th></tr></thead>
    <tbody></tbody>
  </table>
</div>

<script>
let paused = false;
const statusEl = document.getElementById('status');
const tsEl = document.getElementById('ts');
const devEl = document.getElementById('dev');
const typeEl = document.getElementById('type');
const xEl = document.getElementById('x');
const yEl = document.getElementById('y');
const zEl = document.getElementById('z');
const logEl = document.getElementById('log');
const tableBody = document.querySelector('#historyTable tbody');
const maxPointsInput = document.getElementById('maxPoints');
const maxPointsECGInput = document.getElementById('maxPointsECG');

document.getElementById('pauseBtn').addEventListener('click', ()=>{
  paused = !paused;
  document.getElementById('pauseBtn').textContent = paused ? 'Resume' : 'Pause';
});

document.getElementById('clearLog').addEventListener('click', ()=>{ logEl.textContent=''; });

const ctx = document.getElementById('chart').getContext('2d');
let maxPoints = parseInt(maxPointsInput.value) || 200;

const chart = new Chart(ctx, {
  type: 'line',
  data: { labels: [], datasets: [
    { label: 'X', data: [], borderColor: 'rgb(255,99,132)', tension:0.2 },
    { label: 'Y', data: [], borderColor: 'rgb(54,162,235)', tension:0.2 },
    { label: 'Z', data: [], borderColor: 'rgb(75,192,192)', tension:0.2 }
  ]},
  options: { animation:false, responsive:true, scales:{ x:{display:false} } }
});

const ctxECG = document.getElementById('ecgChart').getContext('2d');
let maxPointsECG = parseInt(maxPointsECGInput.value) || 500;

const ecgChart = new Chart(ctxECG, {
  type: 'line',
  data: { labels: [], datasets: [
    { label: 'BPM / Signal ECG', data: [], borderColor: 'rgb(220,53,69)', borderWidth:2, fill:false, tension:0.1 }
  ]},
  options: { animation:false, responsive:true, scales:{ y:{ min:0, max:200 }, x:{display:false} } }
});

function prependLog(text){
  const now = new Date().toISOString();
  logEl.textContent = now + ' ' + text + '\\n' + logEl.textContent;
  if(logEl.textContent.length>10000) logEl.textContent = logEl.textContent.slice(0,10000);
}

function pushMeasurement(m){
  if(paused) return;
  tsEl.textContent = m.timestamp || '-';
  devEl.textContent = m.id || '-';
  typeEl.textContent = m.type || '-';
  xEl.textContent = m.x;
  yEl.textContent = m.y;
  zEl.textContent = m.z;
  
  chart.data.labels.push(m.timestamp || m.rowid);
  chart.data.datasets[0].data.push(m.x);
  chart.data.datasets[1].data.push(m.y);
  chart.data.datasets[2].data.push(m.z);
  while(chart.data.labels.length > maxPoints){
    chart.data.labels.shift();
    chart.data.datasets.forEach(ds=>ds.data.shift());
  }
  chart.update('none');
  
  let ecgValue = null;
  const t = (m.type || '').toLowerCase();
  if (t === 'ecg') {
    if (m.raw && Array.isArray(m.raw.ecg)) {
      pushECGSamples(m.raw.ecg);
    } else if (m.raw && (m.raw.bpm !== undefined)) {
      ecgValue = m.raw.bpm;
    } else if (typeof m.x === 'number') {
      ecgValue = m.x;
    }
  }
  
  if(ecgValue !== null && ecgValue !== undefined){
    ecgChart.data.labels.push(m.timestamp || m.rowid);
    ecgChart.data.datasets[0].data.push(ecgValue);
    while(ecgChart.data.labels.length > maxPointsECG){
      ecgChart.data.labels.shift();
      ecgChart.data.datasets[0].data.shift();
    }
    ecgChart.update('none');
  }
  
  const tr = document.createElement('tr');
  tr.innerHTML = `<td>${m.rowid}</td><td>${m.timestamp||''}</td><td>${m.id||''}</td><td>${m.x}</td><td>${m.y}</td><td>${m.z}</td>`;
  tableBody.insertBefore(tr, tableBody.firstChild);
  while(tableBody.children.length > 200) tableBody.removeChild(tableBody.lastChild);
  prependLog(`id=${m.id||'-'} type=${m.type} x=${m.x} y=${m.y} z=${m.z}`);
}

function pushECGSamples(samples){
  const decimation = Math.max(1, Math.floor(samples.length / 100));
  for(let i=0;i<samples.length;i+=decimation){
    const v = samples[i];
    ecgChart.data.labels.push(new Date().toISOString());
    ecgChart.data.datasets[0].data.push(v);
    if(ecgChart.data.labels.length > maxPointsECG){
      ecgChart.data.labels.shift();
      ecgChart.data.datasets[0].data.shift();
    }
  }
  ecgChart.update('none');
}

const es = new EventSource('/events');
es.addEventListener('connected', e=>{
  const d = JSON.parse(e.data);
  statusEl.textContent = 'connected (last=' + d.last_rowid + ')';
  prependLog('connected, last=' + d.last_rowid);
});
es.addEventListener('measurement', e=>{
  try{
    const m = JSON.parse(e.data);
    pushMeasurement(m);
    statusEl.textContent = 'live';
  }catch(err){
    prependLog('parse error');
  }
});
es.onerror = ()=> { statusEl.textContent = 'disconnected'; prependLog('SSE error'); };

maxPointsInput.addEventListener('change', ()=>{ maxPoints = parseInt(maxPointsInput.value) || 200; });
maxPointsECGInput.addEventListener('change', ()=>{ maxPointsECG = parseInt(maxPointsECGInput.value) || 500; });
</script>
</body>
</html>
"""