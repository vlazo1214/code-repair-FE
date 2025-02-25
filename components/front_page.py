import gradio as gr
#import utils.interface_utils as iutils

from api.initiate_pipeline_call import initiate_pipeline_call
from utils.convert_steps import convert_steps
from utils.storage import save_jwt_to_session
from api.WebSocketClient import WebSocketClient
#from components.interface import create_interface
#from components.model_selection import create_model_selection_dropdown

from components.file_utils import read_file, get_file_language
from components.pipeline_service import initialize_pipeline, run_pipeline, run_fault_localization, get_final_patch
from components.ui_helpers import enable_continue, disable_continue_show_rerun
from components.callbacks import on_continue1, on_continue2, on_continue3

css_code = """
/* Custom CSS for the header bar */
.header-bar {
    padding: 10px;
    display: flex;
    align-items: center;
}
.header-bar img {
    /* Set logo height to match title font size; adjust as needed */
    height: 8em;
    margin-right: 3px;
}

/* Scrollable areas for code and markdown */
.scrollable-code {
    max-height: 600px;
    overflow-y: auto;
}
.scrollable-markdown {
    max-height: 600px;
    overflow-y: auto;
}

/* Styling for custom HTML dropdowns (collapsible patches) */
.dropdown-html details {
    margin-bottom: 10px;
    border: 1px solid #ccc;
    padding: 5px;
    border-radius: 4px;
}
.dropdown-html summary {
    font-weight: bold;
    cursor: pointer;
}

/* Ensure the patch content is scrollable if it exceeds a max height */
.dropdown-html pre {
    max-height: 600px;
    overflow-y: auto;
}
"""

# Default language for file display
language = "python"

def on_file_upload(file):
    """
    Reads the file and updates the file display with its content and detected language.
    Also enables the run buttons if a file is uploaded.
    """
    if file is None:
        return gr.update(value="No file uploaded."), gr.update(interactive=False), gr.update(interactive=False)
    content, _ = read_file(file)
    language = get_file_language(file)
    if language == "java":
        language = "python"
    return gr.update(value=content, language=language), gr.update(interactive=True), gr.update(interactive=True)

ws_client = WebSocketClient()
def handle_initiate_pipeline(files, selected_steps, initial_prompt):
    """Processes the file upload and initiates the pipeline."""
    if not files:
        gr.Warning("Please upload a file/codebase.")
        return gr.update(visible=True), gr.update(visible=False)
    
    binary_steps = convert_steps(selected_steps)

    # TODO: Do something with prompt
    
    response = initiate_pipeline_call(files, binary_steps)
    '''
        Delete print below in production
    '''
    print(response.json())
    #3session_token_update, session_id_update, session_id = save_jwt_to_session(response) 

    session_id = response.json()["session_token"]
    
    ws_client.start_background_connection(session_id)

    return gr.update(visible=False), gr.update(visible=True)

def create_full_ui():
    with gr.Blocks(css=css_code) as app:
        # Header Bar with Logo and Title using gr.Image and gr.HTML
        with gr.Row(elem_classes="header-bar"):
            logo = gr.Image(
                value="gui-SD/logo.png",
                interactive=False,
                show_download_button=False,
                show_fullscreen_button=False,
                show_label=False,
                show_share_button=False,
                container=False
            )
            title = gr.HTML("<h1 class='header-title' style='margin: 0; padding-left: 10px;'>Code Repair with LLMs</h1>")
        
        with gr.Row():
            # Left Column: File Upload and Controls
            with gr.Column(scale=1, min_width=300):
                file_uploader = gr.File(
                    label="File upload (Python, Java, C++)",
                    file_types=[".py", ".java", ".cpp"]
                )
                file_display = gr.Code(
                    elem_classes=["scrollable-code"],
                    show_label=True,
                    label="File Contents",
                    language=language,
                    interactive=True,
                    lines=20
                )
                model_selection = gr.Dropdown(
                    label="Model selection dropdown", 
                    choices=["Meta Llama 3 8B-Instruct(Test)", "Meta Llama 3.1 70B-Instruct"]
                )
                run_pipeline_btn = gr.Button("Run Pipeline", interactive=False)
                manual_run_btn = gr.Button("Manual Run", interactive=False)
            # Right Column: Tabs for Each Pipeline Stage
            with gr.Column(scale=2, min_width=500):
                with gr.Tabs() as tabs:
                    with gr.Tab("Fault Localization"):
                        stage_output_1 = gr.Markdown(elem_classes=["scrollable-markdown"])
                        continue_button_1 = gr.Button("Continue", visible=True, interactive=False)
                    with gr.Tab("Pattern Matching"):
                        stage_output_2 = gr.Markdown(elem_classes=["scrollable-markdown"])
                        continue_button_2 = gr.Button("Continue", visible=True, interactive=False)
                    with gr.Tab("Patch Generation"):
                        stage_output_3 = gr.HTML()
                        continue_button_3 = gr.Button("Continue", visible=True, interactive=False)
                    with gr.Tab("Patch Validation"):
                        stage_output_4 = gr.Markdown(elem_classes=["scrollable-markdown"])
                        file_display_final = gr.Code(
                            elem_classes=["scrollable-code"],
                            show_label=True,
                            label="Final Patch",
                            language=language,
                            interactive=True,
                            lines=20
                        )
                        continue_button_4 = gr.Button("Continue", visible=True, interactive=False)
        
        # =============================================================================
        # EVENT BINDINGS
        # =============================================================================
        file_uploader.change(
            fn=on_file_upload,
            inputs=file_uploader,
            outputs=[file_display, run_pipeline_btn, manual_run_btn]
        )

        manual_run_btn.click(
            fn=initialize_pipeline,
            inputs=[file_display, file_uploader, model_selection],
            outputs=[]
        ).then(
            fn=run_fault_localization,
            inputs=[],
            outputs=stage_output_1
        ).then(
            fn=enable_continue,
            inputs=[],
            outputs=[continue_button_1, continue_button_2, continue_button_3, continue_button_4]
        )

        run_pipeline_btn.click(
            fn=disable_continue_show_rerun,
            inputs=[],
            outputs=[continue_button_1, continue_button_2, continue_button_3, continue_button_4]
        ).then(
            fn=initialize_pipeline,
            inputs=[file_display, file_uploader, model_selection],
            outputs=[]
        ).then(
            fn=run_pipeline,
            inputs=[],
            outputs=[stage_output_1, stage_output_2, stage_output_3, stage_output_4]
        ).then(
            fn=get_final_patch,
            inputs=[],
            outputs=[file_display_final]
        )

        continue_button_1.click(
            fn=on_continue1,
            inputs=[],
            outputs=[continue_button_2, stage_output_2]
        )
        continue_button_2.click(
            fn=on_continue2,
            inputs=[],
            outputs=[continue_button_3, stage_output_3]
        )
        continue_button_3.click(
            fn=on_continue3,
            inputs=[],
            outputs=[continue_button_4, stage_output_4, file_display_final]
        )

    return app
