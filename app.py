import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

# --- 1. DATA HANDLING ---
def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            return json.load(f)
    return {"timetable": [], "tasks": [], "labs": []}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

data = load_data()

ADMIN_PASSWORD = st.secrets["password"]

st.set_page_config(
    page_title="NMAMIT Companion",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. GLOBAL STYLES ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=SF+Pro+Display:wght@300;400;500;600&family=Inter:wght@300;400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* ── Root tokens ── */
:root {
    --bg:        #0a0a0a;
    --surface:   #111111;
    --surface2:  #1a1a1a;
    --border:    #262626;
    --text:      #f5f5f5;
    --text-dim:  #737373;
    --accent:    #f5f5f5;
    --blue:      #3b82f6;
    --green:     #22c55e;
    --amber:     #f59e0b;
    --red:       #ef4444;
    --radius:    14px;
    --radius-sm: 8px;
}

/* ── Base ── */
html, body, .stApp {
    background: var(--bg) !important;
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
.block-container {
    padding: 2rem 1.5rem 4rem !important;
    max-width: 860px !important;
    margin: 0 auto !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
}
section[data-testid="stSidebar"] .stSelectbox > div > div {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}

/* ── Typography ── */
h1, h2, h3, h4 {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    letter-spacing: -0.03em !important;
    color: var(--text) !important;
}
p, span, label, div {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--text) !important;
}

/* ── Page header ── */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid var(--border);
}
.page-header h1 {
    font-size: clamp(1.6rem, 4vw, 2.2rem) !important;
    margin: 0 !important;
}
.page-header .sub {
    font-size: 0.85rem;
    color: var(--text-dim);
    font-weight: 400;
}

/* ── Stat cards ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 12px;
    margin-bottom: 2rem;
}
.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    transition: border-color .2s;
}
.stat-card:hover { border-color: #404040; }
.stat-card .label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: var(--text-dim);
    margin-bottom: 6px;
}
.stat-card .value {
    font-size: 1.6rem;
    font-weight: 600;
    letter-spacing: -0.04em;
    color: var(--text);
}
.stat-card .value.green { color: var(--green); }
.stat-card .value.amber { color: var(--amber); }
.stat-card .value.blue  { color: var(--blue); }

/* ── Section label ── */
.section-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: .1em;
    color: var(--text-dim);
    margin-bottom: 10px;
    margin-top: 1.8rem;
}

/* ── Class pills (today schedule) ── */
.class-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 1rem; }
.class-row {
    display: flex;
    align-items: center;
    gap: 14px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: .75rem 1rem;
}
.class-time {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-dim);
    min-width: 70px;
}
.class-name { font-weight: 500; font-size: 0.9rem; }
.class-venue {
    margin-left: auto;
    font-size: 0.75rem;
    color: var(--text-dim);
    background: var(--surface2);
    padding: 3px 8px;
    border-radius: 20px;
}

/* ── Task pills ── */
.task-list { display: flex; flex-direction: column; gap: 8px; }
.task-row {
    display: flex;
    align-items: center;
    gap: 12px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: .75rem 1rem;
}
.task-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.task-dot.Assignment { background: var(--blue); }
.task-dot.Test       { background: var(--red); }
.task-dot.Homework   { background: var(--amber); }
.task-dot.Lab\ Record { background: var(--green); }
.task-name { font-weight: 500; font-size: 0.9rem; flex: 1; }
.task-type {
    font-size: 0.72rem;
    color: var(--text-dim);
    background: var(--surface2);
    padding: 3px 9px;
    border-radius: 20px;
}
.task-date {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--text-dim);
}

/* ── Deadline badge ── */
.badge-urgent { color: var(--red) !important; }
.badge-soon   { color: var(--amber) !important; }
.badge-ok     { color: var(--green) !important; }

/* ── Forms ── */
.stTextInput input, .stTextArea textarea, .stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #404040 !important;
    box-shadow: none !important;
}

/* ── Buttons ── */
.stButton > button {
    background: var(--text) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    padding: .55rem 1.4rem !important;
    transition: opacity .15s !important;
    letter-spacing: -0.01em !important;
}
.stButton > button:hover { opacity: .85 !important; }

/* ── Download button ── */
.stDownloadButton > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Alerts ── */
.stAlert {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}

