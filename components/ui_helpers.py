# ui_helpers.py
import gradio as gr

def enable_continue():
    # Enable only the first continue button initially.
    return [
        gr.update(interactive=True),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False)
    ]

def unlock_next_button(button_id):
    if button_id == 1:
        return gr.update(interactive=True)
    elif button_id == 2:
        return gr.update(interactive=True)
    elif button_id == 3:
        return gr.update(interactive=True)
    return gr.update(interactive=False)

def disable_continue_show_rerun():
    return [
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(interactive=False),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True),
        gr.update(visible=True)
    ]
