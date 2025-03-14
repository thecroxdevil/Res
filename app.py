import gradio as gr
import google.generativeai as genai
import os

# Get API key from Hugging Face Secrets (Environment Variable)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Function to get AI response
def chat_with_gemini(prompt):
    if not GEMINI_API_KEY:
        return "❌ API key missing! Set GEMINI_API_KEY in Hugging Face Secrets."
    
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio UI
gr.Interface(
    fn=chat_with_gemini,  # Function to call
    inputs="text",         # User inputs text
    outputs="text",        # AI outputs text
    title="Chat with Gemini AI",
    description="Enter a message and let Gemini AI respond."
).launch()
