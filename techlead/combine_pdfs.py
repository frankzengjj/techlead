import PyPDF2
import os
import glob

def merge_pdfs(paths, output):
    pdf_writer = PyPDF2.PdfWriter()

    for path in paths:
        pdf_reader = PyPDF2.PdfReader(path)
        for page in range(len(pdf_reader.pages)):
            # Add each page to the writer object
            pdf_writer.add_page(pdf_reader.pages[page])

    # Write out the merged PDF
    with open(output, 'wb') as out:
        pdf_writer.write(out)

def get_pdf_paths(folder):
    # Construct the path pattern to match all PDF files in the folder
    path_pattern = os.path.join(folder, '*.pdf')

    # Use glob to find all paths matching the pattern
    pdf_paths = glob.glob(path_pattern)

    return pdf_paths

# Example usage
folder_path = 'pdfs/'
pdf_files = get_pdf_paths(folder_path)
merge_pdfs(pdf_files, 'merged.pdf')
