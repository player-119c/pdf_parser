import fitz  # PyMuPDF
from tika import parser
import pdfplumber
import re

# Function to handle mathematical formulas (LaTeX or inline math)
def handle_math(formula):
    # Handle LaTeX-style math (in $$ or $...$)
    return f"[MATH FORMULA: {formula}]"

# Function to extract tables using pdfplumber (better for text-based tables)
def extract_tables_with_pdfplumber(pdf_path, page_num):
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[page_num]
        table_text = ""
        tables = page.extract_tables()

        if tables:
            for table in tables:
                # Convert to Markdown-like format
                table_text += "| " + " | ".join(table[0]) + " |\n"
                table_text += "|---" * len(table[0]) + "|\n"
                for row in table[1:]:
                    table_text += "| " + " | ".join(row) + " |\n"
            return table_text
        return "[TABLE DETECTED - pdfplumber FAILED TO EXTRACT]"

# Function to process the PDF using Tika and PyMuPDF (fitz)
def parse_pdf(pdf_path):
    output_text = ""

    # Step 1: Extract text using Tika
    parsed = parser.from_file(pdf_path)
    text_from_tika = parsed.get('content', '').strip()

    # Step 2: Extract text and images using PyMuPDF (fitz)
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")

            # Step 3: Detect images and add placeholders
            image_list = page.get_images(full=True)
            if image_list:
                page_text = "[IMAGE]\n" + page_text  # Add image placeholder

            # Step 4: Check for mathematical formulas (basic example, could be extended)
            math_formulas = re.findall(r"\$.*?\$", page_text)  # Find LaTeX-style math
            for formula in math_formulas:
                page_text = page_text.replace(formula, handle_math(formula))

            # Step 5: Combine Tika and PyMuPDF extracted text
            page_text = text_from_tika + "\n" + page_text

            # Step 6: Extract tables using pdfplumber
            table_text = extract_tables_with_pdfplumber(pdf_path, page_num)
            page_text += f"\n[TABLE START]\n{table_text}[TABLE END]"

            # Add the processed page to the output
            output_text += f"\n--- Page {page_num + 1} ---\n{page_text}"

    return output_text

# Function to save the output to a text file
def save_output(output_text, output_file="output_book_v2.txt"):
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output_text)

# Main execution
pdf_path = "/Users/subrat_roy/Documents/LLM/try/Elements_of_Information_Theory_2nd_ed_T (dragged) (dragged).pdf"
output_text = parse_pdf(pdf_path)
save_output(output_text)

print("PDF parsing complete. Check output_book.txt.")
