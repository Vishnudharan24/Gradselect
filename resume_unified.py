from PIL import Image
import pytesseract
import ollama
import re

# Set the path to your Tesseract executable if needed (for Windows users)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    """
    Extracts text from an image using Tesseract OCR.
    """
    # Load the image and extract text
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, config='--psm 6')
    return text

def extract_keywords(text):
    """
    Extracts keywords from the text based on specific patterns.
    """
    # Regex pattern to match lines that start with either a number, a bullet point, or nothing, followed by a word or phrase
    pattern = r"(?:\d+\.|\*|-)?\s*(\b[A-Za-z][A-Za-z\s\(\)]*\b)"
    matches = re.findall(pattern, text)
    keywords = [match.strip() for match in matches if match.strip()]
    return keywords

def get_field_of_interest_conclusion(received_message):
    """
    Sends the extracted text to an AI model to retrieve the candidate's fields of interest.
    """
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': 'just give me the words of field of interest (e.g., full stack) from the given text without adding any precontext; just give me the words'
        },
        {
            'role': 'user',
            'content': received_message
        }
    ])

    return response

def analyze_resume(text):
    """
    Uses an AI model to extract and categorize structured information from a resume text.
    """
    response = ollama.chat(model='llama3.1', messages=[
        {
            'role': 'system',
            'content': '''You are an assistant designed to extract and format structured information from resumes. Given the text from a resume, parse and categorize information strictly according to the following format:

Technical Keywords: The first line should list all relevant technical keywords and domains, including job roles (e.g., "Full Stack Developer," "DevOps Engineer," "Cloud Developer") and technical skills (e.g., "JavaScript," "React," "AWS," "Kubernetes"). Separate each keyword with a comma.

Certifications: The second line should list all certifications, if any (e.g., "AWS Certified Solutions Architect," "Google Cloud Professional Data Engineer"). Separate each certification with a comma.

Experience Level: The third line should include keywords indicating experience level (e.g., "expert," "proficient," "5+ years") and relevant work experience or expertise. Separate each experience detail with a comma.

Education: The fourth line should list formal education details (e.g., "B.S. in Computer Science," "M.S. in Data Science").

Projects: The fifth line should provide a brief summary of significant projects, including the project name, purpose, and technologies used (e.g., "Developed e-commerce platform using Django and React").

Each line should strictly contain only the specified category and omit non-relevant information. Adhere to the line-by-line format exactly to ensure consistency in structured output.'''
        },
        {
            'role': 'user',
            'content': text
        }
    ], stream=True)
    
    # Collect response in real-time from stream
    stream_input = []
    for small_chunk in response:
        small_word = small_chunk['message']['content']
        stream_input.append(small_word)

    # Combine streamed response into a single string
    generated_string = ''.join(stream_input)
    return generated_string

# Main Execution Flow
if __name__ == "__main__":
    image_path = 'resume.webp'  # Replace with the path to your resume image
    # Step 1: Extract text from the resume image
    extracted_text = extract_text_from_image(image_path)
    print("Extracted Text from Resume:\n", extracted_text)

    # Step 2: Analyze extracted text using AI model
    structured_output = analyze_resume(extracted_text)
    print("\nStructured Output:\n", structured_output)

    # Step 3: Extract conclusion based on fields of interest
    conclusion = get_field_of_interest_conclusion(structured_output)
    print("\nField of Interest Conclusion:\n", conclusion['message']['content'])
