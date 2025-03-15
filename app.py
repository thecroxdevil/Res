import os
os.environ['GRADIO_CACHE_DIR'] = '/data/gradio_cache' # Or just '/data' or a subdir within it
import gradio as gr
# ... (rest of your app.py code) ...

# --- Configuration and File Paths ---
RESUME_TEMPLATE_FILE = "user_resume.tex"
COVER_LETTER_TEMPLATE_FILE = "cover_letter_template.tex"
RESUME_PROMPT_FILE = "resume_agent_prompt.txt"
COVER_LETTER_PROMPT_FILE = "cover_letter_agent_prompt.txt"
DEFAULT_RESUME_PROMPT = """
You are a resume modification assistant.
Your goal is to revise the provided resume content to be more relevant to the given Job Description.

**Job Description:**
{jd_text}

**Existing Resume Content (LaTeX):**
{resume_latex_code}

**Instructions:**
1. Analyze the Job Description to identify key skills, keywords, and requirements.
2. Compare these requirements to the content within the 'content sections' of the provided LaTeX resume (skills, experience, projects descriptions - do NOT change formatting commands).
3. Modify the 'content sections' of the resume to emphasize skills and experiences relevant to the Job Description.
4. Retain the original LaTeX template structure. Only replace the text content within the existing sections, not the LaTeX formatting commands or section headings.
5. Ensure the output is valid LaTeX code and ONLY output the modified LaTeX code.  Do NOT include any extra text or explanations.

**Output:** (Only Modified Resume LaTeX code)
"""
DEFAULT_COVER_LETTER_PROMPT = """
You are a cover letter generation assistant.
Your goal is to write a cover letter based on the provided Job Description and the applicant's Modified Resume.

**Job Description:**
{jd_text}

**Modified Resume Content (LaTeX):**
{modified_resume_latex_code}

**Cover Letter Template (LaTeX structure):**
{cover_letter_template_latex_code}

**Instructions:**
1. Analyze the Job Description to understand the company, role, required skills, and tone.
2. Review the Modified Resume to identify the applicant's most relevant skills and experiences for this role.
3. Write a compelling cover letter addressed to the hiring manager (if name is in JD, use it, otherwise use a general salutation like "Dear Hiring Manager").
4. Highlight 2-3 key achievements or experiences from the resume that directly match the job requirements and company values (if discernible from JD).
5. Express your enthusiasm for the role and company.
6. Maintain a professional and enthusiastic tone.
7.  Ensure the cover letter text fits into the provided LaTeX cover letter template structure.  ONLY provide the cover letter text itself.  Do NOT output the full LaTeX document, just the text content to be inserted into the template's body section.


**Output:** (Only Cover Letter Text - to be placed inside the template)
"""

def load_text_file(filepath, default_content=""):
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return ""  # Return an EMPTY STRING if file doesn't exist

def save_text_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def load_latex_file(filepath): # Keeping this function as you might use it for initial template loading if needed.
    return load_text_file(filepath) # Using text file load for simplicity here for Space demo.

def save_latex_file(filepath, latex_code): #  Keeping this too
    save_text_file(filepath, latex_code)

def insert_content_into_latex_template(template_latex, content, placeholder="[COVER_LETTER_CONTENT_PLACEHOLDER]"):
    return template_latex.replace(placeholder, content)

def call_ai_model(prompt, ai_model_choice):
    print(f"\n--- Calling {ai_model_choice.upper()} API --- Prompt:\n{prompt}\n---")

    if ai_model_choice == "gemini":
        try:
            from google.generativeai import GenerativeModel

            google_api_key = os.environ.get("GOOGLE_API_KEY") # Get API Key from Secrets
            if not google_api_key:
                return "Error: GOOGLE_API_KEY secret not found. Please set it in Hugging Face Space Secrets."

            gemini_model = GenerativeModel(model_name="gemini-2.0-flash", api_key=google_api_key) # Use 'gemini-pro' or your model name
            response = gemini_model.generate_content(prompt)

            if response and response.text:
                ai_output_text = response.text
            else:
                return f"Gemini API Error: No text response. Response details: {response}" # More descriptive error
            return ai_output_text

        except ImportError:
            return "Error: `google-generativeai` library not installed. Please add it to `requirements.txt`."
        except Exception as e: # Catch other potential API errors
            return f"Gemini API Error: {e}"


    elif ai_model_choice == "deepseek":
        # --- DEEPSEEK API SIMULATION REMAINS --- (Replace with real Deepseek API integration when available)
        if "resume modification" in prompt.lower():
            return "\\documentclass{article}\n\\begin{document}\n% SIMULATED DeepSeek Modified resume content based on JD\n\\section*{Projects} (DeepSeek - Projects emphasized based on JD)...\n\\section*{Awards} (DeepSeek - Awards relevant to JD)...\n\\end{document}"
        elif "cover letter" in prompt.lower():
            return "Dear Hiring Team,\n\nSIMULATED Cover letter from DeepSeek, highlighting project relevance... (DeepSeek - Cover Letter content).\n\nBest regards,\n[Your Name]"
        else:
            return "SIMULATED DeepSeek: Prompt type not recognized."
    else:
        return "Error: Invalid AI model choice."


def modify_resume_agent(jd_text, resume_latex_code, resume_template_latex_code, ai_model_choice, resume_agent_prompt):
    prompt = resume_agent_prompt.format(jd_text=jd_text, resume_latex_code=resume_latex_code)
    modified_content = call_ai_model(prompt, ai_model_choice)
    return modified_content

