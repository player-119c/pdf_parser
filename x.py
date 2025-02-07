from tika import parser

# Parse the PDF
parsed = parser.from_file("/Users/subrat_roy/Documents/LLM/try/daddddy.pdf")

# Get the extracted text
output_text = parsed.get('content', '').strip()

# Write the combined output to a text file
with open("output_book4.txt", "w", encoding="utf-8") as f:
    f.write(output_text)
