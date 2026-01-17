INDEX_HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>ESP32 — Live</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hammerjs@2.0.8"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
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
    <span id="evtCount" style="margin-left:12px;color:#666">events: 0</span>
    <button id="pauseBtn">Pause</button>
    <button id="clearLog">Clear</button>
    <button id="resetZoom">Reset Zoom</button>
  </div>
</div>

<div class="card">
  <div class="kv"><span class="label">Dernière lecture :</span><span id="ts" class="value">—</span></div>
  <div class="kv"><span class="label">Device:</span><span id="dev" class="value">—</span></div>
  <div class="kv"><span class="label">Type:</span><span id="type" class="value">—</span></div>
  <div style="display:flex;gap:12px;margin-top:8px;align-items:center;">
    <div id="accelValues" style="display:flex;gap:12px;align-items:center;">
      <div><span class="label">X</span><div id="x" class="value">—</div></div>
      <div><span class="label">Y</span><div id="y" class="value">—</div></div>
      <div><span class="label">Z</span><div id="z" class="value">—</div></div>
    </div>
    <div id="bpmContainer" style="display:none;margin-left:12px"><div><span class="label">BPM</span><div id="bpm" class="value">—</div></div></div>
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
      <label>Valeur affichée:
        <select id="ecgValueSelector" style="padding:4px;">
          <option value="bpm">BPM (Battements/min)</option>
          <option value="ir">IR (Signal infrarouge)</option>
          <option value="ecg">ECG (Signal brut)</option>
        </select>
      </label>
      <label style="margin-left:16px;">Max points: <input id="maxPointsECG" type="number" value="500" min="10" max="2000" style="width:80px"></label>
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

<div class="card">
  <h4>Historique ECG</h4>
  <table class="table" id="ecgTable">
    <thead><tr><th>#</th><th>ts</th><th>id</th><th>bpm</th><th>ir</th><th>ecg</th></tr></thead>
    <tbody></tbody>
  </table>
</div>

<script>
let paused = false;
const statusEl = document.getElementById('status');
const evtCountEl = document.getElementById('evtCount');
let evtCounter = 0;
const tsEl = document.getElementById('ts');
const devEl = document.getElementById('dev');
const typeEl = document.getElementById('type');
const xEl = document.getElementById('x');
const yEl = document.getElementById('y');
const zEl = document.getElementById('z');
const accelValuesEl = document.getElementById('accelValues');
const bpmContainer = document.getElementById('bpmContainer');
const bpmEl = document.getElementById('bpm');
const logEl = document.getElementById('log');
const tableBody = document.querySelector('#historyTable tbody');
const ecgTableBody = document.querySelector('#ecgTable tbody');
const maxPointsInput = document.getElementById('maxPoints');
const maxPointsECGInput = document.getElementById('maxPointsECG');
const ecgValueSelector = document.getElementById('ecgValueSelector');
let selectedECGValue = 'bpm';

document.getElementById('pauseBtn').addEventListener('click', ()=>{
  paused = !paused;
  document.getElementById('pauseBtn').textContent = paused ? 'Resume' : 'Pause';
});

document.getElementById('clearLog').addEventListener('click', ()=>{ 
  // Vider le log
  logEl.textContent='';
  
  // Vider le graphique accéléromètre
  chart.data.labels = [];
  chart.data.datasets.forEach(ds => ds.data = []);
  chart.update('none');
  
  // Vider le graphique ECG
  ecgChart.data.labels = [];
  ecgChart.data.datasets.forEach(ds => ds.data = []);
  ecgChart.update('none');
  
  // Vider les tableaux
  if (accelTableBody) accelTableBody.innerHTML = '';
  if (ecgTableBody) ecgTableBody.innerHTML = '';
  
  prependLog('Toutes les données effacées');
});

document.getElementById('resetZoom').addEventListener('click', ()=>{
  chart.resetZoom();
  ecgChart.resetZoom();
  prependLog('Zoom réinitialisé');
});

ecgValueSelector.addEventListener('change', ()=>{
  selectedECGValue = ecgValueSelector.value;
  // Basculer la visibilité des datasets
  const datasetMap = { 'bpm': 0, 'ir': 1, 'ecg': 2 };
  const selectedIndex = datasetMap[selectedECGValue];
  ecgChart.data.datasets.forEach((ds, idx) => {
    ds.hidden = (idx !== selectedIndex);
  });
  // Adapter l'échelle Y selon le dataset sélectionné
  ecgChart.options.scales.y.min = datasetLimits[selectedIndex].min;
  ecgChart.options.scales.y.max = datasetLimits[selectedIndex].max;
  ecgChart.update('none');
});

const ctx = document.getElementById('chart').getContext('2d');
let maxPoints = parseInt(maxPointsInput.value) || 200;

