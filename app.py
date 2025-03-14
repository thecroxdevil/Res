import streamlit as st
import google.generativeai as genai
import os

def load_file(uploaded_file):
    """Loads the content of an uploaded file."""
    return uploaded_file.read().decode("utf-8") if uploaded_file else None

# Load API Key securely
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = api_key
else:
    st.error("API Key not found! Set it in Hugging Face Secrets.")
    st.stop()

# Configure Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Streamlit UI
st.title("📄 AI Resume & Cover Letter Generator")

# Job Description Input
default_jd = """Software Engineer: Looking for a software engineer with 5+ years of experience in Python and cloud technologies. Experience with AWS and Docker is a must."""
jd = st.text_area("Paste the Job Description:", default_jd, height=150)

# File Uploads
resume_file = st.file_uploader("Upload Resume (LaTeX file)", type=["tex"])
cover_letter_template_file = st.file_uploader("Upload Cover Letter Template (LaTeX file)", type=["tex"])

def modify_resume(jd, resume_latex):
    """Modifies the resume based on the job description."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are an expert resume editor. Modify the resume below to align with the job description.
    Job Description:
    {jd}

    Resume (LaTeX):
    {resume_latex}
    """
    response = model.generate_content(prompt)
    return response.text

def generate_cover_letter(jd, modified_resume_latex, cover_letter_template_latex):
    """Generates a cover letter based on the job description and modified resume."""
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
    You are a cover letter expert. Generate a cover letter for the given job description using the resume below.
    Job Description:
    {jd}

    Resume (LaTeX):
    {modified_resume_latex}

    Cover Letter Template:
    {cover_letter_template_latex}
    """
    response = model.generate_content(prompt)
    return response.text

if st.button("Generate Resume & Cover Letter"):
    if resume_file and cover_letter_template_file:
        resume_latex = load_file(resume_file)
        cover_letter_template_latex = load_file(cover_letter_template_file)
        
        modified_resume = modify_resume(jd, resume_latex)
        cover_letter = generate_cover_letter(jd, modified_resume, cover_letter_template_latex)
        
        st.subheader("📄 Modified Resume")
        st.text_area("Updated Resume (LaTeX)", modified_resume, height=200)
        
        st.subheader("✉️ Generated Cover Letter")
        st.text_area("Generated Cover Letter (LaTeX)", cover_letter, height=200)
        
        st.download_button("Download Modified Resume", modified_resume, file_name="modified_resume.tex")
        st.download_button("Download Cover Letter", cover_letter, file_name="cover_letter.tex")
    else:
        st.error("Please upload both the resume and cover letter template.")
