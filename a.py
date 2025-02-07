from unstructured.partition.pdf import partition_pdf

# Extract content from the PDF
elements = partition_pdf("/Users/subrat_roy/Documents/LLM/try/daddddy.pdf")

# Open a file to write the content to
with open("output.txt", "w") as file:
    # Iterate over each element and write its text content to the file
    for element in elements:
        if hasattr(element, 'text'):  # Check if the element has a 'text' attribute
            file.write(element.text + "\n")
