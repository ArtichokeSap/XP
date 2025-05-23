import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
from xp_tracker import User, Task
import os

# File to store last loaded user
LAST_USER_FILE = "last_user.txt"

# Initialize User and load last user
if 'user' not in st.session_state:
    st.session_state.user = User()
    if os.path.exists(LAST_USER_FILE):
        with open(LAST_USER_FILE, 'r') as f:
            last_user = f.read().strip()
        if last_user and os.path.exists(f"{last_user}.json"):
            st.session_state.user.load_from_json(f"{last_user}.json")
            st.session_state.current_user = last_user
        else:
            st.session_state.current_user = "default"
    else:
        st.session_state.current_user = "default"

user = st.session_state.user

# Reduce whitespace
st.set_page_config(layout="wide")

# Sidebar for user management
with st.sidebar:
    st.subheader("User Management")
    user_name = st.text_input("User Name", value=st.session_state.current_user, placeholder="Enter user name")
    if st.button("Save User"):
        if user_name:
            st.session_state.current_user = user_name
            user.save_to_json(f"{user_name}.json")
            with open(LAST_USER_FILE, 'w') as f:
                f.write(user_name)
            st.success(f"Saved user: {user_name}")
        else:
            st.error("Please enter a user name.")
    if st.button("Load User"):
        if user_name and os.path.exists(f"{user_name}.json"):
            user.tasks = []
            user.load_from_json(f"{user_name}.json")
            st.session_state.current_user = user_name
            with open(LAST_USER_FILE, 'w') as f:
                f.write(user_name)
            st.success(f"Loaded user: {user_name}")
        else:
            st.error(f"User {user_name} not found.")

# Split layout into two columns
col1, col2 = st.columns([1, 1])

# Left pane for inputs and recent tasks
with col1:
    st.subheader("Add Task", help=None)
    
    # Apply CSS to reduce spacing in the form
    st.markdown(
        """
        <style>
        /* Target the form container to reduce spacing between elements */
        div[data-testid="stForm"] > div > div {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
        /* Target the radio widget's parent container */
        div.row-widget.stRadio {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
        /* Target the horizontal radio group specifically */
        div[data-testid="stHorizontalBlock"] {
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    with st.form(key="task_form", clear_on_submit=False):
        # Row 1: Description, Category, Date
        row1 = st.columns([2, 1, 1])
        with row1[0]:
            desc = st.text_input("Description", placeholder="Enter task description")
        with row1[1]:
            categories = ['none', 'Music', 'Typing']
            cat = st.selectbox("Category", categories, index=0)
        with row1[2]:
            date = st.date_input("Date", value=datetime.now())
        
        # Row 2: Radio buttons for Stats
        stats = ['Body', 'Mind', 'Art', 'Tech', 'Home', 'Spirit']
        stat_colors = {'Body': 'red', 'Mind': 'magenta', 'Art': 'green', 'Tech': 'darkblue', 'Home': 'orange', 'Spirit': 'purple'}
        stat = st.radio(
            "Stat",
            stats,
            index=0,
            format_func=lambda x: f"{x}",
            horizontal=True
        )
        # Apply CSS to color radio buttons
        for s in stats:
            st.markdown(
                f"<style>input[type='radio'][value='{s}'] + div {{ color: {stat_colors[s]} !important; }}</style>",
                unsafe_allow_html=True
            )
        
        # Row 3: Minutes, Outside, Submit, Undo
        row3 = st.columns([1, 1, 1, 1])
        with row3[0]:
            minutes = st.number_input("Minutes", min_value=0, step=1, value=0, label_visibility="visible")
        with row3[1]:
            st.markdown(
                "<div style='display: flex; justify-content: center; align-items: center; padding: 0px;'>",
                unsafe_allow_html=True
            )
            outside = st.checkbox("Outside", label_visibility="visible")
            st.markdown("</div>", unsafe_allow_html=True)
        with row3[2]:
            st.markdown(
                "<div style='display: flex; justify-content: center; align-items: center; padding: 0px;'>",
                unsafe_allow_html=True
            )
            submit_clicked = st.form_submit_button("Submit")
            st.markdown("</div>", unsafe_allow_html=True)
        with row3[3]:
            st.markdown(
                "<div style='display: flex; justify-content: center; align-items: center; padding: 0px;'>",
                unsafe_allow_html=True
            )
            undo_clicked = st.form_submit_button("Undo")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Row 4: Feedback
    if submit_clicked:
        if desc and minutes > 0:
            try:
                task = Task(name=desc, category=cat, duration=int(minutes), stat=stat, date=date, outside=outside)
                user.add_task(task)
                user.save_to_json(f"{st.session_state.current_user}.json")
                st.success(f"Added: {desc} ({minutes} min)")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please provide a description and valid minutes.")
    if undo_clicked:
        user.undo()
        user.save_to_json(f"{st.session_state.current_user}.json")
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
                "Outside": "Yes" if t.outside else "No",
                "Chain": f"x{min(len(user.streaks.get(t.category, [])) + 1, 3)}" if t.category in ['Music', 'Typing'] else "x1",
                "XP": t.duration * (2 if t.outside else 1) * (min(len(user.streaks.get(t.category, [])) + 1, 3) if t.category in ['Music', 'Typing'] else 1)
            }
            for t in user.tasks[-5:]
        ]
        df = pd.DataFrame(task_data)[["Date", "Description", "Category", "Stat", "Time", "Outside", "Chain", "XP"]]
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
    
    # XP Trend plot (Cumulative XP over time)
    st.subheader("XP Trend", help=None)
    if user.tasks:
        sorted_tasks = sorted(user.tasks, key=lambda t: t.date)
        # Calculate cumulative XP
        df_data = []
        cumulative_xp = 0
        for t in sorted_tasks:
            xp = t.duration * (2 if t.outside else 1) * (min(len(user.streaks.get(t.category, [])) + 1, 3) if t.category in ['Music', 'Typing'] else 1)
            cumulative_xp += xp
            df_data.append({
                "Date": t.date,
                "XP": cumulative_xp,
                "Task": t.name
            })
        df = pd.DataFrame(df_data)
        fig = go.Figure(data=go.Scatter(
            x=df['Date'],
            y=df['XP'],
            mode='lines+markers',
            text=df['Task'],
            hoverinfo='text+x+y'
        ))
        fig.update_layout(
            title="Cumulative XP Over Time",
            xaxis_title="Date",
            yaxis_title="Cumulative XP",
            xaxis_title_font=dict(size=32, weight='bold'),
            yaxis_title_font=dict(size=32, weight='bold'),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})
    else:
        st.write("No data to plot yet.")