# callbacks.py
from components.pipeline_service import run_patch_validation, get_final_patch
from components.ui_helpers import unlock_next_button

def on_continue1():
    # Transition: Fault Localization → Pattern Matching.
    from pipeline_service import run_pattern_matching  # local import if needed
    patterns_markdown, status = run_pattern_matching()
    next_update = unlock_next_button(2)
    return next_update, patterns_markdown, status

def on_continue2():
    # Transition: Pattern Matching → Patch Generation.
    from pipeline_service import run_patch_generation  # local import if needed
    patch_dropdowns_html, status = run_patch_generation()
    next_update = unlock_next_button(2)
    return next_update, patch_dropdowns_html, status

def on_continue3():
    # Transition: Patch Generation → Patch Validation.
    val, status = run_patch_validation()
    final_patch, status = get_final_patch()
    next_update = unlock_next_button(3)
    # Return an additional output for final patch display.
    return next_update, val, final_patch, status
