import gradio as gr
import os
import utils.interface_utils as iutils
from components.chat import create_chat_controls, set_websocket_client
from components.bug_finding import create_bug_finding_tab
from components.pattern_matching import create_pattern_matching_tab
from components.patch_generation import create_patch_generation_tab
from components.patch_validation import create_patch_validation_tab
from components.file_upload import create_file_upload_section
from components.model_selection import create_model_selection_dropdown


def create_interface(ws_client=None):

    if ws_client:
        set_websocket_client(ws_client)

    choices = {"ChatGPT", "Claude"}

    with gr.Blocks(theme=iutils.custom_theme(), css=iutils.custom_css()) as interface:
        with gr.Column():
            # Header with Logo
            with gr.Row():
                gr.Markdown("# Code Repair with LLMs")  
                gr.Markdown("")  # Filler to push logo to the right
                gr.Image("logo.png", label="Logo", show_download_button=False, show_fullscreen_button=False, show_label=False, height=250, width=450, container=False)

            # Tabs for Different Features
            with gr.Tab("Chat"):
                with gr.Column():
                    steps = ["Bug Finding", "Pattern Matching", "Patch Generation", "Patch Validation"]
                    checkboxes = gr.CheckboxGroup(steps, label="Select Desired Steps", value=steps, interactive=True)
                    create_model_selection_dropdown(choices)
                    with gr.Column():
                        chatbot = gr.Chatbot(value=None, type="tuples", show_label=True, show_share_button=False)
                        create_chat_controls(chatbot)


            with gr.Tab("Bug Finding"):
                create_bug_finding_tab(choices)

            with gr.Tab("Pattern Matching"):
                create_pattern_matching_tab(choices)

            with gr.Tab("Patch Generation"):
                create_patch_generation_tab(choices)

            with gr.Tab("Patch Validation"):
                create_patch_validation_tab(choices)

            # Chatbot Always at the Bottom
            # with gr.Column():
            #     chatbot = gr.Chatbot(value=None, type="tuples", show_label=True, show_share_button=False)
            #     create_chat_controls(chatbot)

    return interface
