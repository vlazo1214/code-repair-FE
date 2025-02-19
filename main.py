import gradio as gr
from components.front_page import create_full_ui

# Create the UI
app = create_full_ui()

# Launch the app
if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7860, share=True, show_api=False)

