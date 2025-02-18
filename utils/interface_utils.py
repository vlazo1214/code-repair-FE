# event handlers

import gradio as gr

def custom_theme():
    # Gradio UI styling
    return gr.themes.Ocean(
        primary_hue=gr.themes.Color(c100="#fef9c3", c200="#fef08a", c300="#fde047", c400="#facc15", c50="#fefce8", c500="#eab308", c600="#ca8a04", c700="#a16207", c800="#854d0e", c900="#713f12", c950="#BA9B37"),
        secondary_hue="zinc",
        radius_size="lg",
    ).set(
        background_fill_primary='*neutral_900',
        background_fill_secondary='*neutral_700',
        body_background_fill='*secondary_900',
        body_text_color='*neutral_100',
        body_text_color_subdued='*neutral_400',
        border_color_accent='*neutral_900',
        button_secondary_background_fill='linear-gradient(120deg, *secondary_900 0%, *primary_400 50%, *primary_700 100%)',
        button_secondary_background_fill_hover='linear-gradient(120deg, *secondary_900 0%, *primary_400 50%, *primary_700 100%)',
        checkbox_label_background_fill_selected="linear-gradient(120deg, *secondary_900 0%, *primary_400 50%, *primary_700 100%)",
        code_background_fill='*neutral_950',
        color_accent_soft='*primary_950',
        input_background_fill='*neutral_700',
        table_odd_background_fill='*neutral_700'
    )

def custom_css():
    return """
    .fixed-height 
    {
        height: 300px !important;
        overflow-y: auto !important;
    }

    .stage-box 
    {
        text-align: center !important;
        font-weight: bold !important;
    }

    .title 
    { 
        text-align: center; 
        font-size: 2rem; 
        font-weight: bold; 
    }

    .subtitle 
    { 
        text-align: center;
        font-size: 1.2rem;
    }

    .big-checkboxes label 
    { 
        font-size: 1.5rem;
        display: block; 
        text-align: center;
    }

    .big-button 
    { 
        font-size: 1.5rem; 
        padding: 10px 20px; 
        display: block; 
        margin: 0 auto; 
    }

    """

def display_file_content(file):
    if file is None:
        return "No file uploaded yet."
    try:
        if isinstance(file, str):
            with open(file, 'r') as f:
                return f.read()
        elif hasattr(file, 'name'):
            return file.name
        elif hasattr(file, 'read'):
            return file.read().decode('utf-8')
        else:
            return str(file)
    except Exception as e:
        return f"An error occurred while reading the file: {str(e)}"

def process_file(file, language):
    if file is None:
        return "Skipped", "Skipped", "Skipped", "Skipped", "Please upload a file."
    
    try:
        content = display_file_content(file)
        stage1_result = "Complete"
        stage2_result = "Complete"
        stage3_result = "Complete"
        stage4_result = "Complete"
        processed_content = process_content(content, language)
        return stage1_result, stage2_result, stage3_result, stage4_result, processed_content
    except Exception as e:
        return "Error", "Error", "Error", "Error", f"An error occurred: {str(e)}"

def process_content(content, language):
    # This is where you would implement your actual processing logic
    # For now, we'll just return the file content with a message
    return f"Processing {language} code:\n\n{content}\n\nProcessing complete."
