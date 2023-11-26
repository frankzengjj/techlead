import os

def generate_pdfs_file_path(title) -> str:
    project_root = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    pdf_directory = os.path.join(project_root, "pdfs")
    os.makedirs(pdf_directory, exist_ok=True)
    pdf_path = os.path.join(pdf_directory, f"{title}.pdf")
    return pdf_path
