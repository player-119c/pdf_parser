import re

# Read the input file
with open("/Users/subrat_roy/Documents/LLM/try/final_cleaned_text copy.txt", "r", encoding="utf-8") as file:
    text = file.read()

# Remove content between <think> and </think>
cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

# Write the cleaned text back to a new file
with open("book.txt", "w", encoding="utf-8") as file:
    file.write(cleaned_text)

print("Text between <think> and </think> removed successfully!")