const chart = new Chart(ctx, {
  type: 'line',
  data: { labels: [], datasets: [
    { label: 'X', data: [], borderColor: 'rgb(255,99,132)', tension:0.2 },
    { label: 'Y', data: [], borderColor: 'rgb(54,162,235)', tension:0.2 },
    { label: 'Z', data: [], borderColor: 'rgb(75,192,192)', tension:0.2 }
  ]},
  options: {
    animation:false,
    responsive:true,
    scales:{
      x:{ display:true, title:{display:true, text:'Time'}, ticks:{ maxRotation:45, autoSkip:true, maxTicksLimit:10 } }
    },
    plugins: {
      zoom: {
        pan: {
          enabled: true,
          mode: 'xy',
          modifierKey: 'ctrl'
        },
        zoom: {
          wheel: {
            enabled: true,
            speed: 0.1
          },
          drag: {
            enabled: true,
            backgroundColor: 'rgba(54,162,235,0.3)'
          },
          pinch: {
            enabled: true
          },
          mode: 'xy'
        },
        limits: {
          x: {min: 'original', max: 'original'},
          y: {min: 'original', max: 'original'}
        }
      }
    }
  }
});

const ctxECG = document.getElementById('ecgChart').getContext('2d');
let maxPointsECG = parseInt(maxPointsECGInput.value) || 500;

// Limites pour chaque type de donnée
const datasetLimits = {
  0: { min: 0, max: 150 },           // BPM: 0-150
  1: { min: 0, max: 300000 },        // IR: 0-300000
  2: { min: -200000, max: 200000 }   // ECG: -200000 à +200000
};

const ecgChart = new Chart(ctxECG, {
  type: 'line',
  data: { labels: [], datasets: [
    { label: 'BPM', data: [], borderColor: 'rgb(220,53,69)', borderWidth:2, fill:false, tension:0.1, hidden: false },
    { label: 'IR', data: [], borderColor: 'rgb(255,193,7)', borderWidth:2, fill:false, tension:0.1, hidden: true },
    { label: 'ECG', data: [], borderColor: 'rgb(76,175,80)', borderWidth:2, fill:false, tension:0.1, hidden: true }
  ]},
  options: {
    animation:false,
    responsive:true,
    scales:{
      y:{ min:0, max:150 },
      x:{ display:true, title:{display:true, text:'Time'}, ticks:{ maxRotation:45, autoSkip:true, maxTicksLimit:20 } }
    },
    plugins: {
      zoom: {
        pan: {
          enabled: true,
          mode: 'xy',
          modifierKey: 'ctrl'
        },
        zoom: {
          wheel: {
            enabled: true,
            speed: 0.1
          },
          drag: {
            enabled: true,
            backgroundColor: 'rgba(220,53,69,0.3)'
          },
          pinch: {
            enabled: true
          },
          mode: 'xy'
        },
        limits: {
          x: {min: 'original', max: 'original'},
          y: {min: 'original', max: 'original'}
        }
      }
    }
  }
});

function prependLog(text){
  const now = new Date().toISOString();
  logEl.textContent = now + ' ' + text + '\\n' + logEl.textContent;
  if(logEl.textContent.length>10000) logEl.textContent = logEl.textContent.slice(0,10000);
}

