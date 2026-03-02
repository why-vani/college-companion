import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

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
    st.subheader(f"📅 Today: {datetime.now().strftime('%A, %d %B')}")
    # Filter pending tasks
    pending = [t for t in data['tasks'] if not t.get('done', False)]
    st.metric("Pending Tasks", len(pending))
    if pending:
        st.write("Upcoming Deadlines:")
        st.table(pd.DataFrame(pending).head(3))

# --- TIMETABLE ---
elif choice == "Timetable":
    st.subheader("🗓️ NMAMIT Semester II Timetable (Section Y)")
    
    # Create the DataFrame
    df_timetable = pd.DataFrame(data['timetable'])
    
    # Display the table with specific formatting
    st.write("Click any cell to edit your classes:")
    edited_df = st.data_editor(
        df_timetable, 
        hide_index=True, 
        use_container_width=True,
        column_config={
            "Day": st.column_config.TextColumn("Day", disabled=True),
            "1.00-1.55": st.column_config.TextColumn("Lunch Break", disabled=True)
        }
    )
    
    if st.button("💾 Save All Changes"):
        data['timetable'] = edited_df.to_dict('records')
        save_data(data)
        st.success("Timetable updated successfully!")

    st.divider()
    st.info("💡 Note: (SL) stands for Self Learning sessions.")
# --- ASSIGNMENTS & TESTS ---
elif choice == "Assignments & Tests":
    st.subheader("📝 Assignments, Homework & Tests")
    
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
            st.rerun()

    if data['tasks']:
        df = pd.DataFrame(data['tasks'])
        st.dataframe(df, use_container_width=True)
        if st.button("Clear All Completed"):
            # Logic to clear can be added here
            pass

# --- LAB RECORDS ---
elif choice == "Lab Record Writer":
    st.subheader("🧪 Lab Record Draftsman")
    lab_name = st.text_input("Experiment Name")
    content = st.text_area("Write your record here...", height=300)
    
    if st.button("Save Draft"):
        st.info("Draft ready for download!")
        st.download_button("Download .txt", content, file_name=f"{lab_name}.txt")
