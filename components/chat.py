import gradio as gr
from api.WebSocketClient import WebSocketClient

# Get access to the global WebSocket client
ws_client = None

def set_websocket_client(client):
    """Set the global WebSocket client reference"""
    global ws_client
    ws_client = client

def create_chat_controls(chatbot):
    """Create chat controls and connect them to the WebSocket client"""
    with gr.Row():
        with gr.Column(scale=10):
            msg = gr.Textbox(label="Prompt", placeholder="Enter prompt")

    with gr.Row():
        with gr.Column(min_width=0, scale=10):
            submit_button = gr.Button("Submit Prompt")
    
    def send_chat_message(message, chat_history):
        """Send a message to the WebSocket server and update the chat"""
        if not message.strip():
            return chat_history

        chat_history = chat_history or []
        chat_history.append([message, None])  # Add user message

        if ws_client:
            try:
                response = ws_client.send_message(message)

                # Ensure response is properly extracted
                assistant_message = None
                if isinstance(response, dict):
                    assistant_message = response.get("content") or response.get("error")
                else:
                    assistant_message = str(response)

                # Update the last message in chat history
                chat_history[-1][1] = assistant_message

            except Exception as e:
                chat_history[-1][1] = f"Error: Could not communicate with the server. {str(e)}"
        else:
            chat_history[-1][1] = "WebSocket not connected. Please start the pipeline first."

        return chat_history
    
    # Connect submit button to send function
    submit_button.click(
        fn=send_chat_message,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    )
    
    # Also connect pressing Enter to send
    msg.submit(
        fn=send_chat_message,
        inputs=[msg, chatbot],
        outputs=[chatbot]
    )
    
    return msg, submit_button