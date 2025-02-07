import fitz  # PyMuPDF
from tika import parser
import pdfplumber
import re
import json

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
                # Convert to a list of lists (rows)
                table_data = [table[0]] + table[1:]
                return table_data
        return None

# Function to process the PDF using Tika and PyMuPDF (fitz)
def parse_pdf(pdf_path):
    output_data = {}

    # Step 1: Extract text using Tika
    parsed = parser.from_file(pdf_path)
    text_from_tika = parsed.get('content', '').strip()

    # Step 2: Extract text and images using PyMuPDF (fitz)
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            page_text = page.get_text("text")

            page_data = {
                'page_number': page_num + 1,
                'text': page_text,
                'tables': [],
                'images': [],
                'math_formulas': []
            }

            # Step 3: Detect images and add placeholders
            image_list = page.get_images(full=True)
            if image_list:
                page_data['images'] = [f"[IMAGE {i+1}]" for i in range(len(image_list))]

            # Step 4: Check for mathematical formulas (basic example, could be extended)
            math_formulas = re.findall(r"\$.*?\$", page_text)  # Find LaTeX-style math
            for formula in math_formulas:
                page_text = page_text.replace(formula, handle_math(formula))
                page_data['math_formulas'].append(formula)

            # Step 5: Combine Tika and PyMuPDF extracted text
            page_data['text'] = text_from_tika + "\n" + page_text

            # Step 6: Extract tables using pdfplumber
            table_data = extract_tables_with_pdfplumber(pdf_path, page_num)
            if table_data:
                page_data['tables'] = table_data

            output_data[f'page_{page_num + 1}'] = page_data

    return output_data

# Function to save the output to a JSON file
def save_output_json(output_data, output_file="output_book_v2.json"):
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

# Main execution
pdf_path = "/Users/subrat_roy/Documents/LLM/try/daddddy.pdf"
output_data = parse_pdf(pdf_path)
save_output_json(output_data)

print("PDF parsing complete. Check output_book_v2.json.")
