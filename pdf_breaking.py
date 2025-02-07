import os
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(input_pdf_path, output_dir, pages_per_split=100):
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Read the input PDF
    reader = PdfReader(input_pdf_path)
    total_pages = len(reader.pages)
    
    # Split the PDF into smaller parts
    for start_page in range(0, total_pages, pages_per_split):
        writer = PdfWriter()
        end_page = min(start_page + pages_per_split, total_pages)
        
        # Add pages to the writer
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        # Output file name
        output_pdf_path = os.path.join(output_dir, f"part_{start_page // pages_per_split + 1}.pdf")
        
        # Write the output PDF
        with open(output_pdf_path, "wb") as output_pdf:
            writer.write(output_pdf)
        
        print(f"Created: {output_pdf_path}")

if __name__ == "__main__":
    input_pdf_path = "/Users/subrat_roy/Documents/LLM/try/Elements_of_Information_Theory_2nd_ed_T.pdf"  # Change to your PDF file
    output_dir = "book_broken"  # Change to your desired output directory
    split_pdf(input_pdf_path, output_dir)
