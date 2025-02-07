import pdfplumber
import camelot  # for table extraction

output_text = ""

with pdfplumber.open("/Users/subrat_roy/Documents/LLM/try/DeepSeek_V3.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages, start=1):
        # Extract plain text
        page_text = page.extract_text()
        # Detect images on the page, you can use page.images which returns bounding boxes
        if page.images:
            # Optionally, decide where the image falls in the text based on coordinates.
            # Here, we just prepend a placeholder.
            page_text = "[IMAGE]\n" + page_text

        # Check if the page likely contains a table:
        tables = page.extract_tables()
        if tables:
            # If you want to preserve table structure, you might use camelot for better formatting:
            try:
                camelot_tables = camelot.read_pdf("book.pdf", pages=str(page_num))
                page_text += "\n[TABLE START]\n"
                for table in camelot_tables:
                    # Convert table dataframe to markdown table string
                    page_text += table.df.to_markdown() + "\n"
                page_text += "[TABLE END]\n"
            except Exception:
                # Fallback to adding raw table text if Camelot fails
                page_text += "\n[TABLE DETECTED]\n"

        output_text += f"\n--- Page {page_num} ---\n" + page_text

# Write the combined output to a text file
with open("output_book.txt", "w", encoding="utf-8") as f:
    f.write(output_text)