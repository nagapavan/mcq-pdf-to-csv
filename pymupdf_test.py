# Usinf pymupdf
from typing import Dict

import fitz  # this is pymupdf


def get_pages(file_path: str) -> Dict:
    pymupdf_text = dict()
    with fitz.Document(file_path) as doc:
        for page in doc:
            text = page.get_text()
            pymupdf_text[page.number] = text.split('\n')
    return pymupdf_text
