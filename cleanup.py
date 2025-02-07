import os
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import tiktoken
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import apikey
import re

# Set up API key and model
api_key = apikey.groq_key # Replace with your Groq API key
model = ChatGroq(model="llama3-70b-8192", api_key=api_key, temperature=0.1)

# Configure tokenizer for length estimation
tokenizer = tiktoken.get_encoding("cl100k_base")

# Retry decorator for API calls
@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=2, max=60))
def process_with_retry(chain, text):
    return chain.run(text=text)

def estimate_tokens(text):
    return len(tokenizer.encode(text))

def split_text(text, max_tokens=4000):
    """Split text into chunks based on token limits."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = estimate_tokens(para)
        if para_tokens > max_tokens:
            # Split large paragraphs into sentences
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
1. Remove any unnecessary formatting, extra spaces, or line breaks.
2. Fix any broken sentences or paragraphs.
3. Ensure consistent punctuation and capitalization.
4. Remove any non-standard characters or encoding artifacts.
5. Preserve the original meaning and structure of the text.
6. Make the text more readable and well-formatted.

Return only the cleaned text without additional explanations.
"""

# Create the prompt template and chain
prompt = PromptTemplate(input_variables=["text"], template=cleanup_prompt_template)
llm_chain = LLMChain(llm=model, prompt=prompt)

def cleanup_text_file(input_file, output_file):
    """Clean up a text file using the LLM."""
    # Read the input file
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Split the text into manageable chunks
    chunks = split_text(text)

    # Process each chunk
    cleaned_text = []
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        try:
            # Process the chunk with the LLM
            result = process_with_retry(llm_chain, chunk)
            cleaned_text.append(result)
            time.sleep(2)  # Rate limiting
        except Exception as e:
            print(f"Error processing chunk {i+1}: {str(e)}")
            cleaned_text.append(chunk)  # Fallback to original text if error occurs

    # Combine the cleaned chunks
    final_text = "\n\n".join(cleaned_text)

    # Write the cleaned text to the output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(final_text)

    print(f"Text cleanup complete. Output saved to {output_file}")

# Example usage
input_file = "/Users/subrat_roy/Documents/LLM/try/output_shannon_paper.txt"  # Replace with your input file path
output_file = "cleaned_shannon.txt"  # Replace with your desired output file path
cleanup_text_file(input_file, output_file)