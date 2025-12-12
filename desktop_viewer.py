import config
from main import app
import csv
import ostime import datetime
import sqlite3
import timeQtCore import QTimer, Qt
import jsonQtWidgets import (
from flask import Response, render_template_stringt, QHBoxLayout,
    QPushButton, QLabel, QSpinBox, QFileDialog, QTextEdit
from .ui import INDEX_HTML
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# DB path (same place que le projet) — ajuste si nécessaire
DB_PATH = os.path.join(os.path.dirname(__file__), "esp32_data.db")
DB_PATH = os.path.join(os.path.dirname(__file__), 'esp32_data.db')
def get_max_rowid():
    if not os.path.exists(DB_PATH):or "real-time" updates
        return 0
    try:h_history(limit=500):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT MAX(rowid) FROM sensor_data;")
        r = cur.fetchone()
        conn.close()ECT rowid,timestamp,x,y,z FROM sensor_data ORDER BY rowid DESC LIMIT ?;", (limit,))
        return r[0] or 0)
    except Exception:
        return 0reversed(rows))  # ascending time
    return [{"rowid": r[0], "timestamp": r[1], "x": r[2], "y": r[3], "z": r[4]} for r in rows]
def fetch_rows_since(last):
    if not os.path.exists(DB_PATH):
        return []self, parent=None):
    try:fig = Figure(figsize=(8,4), tight_layout=True)
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()nt)
        cur.execute("SELECT rowid,id,type,timestamp,x,y,z,raw FROM sensor_data WHERE rowid > ? ORDER BY rowid ASC;", (last,))
        rows = cur.fetchall()x.plot([], [], label='X', color='r')
        conn.close() = self.ax.plot([], [], label='Y', color='g')
        out = []e_z, = self.ax.plot([], [], label='Z', color='b')
        for r in rows:(loc='upper right')
            rowid,id_,type_,timestamp,x,y,z,raw = r
            try:set_ylabel('accel')
                raw_json = json.loads(raw)
            except Exception:
                raw_json = rawstamps, xs, ys, zs):
            out.append({s:
                "rowid": rowid, "id": id_, "type": type_, "timestamp": timestamp,
                "x": x, "y": y, "z": z, "raw": raw_json
            })lf.ax.set_xlabel('time')
        return outx.set_ylabel('accel')
    except Exception:()
        return []n
        # map timestamps to short labels
def event_stream(poll_interval=0.15): 'T' in t else t for t in timestamps]
    """SSE generator: poll DB for new rows and yield measurement events."""
    last = get_max_rowid()ta(idx, xs)
    # initial connected eventidx, ys)
    yield f"event: connected\ndata: {json.dumps({'last_rowid': last})}\n\n"
    try:self.ax.set_xlim(0, max(1, len(labels)-1))
        while True:min(xs), min(ys), min(zs)) if xs and ys and zs else -1
            current = get_max_rowid()max(zs)) if xs and ys and zs else 1
            if current > last: ymin) * 0.1)
                rows = fetch_rows_since(last)ad)
                for r in rows:
                    yield f"event: measurement\ndata: {json.dumps(r, default=str)}\n\n"
                    last = r["rowid"](0, len(labels), step)))
            time.sleep(poll_interval)ls[i] for i in range(0, len(labels), step)], rotation=30, ha='right', fontsize=8)
    except GeneratorExit:
        return
    except Exception:nWindow):
        time.sleep(poll_interval)
        return).__init__()
        self.setWindowTitle("ESP32 Desktop Viewer")
@app.route('/')size(1000, 700)
def index():
    return render_template_string(INDEX_HTML)
        self.setCentralWidget(central)
@app.route('/events')xLayout()
def events():al.setLayout(layout)
    return Response(event_stream(), mimetype='text/event-stream')
        # controls
if __name__ == "__main__" and __package__ is None:
    import sys, osLayout(ctrl)
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
        ctrl.addWidget(QLabel("History points:"))
import oself.spin_history = QSpinBox()
import sqlite3pin_history.setRange(10, 5000)
import timef.spin_history.setValue(500)
import jsonl.addWidget(self.spin_history)
from flask import Response, render_template_string
        self.btn_reload = QPushButton("Charger")
from src.ui import INDEX_HTMLtn_reload)
from src.api.routes import api_bptton("Exporter CSV")
        ctrl.addWidget(self.btn_export)
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "esp32_data.db")
        ctrl.addStretch()
