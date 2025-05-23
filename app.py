import streamlit as st

# Initialize session state for login status
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Define a simple authentication function (replace with your own logic)
def authenticate(username, password):
    # Example: Hardcoded credentials (replace with secure storage/database)
    return username == "admin" and password == "password"

# Login page logic
def login_page():
    st.title("Login to XP Tracker")
    
    # If already logged in, redirect to the main app
    if st.session_state.logged_in:
        st.switch_page("pages/xp_tracker_app.py")
    
    # Login form
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.switch_page("pages/xp_tracker_app.py")
        else:
            st.error("Invalid username or password")

# Run the login page
if __name__ == "__main__":
    login_page()