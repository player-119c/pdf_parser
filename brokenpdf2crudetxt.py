import os
import fitz  # PyMuPDF

# Function to extract text and handle images from PDF
def extract_text_from_pdf(pdf_path):
    output_text = ""
    
    # Open the PDF file
    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)  # Load the page
            page_text = page.get_text("text")  # Extract plain text

            # Check if the page contains images
            image_list = page.get_images(full=True)
            if image_list:
                page_text = "[IMAGE]\n" + page_text  # Add placeholder for images

            # Add page number and text to output
            output_text += f"\n--- Page {page_num + 1} ---\n" + page_text
    
    return output_text


# Directory containing the broken PDFs
input_pdf_dir = "/Users/subrat_roy/Documents/LLM/try/book_broken"  # Change this to the directory with split PDFs
output_text_dir = "broken_crude_text"  # Directory to save the extracted text files

# Ensure the output directory exists
if not os.path.exists(output_text_dir):
    os.makedirs(output_text_dir)

# Loop through each PDF file in the directory
for filename in os.listdir(input_pdf_dir):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(input_pdf_dir, filename)
        
        # Extract text from each PDF
        extracted_text = extract_text_from_pdf(pdf_path)
        
        # Create a text file with the same name as the PDF, but with a .txt extension
        text_file_path = os.path.join(output_text_dir, f"{os.path.splitext(filename)[0]}.txt")
        
        # Write the extracted text to the text file
        with open(text_file_path, "w", encoding="utf-8") as text_file:
            text_file.write(extracted_text)
        
        print(f"Processed and saved: {text_file_path}")

print(f"All PDFs processed. Text files saved in {output_text_dir}.")
