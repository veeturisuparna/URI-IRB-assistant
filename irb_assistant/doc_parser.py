#!/usr/bin/env python3
"""
doc_parser.py

Extract text from .docx files using python-docx.
Extract text from .pdf files using PyPDF2.
"""

# Import for DOCX parsing
try:
    from docx import Document
except ImportError:
    print(
        "ERROR: python-docx is not installed in this environment."
        "\nInstall it with: pip install python-docx"
    )
    import sys
    sys.exit(1)

# Import for PDF parsing
try:
    import PyPDF2
    from PyPDF2.errors import PdfReadError
except ImportError:
    print(
        "ERROR: PyPDF2 is not installed in this environment."
        "\nInstall it with: pip install PyPDF2"
    )
    import sys
    sys.exit(1)

import os
import zipfile


def extract_text_from_docx(file_path):
    """
    Extracts and returns the full text content from a .docx file.

    Args:
        file_path (str): Path to the .docx file.

    Returns:
        str: The extracted text as a single string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a .docx or is corrupted.
        RuntimeError: For other errors opening the document.
    """
    # Check existence and extension
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.lower().endswith('.docx'):
        raise ValueError(f"Not a .docx file: {file_path}")

    try:
        doc = Document(file_path)
    except zipfile.BadZipFile:
        raise ValueError(f"Corrupted or invalid .docx: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error opening document: {e}")

    # Join all paragraph texts
    return "\n".join([para.text for para in doc.paragraphs])


def extract_text_from_pdf(file_path):
    """
    Extracts and returns the full text content from a .pdf file using PyPDF2.

    Args:
        file_path (str): Path to the .pdf file.

    Returns:
        str: The extracted text as a single string.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a .pdf or is corrupted.
        RuntimeError: For other errors opening the document.
    """
    # Check existence and extension
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"Not a .pdf file: {file_path}")

    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text_pages = []
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_pages.append(page_text)
        return "\n".join(text_pages)
    except PdfReadError:
        raise ValueError(f"Corrupted or invalid .pdf: {file_path}")
    except Exception as e:
        raise RuntimeError(f"Error reading PDF: {e}")


if __name__ == "__main__":
    # Paths to your IRB template documents (use raw strings for backslashes)
    application_template_path = r"G:\My Drive\PhD\Spring 25\EGR 404\Project\IRB Templates\IRB Application_April 2019.docx"
    consent_template_path    = r"G:\My Drive\PhD\Spring 25\EGR 404\Project\IRB Templates\IRB Consent Form for Research.Jan 2019 (2023).docx"
    appendix_b_template_path = r"G:\My Drive\PhD\Spring 25\EGR 404\Project\IRB Templates\Appendix B template.pdf"

    # Extract and print application template text
    print("--- Application Template Text ---")
    try:
        app_text = extract_text_from_docx(application_template_path)
        print(app_text)
    except Exception as err:
        print(f"Error reading application template: {err}")

    # Extract and print consent template text
    print("\n--- Consent Template Text ---")
    try:
        consent_text = extract_text_from_docx(consent_template_path)
        print(consent_text)
    except Exception as err:
        print(f"Error reading consent template: {err}")

    # Extract and print Appendix B template text
    print("\n--- Appendix B Template Text ---")
    try:
        appendix_text = extract_text_from_pdf(appendix_b_template_path)
        print(appendix_text)
    except Exception as err:
        print(f"Error reading Appendix B template: {err}")