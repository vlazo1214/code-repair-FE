import gradio as gr
from components.model_selection import create_model_selection_dropdown

def create_patch_validation_tab(choices):
    with gr.Column():
        create_model_selection_dropdown(choices)
        gr.Textbox(label="Output", interactive=False)
        gr.Code(label="File Contents", language="python", interactive=False, elem_classes=["fixed-height"])