def get_max_rowid():label = QLabel("Status: idle")
    if not os.path.exists(DB_PATH):label)
        return 0
    try:# plot
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()lf.plot)
        cur.execute("SELECT MAX(rowid) FROM sensor_data;")
        r = cur.fetchone()
        conn.close()TextEdit()
        return r[0] or 0Only(True)
    except Exception:aximumHeight(200)
        return 0ddWidget(self.log)

def fetch_rows_since(last):
    if not os.path.exists(DB_PATH):
        return []
    try:# connections
        conn = sqlite3.connect(DB_PATH)(self.load_history)
        cur = conn.cursor()cked.connect(self.export_csv)
        cur.execute("SELECT rowid,id,type,timestamp,x,y,z,raw FROM sensor_data WHERE rowid > ? ORDER BY rowid ASC;", (last,))
        rows = cur.fetchall()
        conn.close() QTimer()
        out = []er.setInterval(POLL_MS)
        for r in rows:eout.connect(self.poll_new)
            rowid,id_,type_,timestamp,x,y,z,raw = r
            try:
                raw_json = json.loads(raw)
            except Exception:
                raw_json = raw
            out.append({ text):
                "rowid": rowid, "id": id_, "type": type_, "timestamp": timestamp,
                "x": x, "y": y, "z": z, "raw": raw_json
            })og.ensureCursorVisible()
        return out
    except Exception:self):
        return []spin_history.value()
        rows = fetch_history(limit=n)
def event_stream(poll_interval=0.15):
    """SSE generator: poll DB for new rows and yield measurement events."""
    last = get_max_rowid()te_plot([], [], [], [])
    # initial connected event 0
    yield f"event: connected\ndata: {json.dumps({'last_rowid': last})}\n\n"
    try:timestamps = [r['timestamp'] or str(r['rowid']) for r in rows]
        while True:] for r in rows]
            current = get_max_rowid()
            if current > last:rows]
                rows = fetch_rows_since(last) ys, zs)
                for r in rows:[-1]['rowid']
                    yield f"event: measurement\ndata: {json.dumps(r, default=str)}\n\n"})")
                    last = r["rowid"]ded {len(rows)} points (last id {self.last_rowid})")
            time.sleep(poll_interval)
    except GeneratorExit:
        returnh rows since last_rowid (small limit)
    except Exception:h.exists(DB_PATH):
        time.sleep(poll_interval)
        return sqlite3.connect(DB_PATH)
        cur = conn.cursor()
def setup_routes(app):ELECT rowid,timestamp,x,y,z FROM sensor_data WHERE rowid > ? ORDER BY rowid ASC LIMIT 1000;", (self.last_rowid,))
    """Configure routes sur l'app Flask."""
    app.register_blueprint(api_bp)
        if not rows:
    @app.route('/')
    def index(): to current plot data
        return render_template_string(INDEX_HTML)
        current_labels = list(self.plot.ax.get_xticklabels())
    @app.route('/events')ent history to redraw (simpler)
    def events():elf.spin_history.value()
        return Response(event_stream(), mimetype='text/event-stream')
        timestamps = [r['timestamp'] or str(r['rowid']) for r in history]
        xs = [r['x'] for r in history]
        ys = [r['y'] for r in history]
        zs = [r['z'] for r in history]
        self.plot.update_plot(timestamps, xs, ys, zs)
        self.last_rowid = history[-1]['rowid'] if history else self.last_rowid
        # log new rows
        for r in rows:
            self.append_log(f"New row id={r[0]} x={r[2]} y={r[3]} z={r[4]}")

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Exporter CSV", "esp32_export.csv", "CSV files (*.csv)")
        if not path:
            return
        # export all rows
        if not os.path.exists(DB_PATH):
            self.append_log("DB not found, export aborted.")
            return
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT rowid,id,type,timestamp,x,y,z,raw FROM sensor_data ORDER BY rowid ASC;")
        rows = cur.fetchall()
        conn.close()
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(['rowid','id','type','timestamp','x','y','z','raw'])
                for r in rows:
                    w.writerow(r)
            self.append_log(f"Exporté {len(rows)} lignes vers {path}")
        except Exception as e:
            self.append_log(f"Export error: {e}")

def main():
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()