function pushMeasurement(m){
  if(paused) return;
  evtCounter += 1;
  if (evtCountEl) evtCountEl.textContent = 'events: ' + evtCounter; 
  tsEl.textContent = m.timestamp ? new Date(m.timestamp).toLocaleString() : '-';
  devEl.textContent = m.id || '-';
  typeEl.textContent = m.type || '-';

  // build a short time label for chart X axis
  const label = m.timestamp ? new Date(m.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString();
  const t = (m.type || '').toLowerCase();

  // For ECG events, do not display them as accelerometer X/Y/Z; show BPM instead
  if (t === 'ecg') {
    // Utiliser directement les champs bpm, ir, ecg
    const bpm = (m.bpm !== undefined && m.bpm !== null) ? m.bpm : 
                ((m.raw && m.raw.bpm !== undefined) ? m.raw.bpm : '-');
    const ir = (m.ir !== undefined && m.ir !== null) ? m.ir : 
               ((m.raw && m.raw.ir !== undefined) ? m.raw.ir : null);
    const ecg = (m.ecg !== undefined && m.ecg !== null) ? m.ecg : 
                ((m.raw && m.raw.ecg !== undefined) ? m.raw.ecg : null);
    
    if (bpmContainer) { 
      bpmContainer.style.display = ''; 
      bpmEl.textContent = bpm !== '-' ? (bpm + ' bpm') : '-'; 
    }
    if (accelValuesEl) accelValuesEl.style.display = 'none';
    xEl.textContent = '-';
    yEl.textContent = '-';
    zEl.textContent = '-';
  } else {
    if (bpmContainer) bpmContainer.style.display = 'none';
    if (accelValuesEl) accelValuesEl.style.display = 'flex';
    xEl.textContent = m.x;
    yEl.textContent = m.y;
    zEl.textContent = m.z;
  }

  // Only push to accelerometer chart when data is not ECG
  if (t !== 'ecg' && m.x !== undefined && m.y !== undefined && m.z !== undefined) {
    chart.data.labels.push(label);
    chart.data.datasets[0].data.push(m.x);
    chart.data.datasets[1].data.push(m.y);
    chart.data.datasets[2].data.push(m.z);
    while(chart.data.labels.length > maxPoints){
      chart.data.labels.shift();
      chart.data.datasets.forEach(ds=>ds.data.shift());
    }
    chart.update('none');
  }

  let ecgValue = null;
  if (t === 'ecg') {
    // Utiliser directement les champs bpm, ir, ecg de la mesure
    const bpmValue = (m.bpm !== undefined && m.bpm !== null) ? m.bpm : 
                     ((m.raw && m.raw.bpm !== undefined) ? m.raw.bpm : null);
    const irValue = (m.ir !== undefined && m.ir !== null) ? m.ir : 
                    ((m.raw && m.raw.ir !== undefined) ? m.raw.ir : null);
    const ecgValue = (m.ecg !== undefined && m.ecg !== null) ? m.ecg : 
                     ((m.raw && m.raw.ecg !== undefined) ? m.raw.ecg : null);

    // Ajouter BPM au dataset 0
    if(bpmValue !== null && bpmValue !== undefined){
      ecgChart.data.labels.push(label);
      ecgChart.data.datasets[0].data.push(bpmValue);
      
      // Ajouter IR au dataset 1 (synchro)
      if(irValue !== null && irValue !== undefined){
        ecgChart.data.datasets[1].data.push(irValue);
      } else {
        ecgChart.data.datasets[1].data.push(null);
      }
      
      // Ajouter ECG au dataset 2 (synchro)
      if(ecgValue !== null && ecgValue !== undefined){
        ecgChart.data.datasets[2].data.push(ecgValue);
      } else {
        ecgChart.data.datasets[2].data.push(null);
      }
      
      while(ecgChart.data.labels.length > maxPointsECG){
        ecgChart.data.labels.shift();
        ecgChart.data.datasets.forEach(ds=>ds.data.shift());
      }
      ecgChart.update('none');
    }
  }
  // Ajout d'une ligne dans la table
  const tr = document.createElement('tr');
  if (t === 'ecg') {
    // Pour les lignes ECG, afficher bpm/ir/ecg dans le tableau ECG
    const bpmCell = (m.bpm !== undefined && m.bpm !== null) ? (m.bpm + ' bpm') : 
                    ((m.raw && m.raw.bpm !== undefined) ? (m.raw.bpm + ' bpm') : '-');
    const irCell = (m.ir !== undefined && m.ir !== null) ? m.ir : 
                   ((m.raw && m.raw.ir !== undefined) ? m.raw.ir : '-');
    const ecgCell = (m.ecg !== undefined && m.ecg !== null) ? m.ecg : 
                    ((m.raw && m.raw.ecg !== undefined) ? m.raw.ecg : '-');
    
    tr.innerHTML = `<td>${m.rowid||''}</td><td>${m.timestamp||''}</td><td>${m.id||''}</td><td>${bpmCell}</td><td>${irCell}</td><td>${ecgCell}</td>`;
    if (ecgTableBody) {
      ecgTableBody.insertBefore(tr, ecgTableBody.firstChild);
      while(ecgTableBody.children.length > 500) ecgTableBody.removeChild(ecgTableBody.lastChild);
    }
    prependLog(`id=${m.id||'-'} type=${m.type} bpm=${bpmCell} ir=${irCell} ecg=${ecgCell}`);
  } else {
    tr.innerHTML = `<td>${m.rowid||''}</td><td>${m.timestamp||''}</td><td>${m.id||''}</td><td>${m.x}</td><td>${m.y}</td><td>${m.z}</td>`;
    if (accelTableBody) {
      accelTableBody.insertBefore(tr, accelTableBody.firstChild);
      while(accelTableBody.children.length > 500) accelTableBody.removeChild(accelTableBody.lastChild);
    }
    prependLog(`id=${m.id||'-'} type=${m.type} x=${m.x} y=${m.y} z=${m.z}`);
  }
}

function pushECGSamples(samples){
  const decimation = Math.max(1, Math.floor(samples.length / 100));
  for(let i=0;i<samples.length;i+=decimation){
    const v = samples[i];
    ecgChart.data.labels.push(new Date().toLocaleTimeString());
    ecgChart.data.datasets[0].data.push(v);
    if(ecgChart.data.labels.length > maxPointsECG){
      ecgChart.data.labels.shift();
      ecgChart.data.datasets[0].data.shift();
    }
  }
  ecgChart.update('none');
}

let es = null;
function startEventSource(){
  if(es) try{ es.close(); }catch(e){}
  es = new EventSource('/events');
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
  es.onopen = ()=>{ statusEl.textContent = 'connected'; };
  es.onerror = ()=> {
    statusEl.textContent = 'disconnected';
    prependLog('SSE error');
    try{ es.close(); }catch(e){}
    // reconnect after delay
    setTimeout(()=>{ prependLog('reconnecting SSE...'); startEventSource(); }, 2000);
  };
}
startEventSource();

maxPointsInput.addEventListener('change', ()=>{ maxPoints = parseInt(maxPointsInput.value) || 200; });
maxPointsECGInput.addEventListener('change', ()=>{ maxPointsECG = parseInt(maxPointsECGInput.value) || 500; });
</script>
</body>
</html>
"""