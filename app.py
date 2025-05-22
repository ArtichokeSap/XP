import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from xp_tracker import User, Task

# Initialize User and load data
if 'user' not in st.session_state:
    st.session_state.user = User()
    try:
        st.session_state.user.load_from_json("user_data.json")
    except FileNotFoundError:
        pass

user = st.session_state.user

# Reduce whitespace
st.set_page_config(layout="wide")

# Split layout into two columns
col1, col2 = st.columns([1, 1])

# Left pane for inputs and recent tasks
with col1:
    st.subheader("Add Task", help=None)
    desc = st.text_input("Description", placeholder="Enter task description")
    categories = ['typing', 'piano', 'reading', 'exercise', 'cleaning']
    cat = st.selectbox("Category", categories, index=0)
    stats = ['Body', 'Mind', 'Art', 'Tech', 'Home', 'Spirit']
    stat = st.selectbox("Stat", stats, index=0)
    minutes = st.number_input("Minutes", min_value=0, step=1, value=0)
    date = st.date_input("Date", value=datetime.now())
    if st.button("Submit"):
        if desc and minutes > 0:
            try:
                task = Task(name=desc, category=cat, duration=int(minutes), stat=stat, date=date)
                user.add_task(task)
                user.save_to_json("user_data.json")
                st.success(f"Added: {desc} ({minutes} min)")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please provide a description and valid minutes.")
    if st.button("Undo"):
        user.undo()
        user.save_to_json("user_data.json")
        st.success("Last action undone.")
    
    # Recent tasks at bottom of left pane
    st.subheader("Recent Tasks", help=None)
    if user.tasks:
        task_data = [
            {
                "Date": t.date,
                "Description": t.name,
                "Category": t.category,
                "Stat": t.stat,
                "Time": t.duration,
                "Chain": f"x{min(len(user.streaks.get(t.category, [])) + 1, 3)}" if t.category in ['typing', 'piano'] else "x1",
                "XP": t.duration * (min(len(user.streaks.get(t.category, [])) + 1, 3) if t.category in ['typing', 'piano'] else 1)
            }
            for t in user.tasks[-5:]
        ]
        df = pd.DataFrame(task_data)[["Date", "Description", "Category", "Stat", "Time", "Chain", "XP"]]  # Explicit column order
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.write("No tasks yet.")

# Right pane for outputs
with col2:
    st.markdown(f"<h1 style='margin-top: 0; margin-bottom: 10px;'>Total XP: {user.xp}</h1>", unsafe_allow_html=True)
    
    # XP by Stat bar chart
    if user.tasks:
        stat_colors = {'Body': 'red', 'Mind': 'magenta', 'Art': 'green', 'Tech': 'darkblue', 'Home': 'orange', 'Spirit': 'purple'}
        fig = go.Figure(data=go.Bar(
            x=list(user.stats.keys()),
            y=list(user.stats.values()),
            marker_color=[stat_colors[stat] for stat in user.stats.keys()],
            text=list(user.stats.values()),
            textposition='auto',
            textfont=dict(size=16, weight='bold')
        ))
        fig.update_layout(
            xaxis_title="Stat",
            yaxis_title="XP",
            xaxis_title_font=dict(size=32, weight='bold'),
            yaxis_title_font=dict(size=32, weight='bold'),
            yaxis=dict(autorange=True),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
    else:
        st.write("No stat data to plot yet.")
    
    # XP Trend plot
    st.subheader("XP Trend", help=None)
    if user.tasks:
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
            yaxis_title="XP",
            xaxis_title_font=dict(size=32, weight='bold'),
            yaxis_title_font=dict(size=32, weight='bold'),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
    else:
        st.write("No data to plot yet.")