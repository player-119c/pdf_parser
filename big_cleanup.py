import os
import time
import re
import tiktoken
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from tenacity import retry, stop_after_attempt, wait_exponential
import apikey  # Ensure apikey.py contains a list of 4 API keys

# Groq API keys (store them in apikey.py as a list)
api_keys = [
    apikey.groq_key_1, 
    apikey.groq_key_2, 
    apikey.groq_key_3, 
    apikey.groq_key_4,
    
]

# Configure tokenizer for length estimation
tokenizer = tiktoken.get_encoding("cl100k_base")

# Function to estimate token count
def estimate_tokens(text):
    return len(tokenizer.encode(text))

# Function to split text into chunks
def split_text(text, max_tokens=4000):
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_tokens = 0

    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        if para_tokens > max_tokens:
            sentences = re.split(r'(?<=[.!?]) +', para)
            current_chunk.extend(sentences)
        elif current_tokens + para_tokens > max_tokens:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_tokens = para_tokens
        else:
            current_chunk.append(para)
            current_tokens += para_tokens

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    return chunks

# Define the cleanup prompt template
cleanup_prompt_template = """
You are a text cleanup assistant. Your task is to process the following text:

{text}

Perform the following actions:
1. Remove unnecessary formatting, extra spaces, or line breaks.
2. Fix broken sentences or paragraphs.
3. Ensure consistent punctuation and capitalization.
4. Remove any non-standard characters or encoding artifacts.
5. Preserve the original meaning and structure of the text.
6. Make the text more readable and well-formatted.

Return only the cleaned text without additional explanations.
"""

# Function to create LLMChain with a specific API key
def create_llm_chain(api_key):
    model = ChatGroq(model="deepseek-r1-distill-llama-70b", api_key=api_key, temperature=0.1)
    prompt = PromptTemplate(input_variables=["text"], template=cleanup_prompt_template)
    return LLMChain(llm=model, prompt=prompt)

# Retry decorator for API calls
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=60))
def process_with_retry(chain, text):
    return chain.run(text=text)

# Function to process all text files in the directory
def process_text_files(input_dir, output_file):
    text_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".txt")])
    total_files = len(text_files)

    if not text_files:
        print("No text files found in the input directory.")
        return

    cleaned_texts = []
    api_key_index = 0  # To rotate API keys

    for i, filename in enumerate(text_files):
        input_path = os.path.join(input_dir, filename)
        print(f"\nProcessing {filename} ({i+1}/{total_files}) with API Key {api_key_index+1}...")

        # Read the input text
        with open(input_path, "r", encoding="utf-8") as f:
            text = f.read()

        # Split text into chunks
        chunks = split_text(text)

        # Create an LLMChain with the current API key
        llm_chain = create_llm_chain(api_keys[api_key_index])

        # Process each chunk
        cleaned_text = []
        for j, chunk in enumerate(chunks):
            print(f"  -> Processing chunk {j+1}/{len(chunks)}...")
            try:
                result = process_with_retry(llm_chain, chunk)
                cleaned_text.append(result)
                time.sleep(2)  # Rate limiting
            except Exception as e:
                print(f"  !! Error in chunk {j+1}: {str(e)}")
                cleaned_text.append(chunk)  # Fallback to original text

        # Rotate API key after processing one file
        api_key_index = (api_key_index + 1) % len(api_keys)

        # Store cleaned text
        cleaned_texts.append("\n\n".join(cleaned_text))

    # Write all cleaned texts into a single output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n\n".join(cleaned_texts))

    print(f"\nAll text files processed. Combined output saved to {output_file}")

# Paths
input_text_dir = "/Users/subrat_roy/Documents/LLM/try/broken_crude_text"  # Change this to your input directory
final_output_file = "final_cleaned_text.txt"  # Change this to your desired output file

# Run the process
process_text_files(input_text_dir, final_output_file)
