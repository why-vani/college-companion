import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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

# lol nigga u really expect me to be this dumb 😭
# This line now pulls the password from the hidden 'Secrets' menu
ADMIN_PASSWORD = st.secrets["password"]

st.set_page_config(
    page_title="NMAMIT Companion", 
    page_icon="🎓", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.title("🔐 Admin Access")
pwd_input = st.sidebar.text_input("Enter Password", type="password")
st.session_state.logged_in = (pwd_input == ADMIN_PASSWORD)

# --- 3. NAVIGATION ---
menu = ["Dashboard", "Timetable", "Assignments & Tests", "Lab Record Writer"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- 4. DASHBOARD ---
if choice == "Dashboard":
    st.subheader(f"📅 Today: {datetime.now().strftime('%A, %d %B %Y')}")
    
    current_day = datetime.now().strftime("%a").upper() # Gets MON, TUE, etc.
    df_timetable = pd.DataFrame(data['timetable'])

    if not df_timetable.empty:
        # Show today's specific classes vertically for mobile
        today_data = df_timetable[df_timetable['Day'] == current_day]
        if not today_data.empty:
            st.markdown(f"### 📖 Today's Classes ({current_day})")
            st.table(today_data.set_index('Day').T)
        else:
            st.info("No classes scheduled for today! 🎉")
            
        with st.expander("🔍 View Full Weekly Schedule"):
            st.dataframe(df_timetable, hide_index=True, use_container_width=True)
    else:
        st.warning("Timetable is empty. Go to 'Timetable' tab to add your schedule.")

    st.divider()
    st.markdown("### 🔔 Upcoming Deadlines")
    pending = [t for t in data['tasks'] if not t.get('done', False)]
    if pending:
        st.dataframe(pd.DataFrame(pending), use_container_width=True, hide_index=True)
    else:
        st.success("All caught up! No pending assignments.")

# --- 5. TIMETABLE ---
elif choice == "Timetable":
    st.subheader("🗓️ NMAMIT Weekly Schedule")
    df_timetable = pd.DataFrame(data['timetable'])
    
    is_disabled = not st.session_state.logged_in
    
    edited_df = st.data_editor(
        df_timetable, 
        hide_index=True, 
        use_container_width=True,
        disabled=is_disabled 
    )
    
    if st.session_state.logged_in:
        if st.button("💾 Save All Changes"):
            data['timetable'] = edited_df.to_dict('records')
            save_data(data)
            st.success("Timetable updated successfully!")
    else:
        st.warning("⚠️ View Only Mode. Enter password in sidebar to edit.")

# --- 6. ASSIGNMENTS & TESTS ---
elif choice == "Assignments & Tests":
    st.subheader("📝 Assignments & Deadlines")
    
    if st.session_state.logged_in:
        with st.form("task_form"):
            name = st.text_input("Task Title")
            t_type = st.selectbox("Category", ["Assignment", "Homework", "Test", "Lab Record"])
            date = st.date_input("Due Date")
            if st.form_submit_button("Add Task") and name:
                data['tasks'].append({"name": name, "type": t_type, "date": str(date), "done": False})
                save_data(data)
                st.rerun()
    
    if data['tasks']:
        st.dataframe(pd.DataFrame(data['tasks']), use_container_width=True, hide_index=True)

# --- 7. LAB RECORDS ---
elif choice == "Lab Record Writer":
    st.subheader("🧪 Lab Record Draftsman")
    if st.session_state.logged_in:
        lab_name = st.text_input("Experiment Name")
        content = st.text_area("Write your record here...", height=300)
        if st.button("Download .txt"):
            st.download_button("Click to Download", content, file_name=f"{lab_name}.txt")
    else:
        st.warning("🔒 Login to use the Lab Record Writer.")
