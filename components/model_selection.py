import gradio as gr

def create_model_selection_dropdown(choices):
    return gr.Dropdown(label="Model Selection", choices=choices, interactive=True)
