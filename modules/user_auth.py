import hashlib
import sqlite3
import os
import streamlit as st
import re
import time
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, filename='auth.log', 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize the database
def init_auth_db():
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/users.db', timeout=10)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
     username TEXT UNIQUE NOT NULL,
     password_hash TEXT NOT NULL,
     email TEXT UNIQUE NOT NULL,
     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
    ''')
    conn.commit()
    conn.close()

# Hash password for secure storage
def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex() + ':' + key.hex()

def verify_password(stored_hash, provided_password):
    salt_hex, key_hex = stored_hash.split(':')
    salt = bytes.fromhex(salt_hex)
    key = hashlib.pbkdf2_hmac('sha256', provided_password.encode(), salt, 100000)
    return key.hex() == key_hex

# Register a new user
def register_user(username, password, email):
    try:
        conn = sqlite3.connect('data/users.db', timeout=10)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return False, "Username already exists"
        c.execute("SELECT * FROM users WHERE email = ?", (email,))
        if c.fetchone():
            conn.close()
            return False, "Email already exists"
        password_hash = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash, email) VALUES (?, ?, ?)",
                 (username, password_hash, email))
        conn.commit()
        conn.close()
        logging.info(f"User {username} registered successfully")
        return True, "Registration successful"
    except sqlite3.Error as e:
        logging.error(f"Database error during registration for {username}: {str(e)}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error during registration for {username}: {str(e)}")
        return False, f"Error during registration: {str(e)}"

# Authenticate user
def login_user(username, password):
    try:
        conn = sqlite3.connect('data/users.db', timeout=10)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        conn.close()
        if not user:
            logging.warning(f"Login attempt failed: Invalid username {username}")
            return False, "Invalid username"
        stored_password = user[2]  # password_hash
        if verify_password(stored_password, password):
            logging.info(f"User {username} logged in successfully")
            return True, "Login successful"
        else:
            logging.warning(f"Login attempt failed for {username}: Invalid password")
            return False, "Invalid password"
    except sqlite3.Error as e:
        logging.error(f"Database error during login for {username}: {str(e)}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error during login for {username}: {str(e)}")
        return False, f"Error during login: {str(e)}"

# Delete a user by username
def delete_user(username):
    """
    Delete a user from the database.
    Returns tuple (success: bool, message: str)
    """
    conn = None
    try:
        # Ensure we're not deleting admin
        if username.lower() == 'admin':
            return False, "Cannot delete admin account"
            
        conn = sqlite3.connect('data/users.db', timeout=10)
        c = conn.cursor()
        
        # First check if user exists
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = c.fetchone()
        if not user:
            return False, "User not found"
        
        # Delete the user
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        
        # Verify deletion
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone() is None:
            logging.info(f"User {username} deleted successfully")
            return True, "User deleted successfully"
        else:
            logging.error(f"Failed to delete user {username}")
            return False, "Failed to delete user"
            
    except sqlite3.Error as e:
        logging.error(f"Database error deleting user {username}: {str(e)}")
        return False, f"Database error: {str(e)}"
    except Exception as e:
        logging.error(f"Unexpected error deleting user {username}: {str(e)}")
        return False, f"Error: {str(e)}"
    finally:
        try:
            if conn:
                conn.close()
        except Exception as e:
            logging.error(f"Error closing connection: {str(e)}")

# Display login page
def login_page():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    remember_me = st.checkbox("Remember me", key="remember_me")
    if st.button("Login", key="login_button"):
        if username and password:
            success, message = login_user(username, password)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = username
                if remember_me:
                    st.session_state.session_expiry = time.time() + (30 * 24 * 60 * 60)  # 30 days
                else:
                    st.session_state.session_expiry = time.time() + (2 * 60 * 60)  # 2 hours
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Please enter both username and password")

# Display signup page
def signup_page():
    st.subheader("Create New Account")
    username = st.text_input("Username", key="signup_username")
    email = st.text_input("Email", key="signup_email")
    password = st.text_input("Password", type="password", key="signup_password")
    confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm_password")
    if st.button("Sign Up", key="signup_button"):
        if username and email and password and confirm_password:
            valid_username, username_msg = is_valid_username(username)
            if not valid_username:
                st.error(username_msg)
                return
            if not is_valid_email(email):
                st.error("Please enter a valid email address")
                return
            valid_password, password_msg = is_strong_password(password)
            if not valid_password:
                st.error(password_msg)
                return
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            success, message = register_user(username, password, email)
            if success:
                st.success(message)
                st.balloons()
                st.info("Please login with your new account")
            else:
                st.error(message)
        else:
            st.warning("Please fill out all fields")

# Display logout button
def logout():
    if st.sidebar.button("Logout", key="logout_button"):
        st.session_state.logged_in = False
        st.session_state.username = None
        if 'session_expiry' in st.session_state:
            del st.session_state.session_expiry
        st.rerun()

def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    if not (has_upper and has_lower and has_digit and has_special):
        return False, "Password must include uppercase, lowercase, numbers, and special characters"
    return True, "Password meets strength requirements"

def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_username(username):
    if len(username) < 3 or len(username) > 20:
        return False, "Username must be between 3 and 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Valid username"