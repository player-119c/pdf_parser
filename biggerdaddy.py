import langchain
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import pdfplumber
import re
import apikey

# Set up your API key and model
ak = apikey.groq_key
model = ChatGroq(model="llama-3.3-70b-versatile", api_key=ak, streaming=False)

# Define a prompt template to process PDF content
prompt_template = """
You are a helpful assistant for processing PDF content. Here's the extracted content:

{text}

Your tasks are:
1. Clean up and organize the extracted text.
2. If there are any tables, convert them to Markdown format.
3. If mathematical formulas are present (LaTeX-style), convert them to proper LaTeX format.
4. If images are detected in the content, replace them with a placeholder like [IMAGE].
5. Make the output as structured as possible.

Please format the output appropriately and make sure it's readable.
"""

# Create the prompt template and chain
prompt = PromptTemplate(input_variables=["text"], template=prompt_template)
llm_chain = LLMChain(llm=model, prompt=prompt)

# Function to process PDF content with LangChain and ChatGroq
def process_pdf_with_langchain(pdf_path):
    extracted_text = ""

    # Extract text and tables using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()

            # Handle math formulas
            math_formulas = re.findall(r"\$.*?\$", page_text)
            for formula in math_formulas:
                page_text = page_text.replace(formula, f"[MATH FORMULA: {formula}]")

            # Add tables to extracted_text (you can use pdfplumber's table extraction for simple cases)
            tables = page.extract_tables()
            if tables:
                page_text += "\n[TABLE START]\n"
                for table in tables:
                    table_text = "| " + " | ".join(table[0]) + " |\n"
                    table_text += "|---" * len(table[0]) + "|\n"
                    for row in table[1:]:
                        table_text += "| " + " | ".join(row) + " |\n"
                    page_text += table_text
                page_text += "[TABLE END]"

            # Send each page's extracted content as a chunk to LangChain/ChatGroq for processing
            page_chunk = llm_chain.run({"text": page_text})
            extracted_text += f"\n--- Page {page_num} ---\n" + page_chunk

    return extracted_text

# Example usage
pdf_path = '/Users/subrat_roy/Documents/LLM/try/Elements_of_Information_Theory_2nd_ed_T.pdf'
processed_text = process_pdf_with_langchain(pdf_path)

# Save the processed content to a text file
with open("processed_pdf_output_llm_fb.txt", "w", encoding="utf-8") as f:
    f.write(processed_text)

print("PDF parsing and formatting complete. Check processed_pdf_output_llm_fb.txt.")
