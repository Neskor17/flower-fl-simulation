"""
🌸 Flower FL Dashboard - Simulasi 3 Client 1 Server
Ready for Streamlit Community Cloud (streamlit.io)
Deployable directly from GitHub!
"""

import os
import json
import random
import time
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# -------------------------------------------------------------
# 1. Page Configuration
# -------------------------------------------------------------
st.set_page_config(
    page_title="Flower FL Simulation (1 Server 3 Client)",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme glassmorphism styling
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    .metric-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .client-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .badge-ok {
        background: #064e3b;
        color: #34d399;
        padding: 2px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 11px;
    }
    .badge-warn {
        background: #78350f;
        color: #fbbf24;
        padding: 2px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 11px;
    }
    .badge-err {
        background: #7f1d1d;
        color: #f87171;
        padding: 2px 8px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 11px;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Rubric & Checklist Definition (GB-CLASS-IIa-v1)
# -------------------------------------------------------------
CHECKLIST = [
    {"id": "R01", "requirement": "Device description and specification", "requirement_zh": "产品描述与技术规格"},
    {"id": "R02", "requirement": "Labelling and IFU in English", "requirement_zh": "英文标签与使用说明书"},
    {"id": "R03", "requirement": "Essential requirements checklist", "requirement_zh": "基本要求对照表"},
    {"id": "R04", "requirement": "Risk management file (ISO 14971)", "requirement_zh": "风险管理文件"},
    {"id": "R05", "requirement": "Biological evaluation (ISO 10993)", "requirement_zh": "生物相容性评价"},
    {"id": "R06", "requirement": "Sterilisation validation", "requirement_zh": "灭菌确认"},
    {"id": "R07", "requirement": "Clinical evaluation report", "requirement_zh": "临床评价报告"},
    {"id": "R08", "requirement": "QMS certificate (ISO 13485)", "requirement_zh": "质量管理体系证书"},
    {"id": "R09", "requirement": "Approved Body certificate", "requirement_zh": "英国指定机构证书"},
    {"id": "R10", "requirement": "Declaration of Conformity (UK MDR 2002)", "requirement_zh": "符合性声明"},
    {"id": "R11", "requirement": "UKRP designation and mandate letter", "requirement_zh": "英国责任人委任文件"},
    {"id": "R12", "requirement": "Post-market surveillance plan", "requirement_zh": "上市后监督计划"},
]

BASE_DIR = Path(__file__).parent
DEMO_DIR = BASE_DIR / "demo_data"

# -------------------------------------------------------------
# 3. Session State Initialization
# -------------------------------------------------------------
if "current_round" not in st.session_state:
    st.session_state.current_round = 0
    st.session_state.max_rounds = 5
    st.session_state.phase = "IDLE"  # IDLE, BROADCASTING, LOCAL_TRAINING, UPLOADING, AGGREGATING, EVALUATING
    st.session_state.strategy = "FedAvg"
    st.session_state.app_mode = "gapcheck"
    st.session_state.total_bytes = 184500
    st.session_state.total_packets = 14

    st.session_state.server = {
        "name": "Flower UKRP Coordinator (ServerApp)",
        "role": "SuperLink & FedAvg Aggregator",
        "global_accuracy": 73.3,
        "global_loss": 0.267,
        "weights_version": "GB-CLASS-IIa-v1",
        "history": [{"round": 0, "accuracy": 73.3, "loss": 0.267}]
    }

    st.session_state.clients = [
        {
            "id": "manufacturer_a",
            "name": "Manufacturer A",
            "domain": "Sterile Infusion Sets (ISO 11135)",
            "samples": 12,
            "online": True,
            "status": "Ready",
            "accuracy": 100.0,
            "loss": 0.000,
            "color": "#10b981",
            "summary": {"present": 12, "incomplete": 0, "missing": 0, "not_applicable": 0},
            "history": [{"round": 0, "accuracy": 100.0, "loss": 0.000}]
        },
        {
            "id": "manufacturer_b",
            "name": "Manufacturer B",
            "domain": "Electronic Thermometer (IEC 60601)",
            "samples": 8,
            "online": True,
            "status": "Ready",
            "accuracy": 75.0,
            "loss": 0.250,
            "color": "#06b6d4",
            "summary": {"present": 7, "incomplete": 1, "missing": 2, "not_applicable": 2},
            "history": [{"round": 0, "accuracy": 75.0, "loss": 0.250}]
        },
        {
            "id": "manufacturer_c",
            "name": "Manufacturer C",
            "domain": "Class I Orthopaedic Support (Self-Decl)",
            "samples": 6,
            "online": True,
            "status": "Ready",
            "accuracy": 45.0,
            "loss": 0.550,
            "color": "#8b5cf6",
            "summary": {"present": 2, "incomplete": 5, "missing": 3, "not_applicable": 2},
            "history": [{"round": 0, "accuracy": 45.0, "loss": 0.550}]
        }
    ]

    st.session_state.logs = [
        {"time": "08:00:00", "source": "SERVER", "msg": "Flower ServerApp initialized with GB-CLASS-IIa-v1 rubric."},
        {"time": "08:00:01", "source": "NETWORK", "msg": "3 SuperNodes registered: Manufacturer A, B, C."}
    ]

def add_log(source, msg):
    t = time.strftime("%H:%M:%S")
    st.session_state.logs.append({"time": t, "source": source, "msg": msg})
    if len(st.session_state.logs) > 40:
        st.session_state.logs.pop(0)

def step_simulation():
    phase = st.session_state.phase
    rnd = st.session_state.current_round
    online_clients = [c for c in st.session_state.clients if c["online"]]

    if not online_clients:
        add_log("SERVER", "Error: Tidak ada klien yang online!")
        return

    if phase == "IDLE":
        st.session_state.current_round += 1
        st.session_state.phase = "BROADCASTING"
        st.session_state.total_bytes += 78200 * len(online_clients)
        st.session_state.total_packets += len(online_clients)
        for c in online_clients:
            c["status"] = "Receiving Rubric Weights..."
        add_log("SERVER", f"=== ROUND {st.session_state.current_round}/{st.session_state.max_rounds} MULAI ===")
        add_log("gRPC", f"Server broadcast query.gap_check / FitIns ke {len(online_clients)} SuperNodes")

    elif phase == "BROADCASTING":
        st.session_state.phase = "LOCAL_TRAINING"
        for c in online_clients:
            c["status"] = "Audit / Training Lokal..."
            # Slightly improve readiness during learning rounds
            gain = random.uniform(1.5, 4.0)
            c["accuracy"] = min(100.0, round(c["accuracy"] + gain, 1))
            c["loss"] = max(0.0, round((100 - c["accuracy"]) / 100.0, 3))
            c["history"].append({"round": st.session_state.current_round, "accuracy": c["accuracy"], "loss": c["loss"]})
            add_log(c["name"], f"Audit lokal selesai: Readiness {c['accuracy']}% | Gap: {c['loss']}")

    elif phase == "LOCAL_TRAINING":
        st.session_state.phase = "UPLOADING"
        st.session_state.total_bytes += 3200 * len(online_clients)
        st.session_state.total_packets += len(online_clients)
        for c in online_clients:
            c["status"] = "Uploading reply.gap_check (Δw)..."
        add_log("gRPC", "SuperNodes mentransmisikan status kepatuhan (metadata only, 0 raw docs)")

    elif phase == "UPLOADING":
        st.session_state.phase = "AGGREGATING"
        # Federated Averaging
        tot_samples = sum(c["samples"] for c in online_clients)
        avg_acc = sum((c["samples"] / tot_samples) * c["accuracy"] for c in online_clients)
        avg_loss = sum((c["samples"] / tot_samples) * c["loss"] for c in online_clients)

        st.session_state.server["global_accuracy"] = round(avg_acc, 1)
        st.session_state.server["global_loss"] = round(avg_loss, 3)
        st.session_state.server["history"].append({
            "round": st.session_state.current_round,
            "accuracy": round(avg_acc, 1),
            "loss": round(avg_loss, 3)
        })
        for c in online_clients:
            c["status"] = "Synchronized / Idle"
        add_log("SERVER", f"Agregasi FedAvg selesai! Global Readiness: {round(avg_acc, 1)}%, Gap: {round(avg_loss, 3)}")

    elif phase == "AGGREGATING":
        st.session_state.phase = "EVALUATING"
        add_log("SERVER", f"Evaluasi Round {st.session_state.current_round} diverifikasi.")

    elif phase == "EVALUATING":
        if st.session_state.current_round >= st.session_state.max_rounds:
            st.session_state.phase = "COMPLETED"
            add_log("SERVER", f"Federated Learning selesai di seluruh {st.session_state.max_rounds} round!")
        else:
            st.session_state.phase = "IDLE"

def reset_simulation():
    st.session_state.current_round = 0
    st.session_state.phase = "IDLE"
    st.session_state.server["global_accuracy"] = 73.3
    st.session_state.server["global_loss"] = 0.267
    st.session_state.server["history"] = [{"round": 0, "accuracy": 73.3, "loss": 0.267}]
    st.session_state.clients[0]["accuracy"] = 100.0
    st.session_state.clients[0]["history"] = [{"round": 0, "accuracy": 100.0, "loss": 0.000}]
    st.session_state.clients[1]["accuracy"] = 75.0
    st.session_state.clients[1]["history"] = [{"round": 0, "accuracy": 75.0, "loss": 0.250}]
    st.session_state.clients[2]["accuracy"] = 45.0
    st.session_state.clients[2]["history"] = [{"round": 0, "accuracy": 45.0, "loss": 0.550}]
    for c in st.session_state.clients:
        c["status"] = "Ready"
    add_log("SIM", "Simulasi direset ke kondisi awal.")

# -------------------------------------------------------------
# 4. Sidebar Controls
# -------------------------------------------------------------
with st.sidebar:
    st.title("🌸 Flower FL Hub")
    st.caption("1 Central Server (SuperLink) + 3 SuperNodes")

    st.markdown("---")
    st.subheader("⚙️ Kontrol Simulasi")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("⏩ Step Fase", use_container_width=True, type="primary"):
            step_simulation()
            st.rerun()

    with col_btn2:
        if st.button("🔄 Reset", use_container_width=True):
            reset_simulation()
            st.rerun()

    st.markdown("---")
    st.subheader("📡 Pertukaran Data Manual")
    if st.button("🚀 Broadcast (Server ➔ Klien)", use_container_width=True):
        st.session_state.phase = "IDLE"
        step_simulation()
        st.rerun()

    if st.button("📤 Unggah Update (Klien ➔ Server)", use_container_width=True):
        st.session_state.phase = "LOCAL_TRAINING"
        step_simulation()
        st.rerun()

    if st.button("🔄 Agregasi FedAvg", use_container_width=True):
        st.session_state.phase = "UPLOADING"
        step_simulation()
        st.rerun()

    st.markdown("---")
    st.subheader("📶 Status Klien (Dropout Sim)")
    for c in st.session_state.clients:
        c["online"] = st.checkbox(f"{c['name']} (Online)", value=c["online"], key=f"chk_{c['id']}")

    st.markdown("---")
    st.caption("Deployable on Streamlit Community Cloud (share.streamlit.io)")

# -------------------------------------------------------------
# 5. Main Dashboard Header & Metrics HUD
# -------------------------------------------------------------
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🌸 Flower Federated Learning Dashboard")
    st.markdown("**Simulasi Interaktif Visual 1 Central Server (SuperLink) & 3 Distributed Clients**")

with col_h2:
    st.markdown(f"""
    <div style="text-align: right; font-family: monospace; padding-top: 10px;">
        <span style="background: #1e293b; padding: 6px 12px; border-radius: 8px; border: 1px solid #334155;">
            ROUND: <strong style="color: #34d399;">{st.session_state.current_round} / {st.session_state.max_rounds}</strong>
        </span>
        <br><br>
        <span style="background: #1e293b; padding: 6px 12px; border-radius: 8px; border: 1px solid #334155;">
            FASE: <strong style="color: #38bdf8;">{st.session_state.phase}</strong>
        </span>
    </div>
    """, unsafe_allow_html=True)

# 4 Key Metrics Cards
hud1, hud2, hud3, hud4 = st.columns(4)
with hud1:
    st.metric("Global Readiness", f"{st.session_state.server['global_accuracy']}%", delta=f"{round(st.session_state.server['global_accuracy'] - 73.3, 1)}%")

with hud2:
    st.metric("Regulatory Gap / Loss", f"{st.session_state.server['global_loss']}", delta=f"-{round(0.267 - st.session_state.server['global_loss'], 3)}", delta_color="inverse")

with hud3:
    online_count = len([c for c in st.session_state.clients if c["online"]])
    st.metric("Node Klien Terhubung", f"{online_count} / 3 Aktif", delta="gRPC Online")

with hud4:
    tot_kb = round(st.session_state.total_bytes / 1024, 1)
    st.metric("Data Transferred", f"{tot_kb} KB", delta="0 Dokumen Mentah (100% Privacy)")

st.markdown("---")

# -------------------------------------------------------------
# 6. HTML5 60 FPS Visual Canvas Topology Component
# -------------------------------------------------------------
st.subheader("🌐 Topologi Interaksi Jaringan & Aliran Paket Data (gRPC Transport)")

# Generate dynamic canvas script based on current phase and online nodes
online_flags = [c["online"] for c in st.session_state.clients]
current_phase_str = st.session_state.phase

canvas_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ margin: 0; padding: 0; background: #090d16; overflow: hidden; font-family: sans-serif; }}
  canvas {{ width: 100%; height: 350px; display: block; }}
  .banner {{
    position: absolute; bottom: 8px; left: 12px; right: 12px;
    background: rgba(15, 23, 42, 0.9); border: 1px solid #334155;
    border-radius: 10px; padding: 8px 14px; display: flex; justify-content: space-between;
    align-items: center; color: #e2e8f0; font-size: 11px; font-family: monospace;
  }}
</style>
</head>
<body>
<canvas id="cv"></canvas>
<div class="banner">
  <span>FASE: <strong style="color: #38bdf8;">{current_phase_str}</strong> | STATUS: <strong style="color: #34d399;">Flower SuperLink Active</strong></span>
  <span style="color: #94a3b8;">gRPC RecordDict Protocol &bull; 1 Server ➔ 3 Clients</span>
</div>

<script>
const cv = document.getElementById('cv');
const ctx = cv.getContext('2d');
const dpr = window.devicePixelRatio || 1;
let W, H;

function resize() {{
  W = cv.parentElement.clientWidth;
  H = 350;
  cv.width = W * dpr;
  cv.height = H * dpr;
  ctx.scale(dpr, dpr);
}}
resize();
window.addEventListener('resize', resize);

const nodes = {{
  server: {{ x: 0.50, y: 0.24, radius: 32, name: 'Flower ServerApp (UKRP)', color: '#10b981' }},
  c1: {{ x: 0.20, y: 0.72, radius: 24, name: 'Manufacturer A', color: '#10b981', online: {str(online_flags[0]).lower()} }},
  c2: {{ x: 0.50, y: 0.76, radius: 24, name: 'Manufacturer B', color: '#06b6d4', online: {str(online_flags[1]).lower()} }},
  c3: {{ x: 0.80, y: 0.72, radius: 24, name: 'Manufacturer C', color: '#8b5cf6', online: {str(online_flags[2]).lower()} }}
}};

let packets = [];
const phase = '{current_phase_str}';

if (phase === 'BROADCASTING') {{
  ['c1', 'c2', 'c3'].forEach(cid => {{
    if (nodes[cid].online) {{
      packets.push({{ from: 'server', to: cid, prog: 0, speed: 0.015, color: '#38bdf8', label: 'query.gap_check' }});
    }}
  }});
}} else if (phase === 'UPLOADING') {{
  ['c1', 'c2', 'c3'].forEach(cid => {{
    if (nodes[cid].online) {{
      packets.push({{ from: cid, to: 'server', prog: 0, speed: 0.015, color: nodes[cid].color, label: 'reply.gap_check' }});
    }}
  }});
}}

function draw(time) {{
  ctx.clearRect(0, 0, W, H);

  const sPos = {{ x: nodes.server.x * W, y: nodes.server.y * H }};

  // Cables
  ['c1', 'c2', 'c3'].forEach(cid => {{
    const c = nodes[cid];
    const cPos = {{ x: c.x * W, y: c.y * H }};
    ctx.beginPath();
    ctx.moveTo(sPos.x, sPos.y);
    ctx.quadraticCurveTo((sPos.x + cPos.x)/2, (sPos.y + cPos.y)/2 - 20, cPos.x, cPos.y);
    ctx.strokeStyle = c.online ? c.color + '66' : 'rgba(239, 68, 68, 0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
  }});

  // Packets
  packets.forEach(p => {{
    p.prog += p.speed;
    if (p.prog > 1) p.prog = 0;
    const from = nodes[p.from];
    const to = nodes[p.to];
    const fx = from.x * W, fy = from.y * H;
    const tx = to.x * W, ty = to.y * H;
    const midX = (fx + tx)/2, midY = (fy + ty)/2 - 20;
    const t = p.prog;
    const px = (1-t)*(1-t)*fx + 2*(1-t)*t*midX + t*t*tx;
    const py = (1-t)*(1-t)*fy + 2*(1-t)*t*midY + t*t*ty;

    ctx.beginPath();
    ctx.arc(px, py, 6, 0, Math.PI * 2);
    ctx.fillStyle = p.color;
    ctx.fill();

    ctx.font = '9px monospace';
    ctx.fillStyle = '#f8fafc';
    ctx.textAlign = 'center';
    ctx.fillText(p.label, px, py - 10);
  }});

  // Server Node
  ctx.beginPath();
  ctx.arc(sPos.x, sPos.y, nodes.server.radius, 0, Math.PI * 2);
  ctx.fillStyle = '#065f46';
  ctx.fill();
  ctx.strokeStyle = '#34d399';
  ctx.lineWidth = 2.5;
  ctx.stroke();
  ctx.font = 'bold 11px sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.textAlign = 'center';
  ctx.fillText('SERVER', sPos.x, sPos.y + 4);

  // Client Nodes
  ['c1', 'c2', 'c3'].forEach(cid => {{
    const c = nodes[cid];
    const cx = c.x * W, cy = c.y * H;
    ctx.beginPath();
    ctx.arc(cx, cy, c.radius, 0, Math.PI * 2);
    ctx.fillStyle = c.online ? '#0f172a' : '#450a0a';
    ctx.fill();
    ctx.strokeStyle = c.online ? c.color : '#ef4444';
    ctx.lineWidth = 2;
    ctx.stroke();

    ctx.font = 'bold 10px sans-serif';
    ctx.fillStyle = c.online ? '#f1f5f9' : '#f87171';
    ctx.textAlign = 'center';
    ctx.fillText(c.name, cx, cy + c.radius + 14);
  }});

  requestAnimationFrame(draw);
}}
requestAnimationFrame(draw);
</script>
</body>
</html>
"""

components.html(canvas_html, height=360)

# -------------------------------------------------------------
# 7. 3 Client Node Cards
# -------------------------------------------------------------
st.subheader("💻 Node Klien Terdistribusi (3 SuperNodes)")

c_col1, c_col2, c_col3 = st.columns(3)
cols = [c_col1, c_col2, c_col3]

for idx, c in enumerate(st.session_state.clients):
    with cols[idx]:
        st.markdown(f"""
        <div class="client-card" style="border-left: 4px solid {c['color']};">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin: 0; color: #f8fafc;">{c['name']}</h4>
                <span class="{ 'badge-ok' if c['online'] else 'badge-err' }">{ 'ONLINE' if c['online'] else 'OFFLINE' }</span>
            </div>
            <p style="font-size: 11px; color: #94a3b8; font-family: monospace; margin: 4px 0 10px 0;">{c['domain']}</p>
            <div style="display: flex; justify-content: space-between; font-size: 12px; margin-bottom: 6px;">
                <span>Readiness: <strong style="color: #34d399;">{c['accuracy']}%</strong></span>
                <span>Gap: <strong style="color: #fbbf24;">{c['loss']}</strong></span>
            </div>
            <div style="font-size: 11px; color: #64748b; font-family: monospace;">
                Dokumen: {c['samples']} files &bull; Status: {c['status']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# 8. Plotly Convergence Chart & Logs
# -------------------------------------------------------------
chart_col, log_col = st.columns([2, 1])

with chart_col:
    st.subheader("📈 Kurva Konvergensi Federated Learning")

    history = st.session_state.server["history"]
    df_rounds = [f"Round {h['round']}" for h in history]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_rounds,
        y=[h["accuracy"] for h in history],
        mode="lines+markers",
        name="Global Model (Server)",
        line=dict(color="#10b981", width=3),
        marker=dict(size=8)
    ))

    for c in st.session_state.clients:
        fig.add_trace(go.Scatter(
            x=df_rounds[:len(c["history"])],
            y=[h["accuracy"] for h in c["history"]],
            mode="lines+markers",
            name=c["name"],
            line=dict(color=c["color"], width=1.5, dash="dash"),
            marker=dict(size=5)
        ))

    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#090d16",
        paper_bgcolor="#0f172a",
        margin=dict(l=20, r=20, t=30, b=20),
        height=320,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Readiness / Akurasi (%)", range=[20, 105]),
        xaxis=dict(title="Federated Learning Rounds")
    )

    st.plotly_chart(fig, use_container_width=True)

