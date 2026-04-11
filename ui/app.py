import streamlit as st
import cv2
import pandas as pd
import plotly.express as px
import time
import os

from core.detection import PersonDetector
from core.tracker import PersonTracker
from core.logic import CrowdLogic

# Page Config
st.set_page_config(page_title="Queue-Safe AI System", layout="wide", page_icon="🛡️")

# Load CSS
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except Exception as e:
        pass

load_css("ui/style.css")

# --- Session State Management ---
if 'running' not in st.session_state:
    st.session_state.running = False
if 'source' not in st.session_state:
    st.session_state.source = None
if 'history' not in st.session_state:
    st.session_state.history = []
if 'tracker' not in st.session_state:
    st.session_state.tracker = PersonTracker()
if 'logic' not in st.session_state:
    st.session_state.logic = CrowdLogic()
if 'last_fps' not in st.session_state:
    st.session_state.last_fps = 0.0

# Load heavy YOLO model once
@st.cache_resource
def load_detector():
    return PersonDetector("yolov8n.pt")

detector = load_detector()

# --- UI Header ---
st.title("🛡️ Queue-Safe AI System")
st.markdown("<p class='subtitle'>Real-time Queue Intelligence and Safety Monitoring System</p>", unsafe_allow_html=True)

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Controls")
source_type = st.sidebar.radio("Input Source", ["Webcam", "Video File"])

if source_type == "Webcam":
    if st.sidebar.button("Start Webcam"):
        st.session_state.source = 0
        st.session_state.running = True
        st.session_state.history = []
        st.session_state.tracker = PersonTracker()
        st.session_state.logic = CrowdLogic()
elif source_type == "Video File":
    uploaded_file = st.sidebar.file_uploader("Upload Video", type=["mp4", "avi", "mov"])
    if uploaded_file is not None:
        if st.sidebar.button("Start Processing Upload"):
            temp_path = os.path.abspath("temp.mp4")
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.read())
            st.session_state.source = temp_path
            st.session_state.running = True
            st.session_state.history = []
            st.session_state.tracker = PersonTracker()
            st.session_state.logic = CrowdLogic()

if st.sidebar.button("Stop System"):
    st.session_state.running = False

st.sidebar.markdown("---")
st.sidebar.header("👁️ Visual Overlays")
draw_zones = st.sidebar.checkbox("Show Zone Analysis", value=True)
draw_heatmap = st.sidebar.checkbox("Show Density Heatmap", value=False)

# --- Status side panel ---
status_class = "status-dot" if st.session_state.running else "status-dot stopped"
status_text = "Running" if st.session_state.running else "Stopped"
source_text = "Webcam" if source_type == "Webcam" else "Video"

st.sidebar.markdown(f"""
<div class="side-panel glass">
    <h4>Status Panel</h4>
    <p><span class="{status_class}"></span> <strong>{status_text}</strong></p>
    <p>📡 <strong>Source:</strong> {source_text}</p>
</div>
""", unsafe_allow_html=True)

# --- Main Layout ---
alert_banner_placeholder = st.empty()

col1, col2 = st.columns([2, 1])

