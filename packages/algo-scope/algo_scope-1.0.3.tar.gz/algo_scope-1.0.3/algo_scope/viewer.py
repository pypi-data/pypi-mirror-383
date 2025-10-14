import os
import webbrowser
from pathlib import Path

def launch_webpage():
    # Get the path to the current file (viewer.py)
    current_dir = Path(__file__).resolve().parent
    # Build the path to index.html inside the assets folder
    html_path = current_dir / "assets" / "index.html"

    if not html_path.exists():
        raise FileNotFoundError(f"index.html not found at {html_path}")

    # Open the HTML file in the default web browser
    webbrowser.open(f"file://{html_path}")
