import gradio as gr

def assistant(name, question):
    return f"Hello {name}, you asked: {question}. AI is thinking... 🤖"

gr.Interface(
    fn=assistant,
    inputs=["text", "text"],  # Two text inputs
    outputs="text"
).launch()
