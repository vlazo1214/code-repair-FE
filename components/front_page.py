import gradio as gr
import utils.interface_utils as iutils

from api.initiate_pipeline_call import initiate_pipeline_call
from utils.convert_steps import convert_steps
from utils.storage import save_jwt_to_session
from api.WebSocketClient import WebSocketClient
from components.interface import create_interface
from components.model_selection import create_model_selection_dropdown

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
    """Creates the full UI with a front page and the main interface."""
    with gr.Blocks(theme=iutils.custom_theme(), css="style.css") as app:
        # TODO: Replace with actual choices
        choices = ["ChatGPT", "Claude"]

        # Front Page UI
        with gr.Column(visible=True) as front_page:
            gr.Markdown("# Welcome to Code Repair with LLMs!")
            gr.Markdown("## Upload your files/codebase. All steps of the pipeline will be executed on the initial run.")

            file_input = gr.Files(
                label="Upload Multiple Files / Codebase",
                file_types=[".py", ".java", ".c", ".cpp"]
            )
            gr.Markdown("Python, Java, C++, and .zip files accepted.")


            steps = ["Bug Finding", "Pattern Matching", "Patch Generation", "Patch Validation"]
            checkboxes = gr.CheckboxGroup(steps, label="Select Desired Steps", value=steps, interactive=False)

            create_model_selection_dropdown(choices=choices)

            msg = gr.Textbox(label="Prompt", placeholder="Enter prompt (Optional)")
            initiate_button = gr.Button("Initiate Pipeline")

        # Main Interface UI (Initially Hidden)
        with gr.Column(visible=False) as main_interface:
            interface = create_interface(ws_client)

        # Button click should happen inside the context
        initiate_button.click(
            fn=handle_initiate_pipeline,
            inputs=[file_input, checkboxes, msg],
            outputs=[front_page, main_interface]
        )

    return app
