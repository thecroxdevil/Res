import streamlit as st
import google.generativeai as genai
import os
import time

# Set page config for wider layout
st.set_page_config(page_title="AI Resume Assistant", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for chat-like interface
st.markdown("""
<style>
    /* Main chat container styling */
    .chat-container {
        border-radius: 10px;
        margin-bottom: 15px;
        padding: 15px;
    }
    
    /* User message styling */
    .user-message {
        background-color: #F0F2F6;
        text-align: right;
        border-radius: 15px 15px 0 15px;
        padding: 10px 15px;
        margin: 5px 0;
        display: inline-block;
        float: right;
        clear: both;
        max-width: 80%;
    }
    
    /* AI message styling */
    .ai-message {
        background-color: #E8F0FE;
        text-align: left;
        border-radius: 15px 15px 15px 0;
        padding: 10px 15px;
        margin: 5px 0;
        display: inline-block;
        float: left;
        clear: both;
        max-width: 80%;
    }
    
    /* Copy button styling */
    .copy-button {
        background-color: transparent;
        border: none;
        color: #4285F4;
        cursor: pointer;
        float: right;
        margin-top: 5px;
    }
    
    /* Output container */
    .output-container {
        background-color: #F8F9FA;
        border-radius: 10px;
        padding: 15px;
        margin-top: 10px;
        position: relative;
    }
    
    /* Default options section */
    .default-options {
        position: sticky;
        top: 0;
        background-color: white;
        padding: 10px;
        border-bottom: 1px solid #E0E0E0;
        z-index: 100;
    }
    
    /* Streamlit component styling overrides */
    div.row-widget.stRadio > div {
        flex-direction: row;
        align-items: center;
    }
    
    .stButton > button {
        background-color: #4285F4;
        color: white;
        border-radius: 20px;
        padding: 5px 20px;
    }
</style>
""", unsafe_allow_html=True)

# Function to load file content
def load_file(uploaded_file):
    """Loads the content of an uploaded file."""
    return uploaded_file.read().decode("utf-8") if uploaded_file else None

# Function to create a message with copy button
def display_copyable_output(output_text, title):
    output_id = f"output_{hash(output_text)}"
    
    st.markdown(f"""
    <div class="output-container">
        <h4>{title} <button class="copy-button" onclick="copyToClipboard('{output_id}')">
            <i class="material-icons">content_copy</i> Copy
        </button></h4>
        <pre id="{output_id}" style="white-space: pre-wrap;">{output_text}</pre>
    </div>
    
    <script>
    function copyToClipboard(elementId) {{
        const el = document.getElementById(elementId);
        const textArea = document.createElement('textarea');
        textArea.value = el.textContent;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        
        // Show copied notification
        const notification = document.createElement('div');
        notification.textContent = 'Copied to clipboard';
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.backgroundColor = '#4CAF50';
        notification.style.color = 'white';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '5px';
        notification.style.zIndex = '1000';
        document.body.appendChild(notification);
        
        setTimeout(function() {{
            document.body.removeChild(notification);
        }}, 2000);
    }}
    </script>
    """, unsafe_allow_html=True)

# Load API Key securely
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = api_key
else:
    st.error("API Key not found! Set it in Hugging Face Secrets.")
    st.stop()

# Configure Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

if "resume_latex" not in st.session_state:
    st.session_state.resume_latex = "\\documentclass{article}\\begin{document}Your default resume here.\\end{document}"

if "cover_letter_template_latex" not in st.session_state:
    st.session_state.cover_letter_template_latex = "\\documentclass{letter}\\begin{document}Your default cover letter template here.\\end{document}"

# App title with icon
st.markdown("<h1 style='text-align: center;'>📄 AI Resume & Cover Letter Assistant</h1>", unsafe_allow_html=True)

# Default options section - Pinned at the top
with st.container():
    st.markdown('<div class="default-options">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        use_default = st.radio("Template Options:", ("Use Default Templates", "Upload Custom Templates"))
    
    with col2:
        if use_default == "Upload Custom Templates":
            resume_file = st.file_uploader("Upload Resume Template", type=["tex"], key="resume_upload")
            cover_letter_file = st.file_uploader("Upload Cover Letter Template", type=["tex"], key="cover_letter_upload")
            
            if resume_file:
                st.session_state.resume_latex = load_file(resume_file)
            
            if cover_letter_file:
                st.session_state.cover_letter_template_latex = load_file(cover_letter_file)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)

# Job Description Input
default_jd = """Software Engineer: Looking for a software engineer with 5+ years of experience in Python and cloud technologies. Experience with AWS and Docker is a must."""
jd = st.text_area("Enter Job Description or ask me anything:", default_jd, height=100)

# Functions for AI processing
def modify_resume(jd, resume_latex):
    """Modifies the resume based on the job description."""
    model = genai.GenerativeModel('gemini-2.0-flash')
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
    model = genai.GenerativeModel('gemini-2.0-flash')
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

# Send button with loading animation
if st.button("Send", key="send_button"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": jd})
    
    # Show AI thinking animation
    with st.spinner("AI is working on your documents..."):
        # Process the request
        modified_resume = modify_resume(jd, st.session_state.resume_latex)
        cover_letter = generate_cover_letter(jd, modified_resume, st.session_state.cover_letter_template_latex)
        
        # Add AI response to chat history
        ai_response = "I've tailored your resume and created a cover letter for this job description. Here are the results:"
        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        
        # Simulate thinking time
        time.sleep(0.5)
    
    # Refresh the page to show the updated chat history
    st.experimental_rerun()

# Display the output after messages are shown (only if we have generated content)
if len(st.session_state.messages) > 0 and st.session_state.messages[-1]["role"] == "assistant":
    # Only show outputs if we've processed at least one job description
    for i in range(0, len(st.session_state.messages) - 1, 2):
        if i+1 < len(st.session_state.messages):
            user_msg = st.session_state.messages[i]["content"]
            
            # Process the job description again to get the outputs (or you could store these in session state)
            with st.spinner("Loading results..."):
                modified_resume = modify_resume(user_msg, st.session_state.resume_latex)
                cover_letter = generate_cover_letter(user_msg, modified_resume, st.session_state.cover_letter_template_latex)
            
            # Display copyable outputs
            display_copyable_output(modified_resume, "📄 Modified Resume")
            display_copyable_output(cover_letter, "✉️ Generated Cover Letter")
            
            # Download buttons
            col1, col2 = st.columns(2)
            with col1:
                st.download_button("Download Modified Resume", modified_resume, file_name="modified_resume.tex")
            with col2:
                st.download_button("Download Cover Letter", cover_letter, file_name="cover_letter.tex")
            
            st.markdown("<hr>", unsafe_allow_html=True)

# Add material icons for the copy button
st.markdown("""
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
""", unsafe_allow_html=True)
