import streamlit as st
import google.generativeai as genai
import os
import time
from datetime import datetime

# Set page config for wider layout
st.set_page_config(page_title="AI Resume Assistant", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS to mimic WhatsApp chat interface
st.markdown("""
<style>
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 600px;
        margin: 0 auto;
    }
    
    /* WhatsApp background pattern */
    body {
        background-color: #e5ddd5;
        background-image: url("data:image/svg+xml,%3Csvg width='64' height='64' viewBox='0 0 64 64' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M8 16c4.418 0 8-3.582 8-8s-3.582-8-8-8-8 3.582-8 8 3.582 8 8 8zm0-2c3.314 0 6-2.686 6-6s-2.686-6-6-6-6 2.686-6 6 2.686 6 6 6zm33.414-6l5.95-5.95L45.95.636 40 6.586 34.05.636 32.636 2.05 38.586 8l-5.95 5.95 1.414 1.414L40 9.414l5.95 5.95 1.414-1.414L41.414 8zM40 48c4.418 0 8-3.582 8-8s-3.582-8-8-8-8 3.582-8 8 3.582 8 8 8zm0-2c3.314 0 6-2.686 6-6s-2.686-6-6-6-6 2.686-6 6 2.686 6 6 6zM9.414 40l5.95-5.95-1.414-1.414L8 38.586l-5.95-5.95L.636 34.05 6.586 40l-5.95 5.95 1.414 1.414L8 41.414l5.95 5.95 1.414-1.414L9.414 40z' fill='%23cdc8c0' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E");
    }
    
    /* Chat header styling */
    .chat-header {
        background-color: #075E54;
        color: white;
        padding: 10px 16px;
        display: flex;
        align-items: center;
        border-radius: 10px 10px 0 0;
        margin-bottom: 10px;
    }
    
    .chat-header img {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 10px;
    }
    
    .chat-header-info h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 500;
    }
    
    .chat-header-info p {
        margin: 0;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.8);
    }
    
    /* Chat container */
    .chat-container {
        display: flex;
        flex-direction: column;
        height: calc(100vh - 270px);
        overflow-y: auto;
        padding: 10px;
        background-color: #e5ddd5;
        margin-bottom: 10px;
        border-radius: 0 0 10px 10px;
    }
    
    /* Chat message common styling */
    .message {
        padding: 8px 12px;
        border-radius: 7.5px;
        margin-bottom: 8px;
        max-width: 65%;
        position: relative;
        word-wrap: break-word;
    }
    
    .message-time {
        font-size: 11px;
        color: #919191;
        position: absolute;
        bottom: 3px;
        right: 8px;
    }
    
    /* User message styling (right side) */
    .user-message {
        background-color: #dcf8c6;
        align-self: flex-end;
        border-radius: 7.5px 0 7.5px 7.5px;
        margin-left: auto;
        margin-right: 10px;
        box-shadow: 0 1px 0.5px rgba(0, 0, 0, 0.13);
    }
    
    /* Bot message styling (left side) */
    .bot-message {
        background-color: white;
        align-self: flex-start;
        border-radius: 0 7.5px 7.5px 7.5px;
        margin-right: auto;
        margin-left: 10px;
        box-shadow: 0 1px 0.5px rgba(0, 0, 0, 0.13);
    }
    
    /* Input area styling */
    .input-area {
        display: flex;
        padding: 10px;
        background-color: #f0f0f0;
        border-radius: 25px;
        margin-top: 10px;
    }
    
    .input-field {
        flex-grow: 1;
        border: none;
        border-radius: 20px;
        padding: 10px 15px;
        margin-right: 10px;
        outline: none;
    }
    
    .send-button {
        background-color: #128C7E;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }
    
    /* Document output styling */
    .document-container {
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
        box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
    }
    
    .document-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .document-title {
        font-weight: 500;
        color: #128C7E;
        display: flex;
        align-items: center;
    }
    
    .document-title i {
        margin-right: 5px;
    }
    
    .document-actions {
        display: flex;
    }
    
    .action-button {
        background: none;
        border: none;
        color: #919191;
        cursor: pointer;
        padding: 5px;
        margin-left: 8px;
        border-radius: 50%;
    }
    
    .action-button:hover {
        background-color: #f0f0f0;
    }
    
    .document-content {
        font-family: monospace;
        white-space: pre-wrap;
        font-size: 13px;
        line-height: 1.4;
        overflow-x: auto;
        background-color: #f9f9f9;
        padding: 10px;
        border-radius: 5px;
    }
    
    /* Default options styling */
    .default-options {
        background-color: #075E54;
        color: white;
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 15px;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .default-options h3 {
        margin: 0 0 10px 0;
        font-size: 16px;
    }
    
    /* Override Streamlit default styles */
    .stButton>button {
        background-color: #128C7E;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 5px 15px;
    }
    
    .stTextArea>div>div>textarea {
        border-radius: 20px;
        border: 1px solid #ccc;
        padding: 10px;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Function to load file content
def load_file(uploaded_file):
    """Loads the content of an uploaded file."""
    return uploaded_file.read().decode("utf-8") if uploaded_file else None

# Format current time like WhatsApp
def get_current_time():
    return datetime.now().strftime("%I:%M %p")

# Function to display copyable document
def display_whatsapp_document(content, title, icon, file_type):
    # Create a unique ID for the document content
    doc_id = f"doc_{hash(content)}"
    
    st.markdown(f"""
    <div class="document-container">
        <div class="document-header">
            <div class="document-title">
                <i class="material-icons">{icon}</i>
                {title}.{file_type}
            </div>
            <div class="document-actions">
                <button class="action-button" onclick="copyToClipboard('{doc_id}')">
                    <i class="material-icons">content_copy</i>
                </button>
                <button class="action-button" onclick="downloadFile('{doc_id}', '{title}.{file_type}')">
                    <i class="material-icons">download</i>
                </button>
            </div>
        </div>
        <div class="document-content" id="{doc_id}">{content}</div>
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
        
        // Show copy notification
        const notification = document.createElement('div');
        notification.textContent = 'Copied to clipboard';
        notification.style.position = 'fixed';
        notification.style.bottom = '20px';
        notification.style.left = '50%';
        notification.style.transform = 'translateX(-50%)';
        notification.style.backgroundColor = '#25D366';
        notification.style.color = 'white';
        notification.style.padding = '8px 16px';
        notification.style.borderRadius = '20px';
        notification.style.zIndex = '1000';
        document.body.appendChild(notification);
        
        setTimeout(() => {{
            document.body.removeChild(notification);
        }}, 2000);
    }}
    
    function downloadFile(elementId, fileName) {{
        const el = document.getElementById(elementId);
        const a = document.createElement('a');
        const file = new Blob([el.textContent], {{type: 'text/plain'}});
        a.href = URL.createObjectURL(file);
        a.download = fileName;
        a.click();
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

# Default options section - WhatsApp style
with st.container():
    st.markdown('<div class="default-options">', unsafe_allow_html=True)
    st.markdown('<h3>Template Settings</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        use_default = st.radio("Select option:", ("Default Templates", "Custom Templates"), label_visibility="collapsed")
    
    with col2:
        if use_default == "Custom Templates":
            resume_file = st.file_uploader("Upload Resume", type=["tex"], label_visibility="collapsed")
            cover_letter_file = st.file_uploader("Upload Cover Letter", type=["tex"], label_visibility="collapsed")
            
            if resume_file:
                st.session_state.resume_latex = load_file(resume_file)
            
            if cover_letter_file:
                st.session_state.cover_letter_template_latex = load_file(cover_letter_file)
    
    st.markdown('</div>', unsafe_allow_html=True)

# WhatsApp chat header
st.markdown("""
<div class="chat-header">
    <img src="https://via.placeholder.com/40" alt="AI Resume Assistant">
    <div class="chat-header-info">
        <h3>AI Resume Assistant</h3>
        <p>online</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Chat container
st.markdown('<div class="chat-container" id="chat-container">', unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    current_time = get_current_time()
    
    if message["role"] == "user":
        st.markdown(f"""
        <div class="message user-message">
            {message["content"]}
            <span class="message-time">{current_time}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="message bot-message">
            {message["content"]}
            <span class="message-time">{current_time}</span>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area with WhatsApp styling
col1, col2 = st.columns([5, 1])

with col1:
    # Job Description Input
    default_jd = """Software Engineer: Looking for a software engineer with 5+ years of experience in Python and cloud technologies. Experience with AWS and Docker is a must."""
    jd = st.text_area("Type a message", default_jd, height=80, label_visibility="collapsed")

with col2:
    # Send button with
