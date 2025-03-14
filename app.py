import streamlit as st
import google.generativeai as genai
import os

# Load API Key securely from Hugging Face Secrets
if "GOOGLE_API_KEY" in st.secrets:
    api_key = st.secrets["GOOGLE_API_KEY"]
    os.environ["GOOGLE_API_KEY"] = api_key
    st.write("✅ API Key Loaded Successfully!")
else:
    st.write("❌ API Key not found! Please set it in Hugging Face Secrets.")
    st.stop()

# Configure Google AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

st.title("🚀 AI Agent Running on Hugging Face Spaces")
st.write("Your AI Agent is now ready to process input!")
