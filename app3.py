import streamlit as st
import sqlite3
import hashlib
import ollama
import fitz  # PyMuPDF for PDF text extraction
import pytesseract
from PIL import Image
import io

# Set up Tesseract command (change if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path for your system if needed

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

# Functions for Text Extraction
def extract_text_from_pdf(file):
    """Extracts text from each page of a PDF file using PyMuPDF."""
    pdf_text = ""
    with fitz.open(file) as doc:
        for page in doc:
            pdf_text += page.get_text()
    return pdf_text

def extract_text_from_image(file):
    """Extracts text from an image file using Tesseract OCR."""
    image = Image.open(file)
    return pytesseract.image_to_string(image)

def process_resume(file):
    """Extracts text from the uploaded file, handling PDF, PNG, JPG formats."""
    if file.type == "application/pdf":
        return extract_text_from_pdf(file)
    elif file.type in ["image/png", "image/jpeg"]:
        return extract_text_from_image(file)
    else:
        st.error("Unsupported file format. Please upload a PDF, PNG, or JPG file.")
        return None

# Function for Candidate Evaluation
def evaluate_candidate(resume_text, role, criteria):
    """Evaluates candidate based on the extracted resume text and recruiter-provided criteria using Ollama."""
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': f'Act as an HR specialist hiring for the role of "{role}". Evaluate the candidate based on these criteria: {criteria}. Award marks out of 50.'
        },
        {
            'role': 'user',
            'content': f'{resume_text}\n\nIs this candidate suitable for the "{role}" position?'
        }
    ], stream=True)

    evaluation_text = ""
    for chunk in response:
        evaluation_text += chunk['message']['content']
    
    return evaluation_text


# Streamlit App Layout
st.title("Resume Evaluation App")
st.write("Please log in or sign up as a recruiter to proceed.")

# Create database and table if they don't exist
create_users_table()

# Login or Signup Selection
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Signup/Login Form
if not st.session_state.logged_in:
    option = st.selectbox("Choose an option", ["Login", "Sign Up"])

    if option == "Sign Up":
        new_username = st.text_input("Username", key="signup_username")
        new_password = st.text_input("Password", type='password', key="signup_password")
        confirm_password = st.text_input("Confirm Password", type='password', key="signup_confirm_password")

        if new_password == confirm_password:
            if st.button("Sign Up"):
                signup_user(new_username, new_password)
        else:
            st.warning("Passwords do not match")

    elif option == "Login":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.success("Logged in successfully.")
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("Invalid credentials. Please try again.")

# After Login - Recruiter Criteria and Role Input
if st.session_state.logged_in:
    st.write("## Job Criteria and Role")
    role = st.text_input("Job Role", "Software Developer")
    criteria = st.text_area("Evaluation Criteria", "Technical skills, communication, problem-solving, teamwork, and adaptability")

    uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Extract text from the resume
        resume_text = process_resume(uploaded_file)
        
        if resume_text:
            st.write("### Extracted Resume Text")
            st.write(resume_text)

            # Get evaluation from the Llama model
            st.write("### Evaluation")
            evaluation = evaluate_candidate(resume_text, role, criteria)
            st.write(evaluation)
