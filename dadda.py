import fitz  # PyMuPDF

output_text = ""

# Open the PDF file
with fitz.open("/Users/subrat_roy/Documents/LLM/try/Shannon_Paper.pdf") as doc:
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load the page
        page_text = page.get_text("text")  # Extract plain text

        # Check if the page contains images
        image_list = page.get_images(full=True)
        if image_list:
            page_text = "[IMAGE]\n" + page_text  # Add placeholder for images

        # Optionally, handle tables manually or use other libraries
        output_text += f"\n--- Page {page_num + 1} ---\n" + page_text

# Write the combined output to a text file
with open("output_shannon_paper.txt", "w", encoding="utf-8") as f:
    f.write(output_text)
