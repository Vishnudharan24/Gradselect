import streamlit as st
import ollama
import fitz  # PyMuPDF for PDF text extraction
import pytesseract
from PIL import Image
import io

# Set up Tesseract command (change if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update path for your system if needed

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

def evaluate_candidate(resume_text):
    """Evaluates candidate based on the extracted resume text using Ollama."""
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': f'Act as an HR specialist hiring for the role of "{role}". Evaluate the candidate based on these criteria: {criteria}. Award marks out of 50.'
        },
        {
            'role': 'user',
            'content': f'{resume_text}\n\nIs this candidate worth recruiting? Evaluate based on at least 5 criteria and award marks out of 50.'
        }
    ], stream=True)

    evaluation_text = ""
    for chunk in response:
        evaluation_text += chunk['message']['content']
    
    return evaluation_text

# Streamlit App Layout
st.title("Resume Evaluation App")
st.write("Upload a resume in PDF, JPG, or PNG format to receive an evaluation.")

uploaded_file = st.file_uploader("Upload Resume", type=["pdf", "jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Extract text from the resume
    resume_text = process_resume(uploaded_file)
    
    if resume_text:
        st.write("### Extracted Resume Text")
        st.write(resume_text)

        # Get evaluation from the Llama model
        st.write("### Evaluation")
        evaluation = evaluate_candidate(resume_text)
        st.write(evaluation)
