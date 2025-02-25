# pipeline_service.py .
import os
from backend.source.pipeline.pipeline import Pipeline

pipeline = None
language = "text"

def initialize_pipeline(file_display_value, file_obj, model):
    global pipeline, language
    try:
        file_content = file_display_value if file_display_value is not None else ""
        if file_obj is not None and hasattr(file_obj, "name"):
            file_name = os.path.basename(file_obj.name)
            file_ext = os.path.splitext(file_name)[1].lower()
            if file_ext in [".py"]:
                language = "python"
            elif file_ext in [".java"]:
                language = "java"
            elif file_ext in [".cpp", ".c", ".h", ".hpp"]:
                language = "cpp"
            else:
                language = "text"
        else:
            file_name = "Unknown"
            language = "text"
        
        if model == "Meta Llama 3 8B-Instruct(Test)":
            pipeline = Pipeline(file_name, file_content, None, test=True)
        elif model == "Meta Llama 3.1 70B-Instruct":
            model = "accounts/eriktajti-a69f1e/deployedModels/ft-55346a98-791f5-9f0c0828"
            pipeline = Pipeline(file_name, file_content, model)
        
        print("Pipeline initialized with file:", file_name)
        print("Content length:", len(file_content))
        print("Language detected:", language)
    except Exception as e:
        print(f"Error initializing pipeline: {str(e)}")
        pipeline = Pipeline("Unknown", "")
        language = "text"

def run_fault_localization():
    pipeline.fault_localization()
    return str(pipeline.localization)

def run_pattern_matching():
    pipeline.pattern_matching()
    complete_output = ""
    for pre_pattern in pipeline.pre_patterns:
        complete_output += f"{pre_pattern}\n"
    return complete_output

def run_patch_generation():
    pipeline.patch_generation()
    html_output = "<h3>Patches Generated</h3>"
    for i, patch in enumerate(pipeline.patches):
        label = "Final Patch" if i == len(pipeline.patches) - 1 else f"Patch {i+1}"
        html_output += (
            f"<details class='dropdown-html'><summary>{label}</summary>"
            f"<pre><code>{patch}</code></pre></details><br>"
        )
    return html_output

def run_patch_validation():
    pipeline.patch_validation()
    pipeline.rag.clear_index()
    return str(pipeline.validation)

def run_pipeline():
    return (
        run_fault_localization(),
        run_pattern_matching(),
        run_patch_generation(),
        run_patch_validation()
    )

def get_final_patch():
    """Return the final patch from the pipeline's patches list."""
    if pipeline is not None and hasattr(pipeline, "patches") and pipeline.patches:
        return pipeline.patches[-1]
    return ""