with log_col:
    st.subheader("📜 Protokol Log (gRPC Stream)")
    log_box = st.container(height=320)
    with log_box:
        for l in reversed(st.session_state.logs):
            badge_color = "#34d399" if "SERVER" in l["source"] else "#38bdf8" if "gRPC" in l["source"] else "#a855f7"
            st.markdown(f"""
            <div style="font-family: monospace; font-size: 11px; margin-bottom: 6px; line-height: 1.3;">
                <span style="color: #64748b;">[{l['time']}]</span>
                <span style="color: {badge_color}; font-weight: bold;">{l['source']}</span>:
                <span style="color: #cbd5e1;">{l['msg']}</span>
            </div>
            """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------------
# 9. Checklist Regulatory Inspector (R01 - R12)
# -------------------------------------------------------------
st.subheader("📋 Rincian Temuan Regulasi UK MDR 2002 (Rubrik R01 - R12)")

tab_a, tab_b, tab_c = st.tabs(["Manufacturer A (Sterile)", "Manufacturer B (Electronic)", "Manufacturer C (Class I)"])

def render_checklist_table(client_idx):
    c = st.session_state.clients[client_idx]
    rows = []
    for item in CHECKLIST:
        # Determine status per node
        if c["id"] == "manufacturer_a":
            status = "✓ Lengkap"
            cls = "badge-ok"
        elif c["id"] == "manufacturer_b":
            if item["id"] in ["R06", "R12"]:
                status = "✕ Tidak Ada"
                cls = "badge-err"
            elif item["id"] == "R10":
                status = "! Belum Lengkap"
                cls = "badge-warn"
            elif item["id"] in ["R05", "R09"]:
                status = "— N/A"
                cls = "badge-ok"
            else:
                status = "✓ Lengkap"
                cls = "badge-ok"
        else: # manufacturer_c
            if item["id"] in ["R06", "R08", "R09"]:
                status = "— N/A"
                cls = "badge-ok"
            elif item["id"] in ["R07", "R12"]:
                status = "✕ Tidak Ada"
                cls = "badge-err"
            elif item["id"] in ["R01", "R03", "R04", "R10"]:
                status = "! Draft"
                cls = "badge-warn"
            else:
                status = "✓ Lengkap"
                cls = "badge-ok"

        rows.append({
            "ID": item["id"],
            "Persyaratan Regulasi": item["requirement"],
            "Status": f'<span class="{cls}">{status}</span>'
        })
    df = pd.DataFrame(rows)
    st.write(df.to_html(escape=False, index=False), unsafe_allow_html=True)

with tab_a:
    render_checklist_table(0)

with tab_b:
    render_checklist_table(1)

with tab_c:
    render_checklist_table(2)

st.caption("🌸 Flower Federated Learning Streamlit Hub &bull; Ready for Streamlit Cloud")