with col1:
    # Neon-glow video wrapper with title overlay & FPS badge
    fps_val = st.session_state.last_fps
    st.markdown(f'''
    <div class="video-wrapper">
        <div class="video-inner">
            <div class="video-title-overlay"><span>Live AI Detection</span></div>
            <div class="fps-badge"><span>⚡ {fps_val:.1f} FPS</span></div>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    # Actual Streamlit image placeholder sits right below (rendered into the inner area)
    video_placeholder = st.empty()
    loading_placeholder = st.empty()

with col2:
    kpi_placeholder = st.empty()

# Horizontal stats bar (Below video / Above Graph)
horizontal_stats_placeholder = st.empty()

st.markdown("## Upload video or turn on webcam for Analytics & Trends 📈")
graph_placeholder = st.empty()

# Bottom section: AI Insights, Growth
bottom_placeholder = st.empty()


def get_ai_insight(stats):
    """Generate AI insight message based on current stats."""
    risk = stats.get('risk_level', 'LOW')
    growth = stats.get('growth', 0)

    if risk == "HIGH":
        return ("🚨", "Overcrowding detected", "risk-high")
    elif growth > 0:
        return ("⚠️", "Crowd building up", "risk-warning")
    else:
        return ("✅", "Crowd under control", "risk-safe")

def get_decision(count, risk):
    if risk == "LOW":
        return "✅ Situation under control"
    elif risk == "MEDIUM":
        return "⚠️ Monitor crowd closely"
    else:
        return "🚨 Open new counter / restrict entry"

def get_safety_status(count):
    if count <= 10:
        return "SAFE"
    elif count <= 20:
        return "CAUTION"
    else:
        return "DANGER"

def estimate_wait(count):
    return count * 2


def update_ui(stats, fps, frame_count):
    risk_level = stats.get('risk_level', 'LOW')
    risk_color = "red" if risk_level == "HIGH" else "yellow" if risk_level == "MEDIUM" else "green"
    
    current_count = stats.get('count', 0)
    prediction = stats.get('prediction', current_count)
    if prediction > current_count:
        pred_arrow = "⬆ Increasing"
    elif prediction < current_count:
        pred_arrow = "⬇ Decreasing"
    else:
        pred_arrow = "→ Stable"

    growth = stats.get('growth', 0)
    if growth > 0:
        growth_text = "⬆ Increasing"
        growth_color = "#ff4b4b"
    elif growth < 0:
        growth_text = "⬇ Decreasing"
        growth_color = "#00ff00"
    else:
        growth_text = "→ Stable"
        growth_color = "#e2e8f0"
        
    p_risk = stats.get('predicted_risk', 'LOW')
    
    # Large Centered Alert Banner
    with alert_banner_placeholder.container():
        if risk_level == "HIGH":
            st.markdown('<div class="alert-box danger glass animate-pulse" style="text-align:center; font-size:1.5rem; padding:20px;"><strong>🚨 HIGH RISK DETECTED</strong></div>', unsafe_allow_html=True)
        elif risk_level == "MEDIUM":
            st.markdown('<div class="alert-box warning glass" style="text-align:center; font-size:1.5rem; padding:20px;"><strong>⚠️ MEDIUM RISK</strong></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="alert-box safe glass" style="text-align:center; font-size:1.5rem; padding:20px;"><strong>✅ SYSTEM SAFE - LOW RISK</strong></div>', unsafe_allow_html=True)
    
    with kpi_placeholder.container():
        # KPIs + Alerts
        st.markdown(f"""
        <div class="kpi-card glass">
            <h4>👥 Crowd Count</h4>
            <h2>{current_count}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Prediction Card
        st.markdown(f"""
        <div class="kpi-card glass" style="padding: 15px; margin-top: 15px; border-left: 5px solid #00d4ff;">
            <p style="margin: 0; font-size: 0.9rem; color: #cbd5e0; text-transform: uppercase;">Prediction</p>
            <h4 style="margin: 5px 0 0 0; color: #ffffff; font-size: 1.2rem;">Next 10 sec: {prediction} people</h4>
            <p style="margin: 5px 0 0 0; font-size: 1rem; color: #00d4ff;">{pred_arrow}</p>
        </div>
        """, unsafe_allow_html=True)

        avg_conf = stats.get('avg_confidence', 0.0)
        st.markdown(f"""
        <div class="kpi-card glass" style="padding: 15px; margin-top: 15px; border-left: 5px solid rgba(0, 255, 136, 0.4);">
            <p style="margin: 0; font-size: 0.9rem; color: #cbd5e0; text-transform: uppercase;">Detection Accuracy</p>
            <h4 style="margin: 5px 0 0 0; color: #ffffff; font-size: 1.2rem;">Detection Confidence: {avg_conf:.1f}%</h4>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="side-panel glass" style="margin-top: 15px; padding: 10px; text-align: center;">
            <span style="margin-right: 15px;">⏱️ FPS: <strong>{fps:.1f}</strong></span>
            <span>🎞️ Frame: <strong>{frame_count}</strong></span>
        </div>
        """, unsafe_allow_html=True)

        # AI Decision Support Panel
        decision_msg = get_decision(current_count, risk_level)
        st.markdown(f"""
        <div class="kpi-card glass" style="padding: 20px; margin-top: 15px; text-align: center;">
            <p style="margin: 0; font-size: 0.9rem; color: #cbd5e0; text-transform: uppercase;">AI Decision Support</p>
            <h3 style="margin: 10px 0 0 0; color: #ffffff; font-size: 1.4rem;">{decision_msg}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # Public Safety Monitoring
        safety_status = get_safety_status(current_count)
        if safety_status == "SAFE":
            safety_color = "rgba(0, 255, 0, 0.15)"
            border_color = "#00ff00"
            safety_msg = "Environment is safe"
        elif safety_status == "CAUTION":
            safety_color = "rgba(255, 193, 7, 0.15)"
            border_color = "#ffc107"
            safety_msg = "Crowd building up"
        else:
            safety_color = "rgba(255, 75, 75, 0.15)"
            border_color = "#ff4b4b"
            safety_msg = "Unsafe crowd density detected"
            
        st.markdown(f"""
        <div class="kpi-card glass" style="padding: 15px; margin-top: 15px; background: {safety_color}; border-left: 5px solid {border_color};">
            <p style="margin: 0; font-size: 0.9rem; color: #cbd5e0; text-transform: uppercase;">Public Safety Monitoring</p>
            <h4 style="margin: 5px 0 0 0; color: #ffffff; font-size: 1.2rem;">{safety_status}</h4>
            <p style="margin: 5px 0 0 0; font-size: 1rem; color: #e2e8f0;">{safety_msg}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Queue Management Panel
        wait_time = estimate_wait(current_count)
        if current_count <= 5:
            q_status = "Fast Service"
            q_sug = "Flow is smooth"
        elif current_count <= 12:
            q_status = "Moderate Delay"
            q_sug = "Monitor queue"
        else:
            q_status = "High Waiting Time"
            q_sug = "Add more counters"
            
        st.markdown(f"""
        <div class="kpi-card glass" style="padding: 15px; margin-top: 15px; border-left: 5px solid #7b2ff7;">
            <p style="margin: 0; font-size: 0.9rem; color: #cbd5e0; text-transform: uppercase;">Queue Management</p>
            <h4 style="margin: 5px 0 0 0; color: #ffffff; font-size: 1.2rem;">Estimated Wait Time: {wait_time} seconds</h4>
            <p style="margin: 5px 0 0 0; font-size: 1rem; color: #00d4ff;">Status: {q_status}</p>
            <p style="margin: 5px 0 0 0; font-size: 0.95rem; color: #e2e8f0;">💡 {q_sug}</p>
        </div>
        """, unsafe_allow_html=True)

    # --- Horizontal Stats Bar (Below video / Above Graph) --- 
    with horizontal_stats_placeholder.container():
        st.markdown(f"""
        <div class="glass" style="display: flex; justify-content: space-around; padding: 15px; margin-bottom: 20px;">
            <div style="font-size: 1.1rem;">👥 <strong>{stats['count']}</strong> <span style="font-size:0.9rem; color:#cbd5e0;">Count</span></div>
            <div style="font-size: 1.1rem;">⚠️ <strong>{risk_level}</strong> <span style="font-size:0.9rem; color:#cbd5e0;">Risk</span></div>
            <div style="font-size: 1.1rem;">📈 <strong style="color:{growth_color}">{growth_text}</strong> <span style="font-size:0.9rem; color:#cbd5e0;">Growth</span></div>
            <div style="font-size: 1.1rem;">🔮 <strong>{stats.get('prediction', 0)}</strong> <span style="font-size:0.9rem; color:#cbd5e0;">Pred</span></div>
        </div>
        """, unsafe_allow_html=True)
    
    # --- Bottom Section: AI Insights | Growth | Stats ---
    icon, message, css_class = get_ai_insight(stats)
    with bottom_placeholder.container():
        bc1, bc2, bc3 = st.columns([2, 1, 1])
        with bc1:
            st.markdown(f"""
            <div class="ai-insight-panel {css_class}" style="margin: 0;">
                <div class="insight-icon">{icon}</div>
                <div class="insight-text">{message}</div>
                <div class="insight-sublabel">AI Intelligence Engine • Live</div>
            </div>
            """, unsafe_allow_html=True)
        with bc2:
            st.markdown(f"""
            <div class="kpi-card glass" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <h4>📈 Trend</h4>
                <h2 style="font-size: 1.8rem; color: {growth_color};">{growth_text}</h2>
            </div>
            """, unsafe_allow_html=True)
        with bc3:
            st.markdown(f"""
            <div class="kpi-card glass" style="height: 100%; display: flex; flex-direction: column; justify-content: center;">
                <h4>📊 Stats</h4>
                <h2 style="font-size: 1.8rem;">{stats['count']} Total</h2>
            </div>
            """, unsafe_allow_html=True)


# --- Main Processing Loop ---
if st.session_state.running and st.session_state.source is not None:
    cap = cv2.VideoCapture(st.session_state.source)
    if not cap.isOpened():
        st.error(f"Video failed to load from source: {st.session_state.source}")
        st.session_state.running = False
    
    loading_placeholder.info("⏳ Processing video...")
    
    frame_count = 0
    prev_time = time.time()
    
    while cap.isOpened() and st.session_state.running:
        ret, frame = cap.read()
        if not ret:
            st.warning("✅ Video playback finished.")
            st.session_state.running = False
            break
            
        frame_count += 1
        
        # Clear loading indicator on first frame
        if frame_count == 1:
            loading_placeholder.empty()
        
        # Optimize size
        frame = cv2.resize(frame, (640, 480))
        
        # 1. Detect
        detections = detector.detect(frame)
        avg_conf = 0.0
        if detections:
            avg_conf = sum([d[1] for d in detections]) / len(detections)
        
        # 2. Track & Draw
        st.session_state.tracker.draw_bboxes = True
        st.session_state.tracker.draw_heatmap = draw_heatmap
        st.session_state.tracker.draw_lines = True
        try:
            drawn_frame, count, tracker_data = st.session_state.tracker.update(frame, detections)
        except (TypeError, ValueError):
            st.session_state.tracker = PersonTracker()
            st.session_state.logic = CrowdLogic()
            st.session_state.tracker.draw_bboxes = True
            st.session_state.tracker.draw_heatmap = draw_heatmap
            st.session_state.tracker.draw_lines = True
            drawn_frame, count, tracker_data = st.session_state.tracker.update(frame, detections)
        
        # 3. Analyze logic
        stats = st.session_state.logic.analyze_frame(count, tracker_data, frame_width=frame.shape[1])
        stats['avg_confidence'] = avg_conf * 100
        
        # 4. Render Zones directly into Streamlit feed if requested
        if draw_zones and 'zone_risks' in stats:
            w = frame.shape[1]
            z_w = int(w / 3)
            overlay = drawn_frame.copy()
            zones_rects = {"Left": (0, z_w), "Center": (z_w, 2 * z_w), "Right": (2 * z_w, w)}
            
            for z_name, (x_start, x_end) in zones_rects.items():
                risk = stats['zone_risks'][z_name]
                color = (0, 0, 255) if risk == "HIGH" else (0, 255, 255) if risk == "MEDIUM" else (0, 255, 0)
                cv2.rectangle(overlay, (x_start, 0), (x_end, frame.shape[0]), color, -1)
                
            drawn_frame = cv2.addWeighted(overlay, 0.15, drawn_frame, 0.85, 0)
            
            # Draw dividers and labels
            for i, (z_name, (x_start, x_end)) in enumerate(zones_rects.items()):
                if i > 0:
                    cv2.line(drawn_frame, (x_start, 0), (x_start, frame.shape[0]), (255, 255, 255), 1)
                cv2.putText(drawn_frame, z_name, (x_start + 10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)
        
        # Performance/Timing
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time + 0.0001)
        prev_time = curr_time
        st.session_state.last_fps = fps
        
        # BGR -> RGB for Streamlit
        drawn_frame_rgb = cv2.cvtColor(drawn_frame, cv2.COLOR_BGR2RGB)
        
        # Update Image Placeholders
        video_placeholder.image(drawn_frame_rgb, channels="RGB", use_container_width=True)
        
        # History
        if frame_count % 3 == 0:
            st.session_state.history.append({"frame": frame_count, "count": count})
            if len(st.session_state.history) > 100:
                st.session_state.history.pop(0)

        # Update KPI UI
        if frame_count % 3 == 0:
            update_ui(stats, fps, frame_count)
            
            if len(st.session_state.history) > 1:
                df = pd.DataFrame(st.session_state.history)
                fig = px.line(df, x="frame", y="count", title="AI-Queue Intelligence System")
                
                # Base Line
                fig.update_traces(line_color='#00d4ff', line_width=3, line_shape='spline')
                
                # Glow effect
                fig.add_scatter(x=df["frame"], y=df["count"], mode='lines', 
                                line=dict(color='rgba(0, 212, 255, 0.25)', width=8, shape='spline'), 
                                showlegend=False, hoverinfo='skip')

                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", 
                    plot_bgcolor="rgba(0,0,0,0.1)", 
                    font=dict(color="#e2e8f0"),
                    margin=dict(l=20, r=20, t=40, b=20),
                    height=300,
                    xaxis=dict(showgrid=False, title="Frame Index", zeroline=False),
                    yaxis=dict(showgrid=False, title="People Count", zeroline=False)
                )
                
                graph_placeholder.plotly_chart(fig, use_container_width=True)
        
        # Small delay for smooth playback
        time.sleep(0.03)

    cap.release()
