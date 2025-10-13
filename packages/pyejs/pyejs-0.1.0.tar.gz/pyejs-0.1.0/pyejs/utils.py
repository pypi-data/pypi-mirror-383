import os
from io import StringIO
from pyejs import Template

def generate_html(file_path: str, data: dict, obj: object = None, use_buffer: bool = True, destination_path: str = None):
    """
    Generate HTML content from a template file.

    Parameters:
        file_path (str): The path to the source file.
        data (dict): A dictionary containing data for rendering.
        obj (object): Optional object that may be used in processing.
        use_buffer (bool): If True, return the rendered HTML content;
                           if False, write it to a file.
        destination_path (str, optional): Output path for HTML when writing to file.

    Behavior:
        - If use_buffer=True, return rendered HTML string (in memory).
        - If use_buffer=False, write rendered HTML to a file.
    """
    # Ensure template file exists
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Template file '{file_path}' does not exist.")

    # Read template
    with open(file_path, "r", encoding="utf-8") as f:
        template_str = f.read()

    # Prepare context
    context = data.copy()
    if obj is not None:
        context["obj"] = obj

    # Render HTML
    html_content = Template(template_str).render(context)

    # If use_buffer=True → return the rendered HTML string
    if use_buffer:
        return html_content

    # If use_buffer=False → write to file
    destination_path = destination_path or os.environ.get("HTML_OUTPUT_PATH", "output.html")
    os.makedirs(os.path.dirname(destination_path), exist_ok=True) if os.path.dirname(destination_path) else None

    with open(destination_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ HTML written to: {destination_path}")
    return None
