def read_file(file):
    """Read an uploaded file and return its content and file extension/type."""
    if file is not None:
        try:
            with open(file.name, "r", encoding="utf-8") as f:
                content = f.read()
            ext = file.name.split('.')[-1] if '.' in file.name else 'plaintext'
            return content, ext
        except Exception as e:
            return f"Error reading file: {str(e)}", "plaintext"
    return "No file uploaded.", "plaintext"

def get_file_language(file):
    """
    Determine the programming language based on the file's extension.
    Returns a language string that can be used for the Code component.
    """
    if file is None:
        return "text"
    if hasattr(file, "name"):
        filename = file.name
        ext = filename.split('.')[-1].lower()
        if ext == "py":
            return "python"
        elif ext == "java":
            return "java"
        elif ext in ["cpp", "c", "h", "hpp"]:
            return "cpp"
    return "text"