/* ── Dataframe / table ── */
.stDataFrame, .stTable {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
.stDataFrame thead th {
    background: var(--surface2) !important;
    color: var(--text-dim) !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: .07em !important;
    border-bottom: 1px solid var(--border) !important;
}
.stDataFrame tbody td {
    background: var(--surface) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ── Data editor ── */
.stDataEditor {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Expander ── */
.streamlit-expanderHeader {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
}
.streamlit-expanderContent {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: none !important;
}

/* ── Divider ── */
hr { border-color: var(--border) !important; }

/* ── Date input ── */
.stDateInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}

/* ── Password input ── */
.stTextInput [type="password"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}

/* ── Form container ── */
.stForm {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1rem !important;
}

/* ── Warning / success ── */
div[data-testid="stNotification"] {
    background: var(--surface2) !important;
    border-radius: var(--radius-sm) !important;
}

/* ── Mobile tweaks ── */
@media (max-width: 640px) {
    .block-container { padding: 1rem .75rem 3rem !important; }
    .stat-row { grid-template-columns: repeat(2, 1fr); }
    .class-venue { display: none; }
    .task-type { display: none; }
    .page-header .sub { display: none; }
}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 4. SIDEBAR ---
st.sidebar.markdown("### Admin")
pwd_input = st.sidebar.text_input("Password", type="password", placeholder="Enter password…")
st.session_state.logged_in = (pwd_input == ADMIN_PASSWORD)

if st.session_state.logged_in:
    st.sidebar.success("Authenticated")
else:
    st.sidebar.caption("View-only mode")

menu = ["Dashboard", "Timetable", "Assignments & Tests", "Lab Record Writer"]
choice = st.sidebar.selectbox("Navigate", menu)

# --- 5. DASHBOARD ---
if choice == "Dashboard":
    now = datetime.now()
    current_day = now.strftime("%a").upper()

    st.markdown(f"""
    <div class="page-header">
        <h1>Good {"morning" if now.hour < 12 else "afternoon" if now.hour < 17 else "evening"} 👋</h1>
        <span class="sub">{now.strftime('%A, %d %B %Y')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Stats
    pending_tasks = [t for t in data['tasks'] if not t.get('done', False)]
    total_classes = len([t for t in data['timetable'] if t.get('Day') == current_day])

    # Upcoming deadline countdown
    min_days = None
    for t in pending_tasks:
        try:
            d = datetime.strptime(t['date'], "%Y-%m-%d").date()
            diff = (d - now.date()).days
            if min_days is None or diff < min_days:
                min_days = diff
        except:
            pass

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="label">Today's Classes</div>
            <div class="value blue">{total_classes}</div>
        </div>
        <div class="stat-card">
            <div class="label">Pending Tasks</div>
            <div class="value {'amber' if pending_tasks else 'green'}">{len(pending_tasks)}</div>
        </div>
        <div class="stat-card">
            <div class="label">Next Deadline</div>
            <div class="value {'badge-urgent' if min_days is not None and min_days <= 2 else ''}" style="font-size:1.3rem">
                {f'{min_days}d' if min_days is not None else '—'}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Today's classes
    df_tt = pd.DataFrame(data['timetable'])
    st.markdown('<div class="section-label">Today\'s Schedule</div>', unsafe_allow_html=True)

    if not df_tt.empty:
        today_data = df_tt[df_tt['Day'] == current_day]
        if not today_data.empty:
            rows_html = ""
            for _, row in today_data.iterrows():
                cols = [c for c in row.index if c != 'Day']
                for col in cols:
                    val = row.get(col, "")
                    if val and str(val).strip() and str(val).strip().lower() not in ['nan', 'none', '—', '-']:
                        rows_html += f"""
                        <div class="class-row">
                            <span class="class-time">{col}</span>
                            <span class="class-name">{val}</span>
                        </div>"""
            if rows_html:
                st.markdown(f'<div class="class-list">{rows_html}</div>', unsafe_allow_html=True)
            else:
                st.info("No classes today 🎉")
        else:
            st.info("No classes today 🎉")

        with st.expander("View full weekly schedule"):
            st.dataframe(df_tt, hide_index=True, use_container_width=True)
    else:
        st.warning("No timetable data. Add it in the Timetable tab.")

    # Pending tasks
    st.markdown('<div class="section-label">Upcoming Deadlines</div>', unsafe_allow_html=True)
    if pending_tasks:
        rows_html = ""
        for t in sorted(pending_tasks, key=lambda x: x.get('date', '9999')):
            try:
                d = datetime.strptime(t['date'], "%Y-%m-%d").date()
                diff = (d - now.date()).days
                date_class = "badge-urgent" if diff <= 2 else "badge-soon" if diff <= 5 else "badge-ok"
                date_str = f"in {diff}d" if diff >= 0 else f"{abs(diff)}d ago"
            except:
                date_class = ""
                date_str = t.get('date', '')

            t_type = t.get('type', 'Assignment')
            dot_class = t_type.replace(" ", "\\ ")
            rows_html += f"""
            <div class="task-row">
                <div class="task-dot {t_type}"></div>
                <span class="task-name">{t['name']}</span>
                <span class="task-type">{t_type}</span>
                <span class="task-date {date_class}">{date_str}</span>
            </div>"""
        st.markdown(f'<div class="task-list">{rows_html}</div>', unsafe_allow_html=True)
    else:
        st.success("All caught up — no pending tasks.")

# --- 6. TIMETABLE ---
elif choice == "Timetable":
    st.markdown("""
    <div class="page-header">
        <h1>Timetable</h1>
        <span class="sub">Weekly Schedule</span>
    </div>
    """, unsafe_allow_html=True)

    df_timetable = pd.DataFrame(data['timetable'])
    is_disabled = not st.session_state.logged_in

    edited_df = st.data_editor(
        df_timetable,
        hide_index=True,
        use_container_width=True,
        disabled=is_disabled
    )

    if st.session_state.logged_in:
        if st.button("Save Changes"):
            data['timetable'] = edited_df.to_dict('records')
            save_data(data)
            st.success("Timetable saved.")
    else:
        st.caption("View-only — enter password in sidebar to edit.")

# --- 7. ASSIGNMENTS & TESTS ---
elif choice == "Assignments & Tests":
    st.markdown("""
    <div class="page-header">
        <h1>Assignments & Tests</h1>
        <span class="sub">Deadlines & Tasks</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in:
        with st.form("task_form", clear_on_submit=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                name = st.text_input("Title", placeholder="e.g. DSA Assignment 3")
            with col2:
                t_type = st.selectbox("Type", ["Assignment", "Homework", "Test", "Lab Record"])
            with col3:
                due_date = st.date_input("Due Date")
            submitted = st.form_submit_button("Add Task")
            if submitted and name:
                data['tasks'].append({
                    "name": name,
                    "type": t_type,
                    "date": str(due_date),
                    "done": False
                })
                save_data(data)
                st.rerun()

    # Task list with mark-done and delete
    if data['tasks']:
        st.markdown('<div class="section-label">All Tasks</div>', unsafe_allow_html=True)
        for i, t in enumerate(data['tasks']):
            cols = st.columns([0.05, 0.45, 0.2, 0.15, 0.1, 0.05])
            done = t.get('done', False)
            with cols[0]:
                checked = st.checkbox("", value=done, key=f"done_{i}", label_visibility="collapsed")
                if checked != done:
                    data['tasks'][i]['done'] = checked
                    save_data(data)
                    st.rerun()
            with cols[1]:
                label = f"~~{t['name']}~~" if done else t['name']
                st.markdown(label)
            with cols[2]:
                st.caption(t.get('type', ''))
            with cols[3]:
                st.caption(t.get('date', ''))
            if st.session_state.logged_in:
                with cols[5]:
                    if st.button("✕", key=f"del_{i}", help="Delete"):
                        data['tasks'].pop(i)
                        save_data(data)
                        st.rerun()
    else:
        st.info("No tasks yet.")

# --- 8. LAB RECORDS ---
elif choice == "Lab Record Writer":
    st.markdown("""
    <div class="page-header">
        <h1>Lab Record Writer</h1>
        <span class="sub">Draft & Export</span>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in:
        lab_name = st.text_input("Experiment Name", placeholder="e.g. PN Junction Diode Characteristics")
        content = st.text_area("Record Content", height=320, placeholder="Aim:\n\nApparatus Required:\n\nTheory:\n\nProcedure:\n\nObservations:\n\nResult:")
        col1, col2 = st.columns([1, 3])
        with col1:
            if content and lab_name:
                st.download_button(
                    "Download .txt",
                    data=content,
                    file_name=f"{lab_name.replace(' ', '_')}.txt",
                    mime="text/plain"
                )
    else:
        st.warning("Login via the sidebar to use the Lab Record Writer.")
