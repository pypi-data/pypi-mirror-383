"""chatgpt-app: A simple text file package"""

import os
from pathlib import Path

__version__ = "0.0.1"

def get_text():
    """Read and return the content of a.txt"""
    txt_path = Path(__file__).parent / "a.txt"
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_text_path():
    """Return the path to a.txt"""
    return Path(__file__).parent / "a.txt"