def cover_letter_agent(jd_text, modified_resume_latex_code, cover_letter_template_latex_code, ai_model_choice, cover_letter_agent_prompt):
    prompt = cover_letter_agent_prompt.format(jd_text=jd_text, modified_resume_latex_code=modified_resume_latex_code, cover_letter_template_latex_code=cover_letter_template_latex_code)
    cover_letter_content = call_ai_model(prompt, ai_model_choice)
    modified_cover_letter_latex = insert_content_into_latex_template(cover_letter_template_latex_code, cover_letter_content)
    return modified_cover_letter_latex


def process_input(jd_input, resume_file, cover_letter_template_file, ai_model_choice, replace_resume_template, replace_coverletter_template, resume_agent_prompt_input, cover_letter_agent_prompt_input):
    # --- File Handling ---
    if resume_file and hasattr(resume_file, 'read'): # CHECK for .read() method
        resume_latex_code_content = resume_file.read().decode('utf-8')
        if replace_resume_template:
            save_latex_file(RESUME_TEMPLATE_FILE, resume_latex_code_content)
        resume_latex_code = resume_latex_code_content
    else: # This block now executes if resume_file is falsy OR it doesn't have .read()
        resume_latex_code = load_text_file(RESUME_TEMPLATE_FILE)

    if cover_letter_template_file and hasattr(cover_letter_template_file, 'read'): # ADDED hasattr CHECK here too!
        cover_letter_template_latex_code = cover_letter_template_file.read().decode('utf-8')
        if replace_coverletter_template:
             save_latex_file(COVER_LETTER_TEMPLATE_FILE, cover_letter_template_latex_code)
        cover_letter_template_latex_code = cover_letter_template_latex_code
    else: # Execute if cover_letter_template_file is falsy OR doesn't have .read()
        cover_letter_template_latex_code = load_text_file(COVER_LETTER_TEMPLATE_FILE)

    # --- Prompt Handling ---
    resume_agent_prompt = resume_agent_prompt_input if resume_agent_prompt_input else DEFAULT_RESUME_PROMPT
    cover_letter_agent_prompt = cover_letter_agent_prompt_input if cover_letter_agent_prompt_input else DEFAULT_COVER_LETTER_PROMPT

    save_text_file(RESUME_PROMPT_FILE, resume_agent_prompt)
    save_text_file(COVER_LETTER_PROMPT_FILE, cover_letter_agent_prompt)

    # --- Agent Calls ---
    modified_resume_latex_code = modify_resume_agent(jd_input, resume_latex_code, load_text_file(RESUME_TEMPLATE_FILE) if not resume_file else resume_latex_code, ai_model_choice, resume_agent_prompt)
    cover_letter_latex_code = cover_letter_agent(jd_input, modified_resume_latex_code, cover_letter_template_latex_code, ai_model_choice, cover_letter_agent_prompt)

    return modified_resume_latex_code, cover_letter_latex_code


# --- Gradio UI ---
with gr.Blocks(title="AI Resume & Cover Letter Generator") as demo:
    gr.Markdown("# AI Powered Resume & Cover Letter Generator")
    gr.Markdown("Upload your Job Description (JD), Resume template, and Cover Letter template. Edit prompts below if needed. Click 'Generate' to get tailored Resume and Cover Letter.")

    with gr.Accordion("Prompts (Edit & Pin)", open=False):
        resume_agent_prompt_input = gr.TextArea(value=load_text_file(RESUME_PROMPT_FILE, DEFAULT_RESUME_PROMPT), lines=5, label="Resume Modification Agent Prompt")
        cover_letter_agent_prompt_input = gr.TextArea(value=load_text_file(COVER_LETTER_PROMPT_FILE, DEFAULT_COVER_LETTER_PROMPT), lines=5, label="Cover Letter Generation Agent Prompt")

    with gr.Row():
        with gr.Column():
            jd_input = gr.TextArea(lines=7, label="Job Description (JD)")
            resume_file = gr.File(file_types=['.tex'], label="Upload Resume LaTeX Template (Optional - To use new template)")
            replace_resume_template_checkbox = gr.Checkbox(label="Replace Existing Resume Template?", value=False)
            cover_letter_template_file = gr.File(file_types=['.tex'], label="Upload Cover Letter LaTeX Template (Optional - To use new template)")
            replace_coverletter_template_checkbox = gr.Checkbox(label="Replace Existing Cover Letter Template?", value=False)
            ai_model_choice = gr.Dropdown(["gemini", "deepseek"], value="gemini", label="Choose AI Model") # Removed "(Simulated)"
            generate_button = gr.Button("Generate Resume & Cover Letter")

        with gr.Column():
            modified_resume_output = gr.Code(label="Modified Resume (LaTeX Code)") # Removed language='latex'
            cover_letter_output = gr.Code(label="Cover Letter (LaTeX Code)")     # Removed language='latex'

    generate_button.click(
        process_input,
        inputs=[jd_input, resume_file, cover_letter_template_file, ai_model_choice, replace_resume_template_checkbox, replace_coverletter_template_checkbox, resume_agent_prompt_input, cover_letter_agent_prompt_input],
        outputs=[modified_resume_output, cover_letter_output]
    )

demo.launch()
