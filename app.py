import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from xp_tracker import User, Task  # Import your backend

# Initialize User and load data
if 'user' not in st.session_state:
    st.session_state.user = User()
    try:
        st.session_state.user.load_from_json("user_data.json")
    except FileNotFoundError:
        pass  # File may not exist initially

user = st.session_state.user

# Streamlit UI
st.title("XP Tracker")

# Entry Section
st.subheader("Add Task")

# Task description
desc = st.text_input("Description", placeholder="Enter task description")

# Category dropdown
categories = ['typing', 'piano', 'reading', 'exercise', 'cleaning']
cat = st.selectbox("Category", categories, index=0)

# Stat dropdown
stats = ['Body', 'Mind', 'Art', 'Tech', 'Home', 'Spirit']
stat = st.selectbox("Stat", stats, index=0)

# Minutes input
minutes = st.number_input("Minutes", min_value=0, step=1, value=0)

# Date picker
date = st.date_input("Date", value=datetime.now())

# Submit button
if st.button("Submit"):
    if desc and minutes > 0:
        try:
            task = Task(
                name=desc,
                category=cat,
                duration=int(minutes),
                stat=stat,
                date=date
            )
            user.add_task(task)
            user.save_to_json("user_data.json")
            st.success(f"Added: {desc} ({minutes} min)")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please provide a description and valid minutes.")

# Undo button
if st.button("Undo"):
    user.undo()
    user.save_to_json("user_data.json")
    st.success("Last action undone.")

# Stats display
st.subheader("Stats")
stats_text = f"XP: {user.xp}\nLevel: {user.level}\n" + "\n".join(f"{k}: {v}" for k, v in user.stats.items())
st.text(stats_text)

# Recent tasks display
st.subheader("Recent Tasks")
if user.tasks:
    task_data = [
        {"Date": t.date, "Description": t.name, "Duration (min)": t.duration, "Category": t.category, "Stat": t.stat}
        for t in user.tasks[-5:]  # Last 5 tasks
    ]
    df = pd.DataFrame(task_data)
    st.dataframe(df, use_container_width=True)
else:
    st.write("No tasks yet.")

# Static Plotly plot for XP trend
st.subheader("XP Trend")
if user.tasks:
    # Sort tasks by date to ensure chronological order
    sorted_tasks = sorted(user.tasks, key=lambda t: t.date)
    df = pd.DataFrame([
        {
            "Date": t.date,
            "XP": t.duration * (min(len(user.streaks.get(t.category, [])) + 1, 3) if t.category in ['typing', 'piano'] else 1)
        }
        for t in sorted_tasks
    ])
    fig = go.Figure(data=go.Scatter(
        x=df['Date'],
        y=df['XP'],
        mode='lines+markers',
        text=[t.name for t in sorted_tasks],
        hoverinfo='text+x+y'
    ))
    fig.update_layout(
        title="XP Over Time",
        xaxis_title="Date",
        yaxis_title="XP"
    )
    st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
else:
    st.write("No data to plot yet.")