import streamlit as st
import google.generativeai as genai
import os
import PyPDF2 as pdf
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()

# Configure API key from environment variable
api_key = os.getenv("API_KEY")  # Ensure you have set this in your .env file
if api_key is None:
    st.error("API key is missing. Please check your .env file.")
else:
    genai.configure(api_key=api_key)

def get_gemini_response(input_prompt):
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(input_prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

def input_pdf_text(uploaded_file):
    """Extract text from the uploaded PDF file."""
    reader = pdf.PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:  # Check if text extraction was successful
            text += extracted_text + "\n"  # Add a newline for better formatting
    return text.strip()  # Remove any leading/trailing whitespace

# Prompt Template
input_prompt = """
Hey Act Like a skilled or very experienced ATS (Application Tracking System)
with a deep understanding of tech fields, software engineering, data science, data analysis,
and big data engineering. Your task is to evaluate the resume based on the given job description.
You must consider the job market is very competitive and you should provide 
the best assistance for improving the resumes. Assign the percentage matching based 
on the JD and
the missing keywords with high accuracy.
resume: {text}
description: {jd}

I want the response in one single string having the structure
{{"JD Match":"%","MissingKeywords":[],"Profile Summary":""}}
"""

# Streamlit app
st.title("Smart ATS")
st.text("Improve Your Resume ATS")
jd = st.text_area("Paste the Job Description")
uploaded_file = st.file_uploader("Upload Your Resume", type="pdf", help="Please upload a PDF.")

submit = st.button("Submit")

if submit:
    if uploaded_file is not None:
        text = input_pdf_text(uploaded_file)
        if text:  # Ensure that text was extracted successfully
            response = get_gemini_response(input_prompt.format(text=text, jd=jd))
            if response:
                try:
                    response_json = json.loads(response)
                    st.header("Resume Analysis")
                    
                    # Missing Keywords
                    st.subheader("Missing Keywords")
                    missing_keywords = response_json.get("MissingKeywords", [])
                    st.write("• " + "\n• ".join(sorted(missing_keywords)))

                    # About the Resume
                    st.subheader("About the Resume")
                    profile_summary = response_json.get("Profile Summary", "")
                    candidate_skills = [skill.strip() for skill in profile_summary.split(",")]
                    st.write("• " + "\n• ".join(sorted(candidate_skills)))

                    # Percentage Match
                    st.subheader("Percentage Match")
                    st.write(f"{response_json.get('JD Match', '0')}%")
                    
                except json.JSONDecodeError:
                    st.error("Error decoding response from Gemini.")
                except KeyError as e:
                    st.error(f"Key error: {str(e)} in response.")
        else:
            st.error("No text could be extracted from the PDF. Please try another file.")
