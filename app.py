import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# --- 1. SETTINGS & PASSWORD ---
ADMIN_PASSWORD = "nmamit_admin"  # Change this to your secret password!

# Initialize session state for login if it doesn't exist
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- 2. SIDEBAR LOGIN ---
st.sidebar.title("🔐 Admin Access")
pwd_input = st.sidebar.text_input("Enter Password", type="password")

if pwd_input == ADMIN_PASSWORD:
    st.session_state.logged_in = True
    st.sidebar.success("Logged In! You can now edit.")
else:
    st.session_state.logged_in = False
    if pwd_input != "":
        st.sidebar.error("Incorrect Password")

# use this to make it phone friendly
st.set_page_config(
    page_title="College Companion",
    page_icon="🎓",
    layout="wide", # This helps the timetable fit on the screen
    initial_sidebar_state="collapsed" # Hides the sidebar by default on mobile
)

# --- DATA HANDLING ---
def load_data():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as f:
            return json.load(f)
    return {"timetable": {}, "tasks": [], "labs": []}

def save_data(data):
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)

data = load_data()

# --- UI SETUP ---
st.set_page_config(page_title="College Companion", page_icon=":")
st.title("🎓 My College Hub")

menu = ["Dashboard", "Timetable", "Assignments & Tests", "Lab Record Writer"]
choice = st.sidebar.selectbox("Navigation", menu)

# --- DASHBOARD ---
if choice == "Dashboard":
    st.subheader(f"📅 {datetime.now().strftime('%A, %d %B')}")
    
    current_day = datetime.now().strftime("%a").upper() # Gets MON, TUE, etc.
    df_timetable = pd.DataFrame(data['timetable'])

    # Filter to show ONLY today's classes
    today_data = df_timetable[df_timetable['Day'] == current_day]

    if not today_data.empty:
        st.markdown(f"### 📖 Today's Classes ({current_day})")
        # Transpose the table so times are in rows (perfect for phone scrolling)
        df_today = today_data.set_index('Day').T
        st.dataframe(df_today, use_container_width=True)
    else:
        st.info("No classes scheduled for today! 🎉")
    
    st.divider()
    with st.expander("🔍 View Full Weekly Schedule"):
        st.dataframe(df_timetable, hide_index=True)
    # 2. Show Pending Tasks
    st.markdown("### 🔔 Upcoming Deadlines")
    pending = [t for t in data['tasks'] if not t.get('done', False)]
    
    if pending:
        col1, col2 = st.columns([1, 3])
        col1.metric("Pending", len(pending))
        st.dataframe(pd.DataFrame(pending), use_container_width=True, hide_index=True)
    else:
        st.success("All caught up! No pending assignments.")

# 1. SIDEBAR LOGIN (At the top of your script)
ADMIN_PASSWORD = "nmamit_admin" 

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.sidebar.title("🔐 Admin Access")
pwd_input = st.sidebar.text_input("Enter Password", type="password")
st.session_state.logged_in = (pwd_input == ADMIN_PASSWORD)

# ... (Dashboard code stays the same) ...

# 2. THE PROTECTED TIMETABLE SECTION (Replace your old one with this)
elif choice == "Timetable":
    st.subheader("🗓️ NMAMIT Weekly Schedule")
    
    df_timetable = pd.DataFrame(data['timetable'])
    
    # This checks if you are logged in. If not, 'disabled' becomes True.
    is_disabled = not st.session_state.logged_in
    
    # The table is now locked for anyone without the password
    edited_df = st.data_editor(
        df_timetable, 
        hide_index=True, 
        use_container_width=True,
        disabled=is_disabled 
    )
    
    # Only show the Save button if logged in
    if st.session_state.logged_in:
        if st.button("💾 Save All Changes"):
            data['timetable'] = edited_df.to_dict('records')
            save_data(data)
            st.success("Timetable updated successfully!")
    else:
        st.warning("⚠️ View Only Mode. Enter password in sidebar to edit.")

# --- ASSIGNMENTS & TESTS SECTION ---
elif choice == "Assignments & Tests":
    st.subheader("📝 Assignments, Homework & Tests")
    
    # 1. Input Form (ONLY visible if logged in)
    if st.session_state.logged_in:
        with st.form("task_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Task Title")
                t_type = st.selectbox("Category", ["Assignment", "Homework", "Test", "Lab Record"])
            with col2:
                date = st.date_input("Due Date")
                submit = st.form_submit_button("Add Task")

            if submit and name:
                data['tasks'].append({"name": name, "type": t_type, "date": str(date), "done": False})
                save_data(data)
                st.success("Task added!")
                st.rerun()
    else:
        st.info("ℹ️ Login via the sidebar to add new assignments or tests.")

    # 2. Display the List (Always visible to everyone)
    if data['tasks']:
        st.markdown("### Current Deadlines")
        df_tasks = pd.DataFrame(data['tasks'])
        st.dataframe(df_tasks, use_container_width=True, hide_index=True)
        
        # Admin-only delete option
        if st.session_state.logged_in and st.button("🗑️ Clear All Tasks"):
            data['tasks'] = []
            save_data(data)
            st.rerun()

# --- LAB RECORD WRITER SECTION ---
elif choice == "Lab Record Writer":
    st.subheader("🧪 Lab Record Draftsman")
    
    if st.session_state.logged_in:
        lab_name = st.text_input("Experiment Name")
        content = st.text_area("Write your record here...", height=300)
        
        if st.button("Save Draft"):
            st.info("Draft ready for download!")
            st.download_button("Download .txt", content, file_name=f"{lab_name}.txt")
    else:
        st.warning("🔒 This feature is locked. Please log in to write and save lab records.")
