import sqlite3
import streamlit as st
import hashlib

# Database Connection Setup
def create_connection():
    conn = sqlite3.connect('users.db')
    return conn

# Initialize the Database and Create Users Table
def create_users_table():
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

# Hash Password Function
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Signup Function
def signup_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    try:
        hashed_password = hash_password(password)
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        st.success("Account created successfully!")
    except sqlite3.IntegrityError:
        st.error("Username already exists. Please choose another username.")
    finally:
        conn.close()

# Login Function
def login_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    hashed_password = hash_password(password)
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, hashed_password))
    user = cursor.fetchone()
    conn.close()
    return user

# Streamlit Application with Signup and Login
def main():
    st.title("Signup and Login App")
    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Create database and table if they don't exist
    create_users_table()

    if choice == "Login":
        st.subheader("Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success(f"Welcome {username}!")
                st.session_state.logged_in = True
            else:
                st.error("Invalid Username or Password")
    
    elif choice == "Sign Up":
        st.subheader("Create New Account")

        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type='password', key="signup_password")
        confirm_password = st.text_input("Confirm Password", type='password', key="signup_confirm_password")

        if new_password == confirm_password:
            if st.button("Sign Up"):
                signup_user(new_username, new_password)
        else:
            st.warning("Passwords do not match")

# Run the app
if __name__ == '__main__':
    main()
