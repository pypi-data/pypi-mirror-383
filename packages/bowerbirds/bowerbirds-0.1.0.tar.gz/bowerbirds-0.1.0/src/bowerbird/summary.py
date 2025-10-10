import json
import os
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# ------------------- Model Setup -------------------
checkpoint = "HuggingFaceTB/SmolLM2-1.7B-Instruct"
device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(checkpoint)
model = AutoModelForCausalLM.from_pretrained(checkpoint).to(device)

system_prompt_summarize = (
    "Analyze the following code and provide a concise summary that clearly describes its functionality "
    "and purpose. The summary should be suitable for: 1) renaming the file in a meaningful way, "
    "and 2) guiding the organization of the project structure"
)

# ------------------- Functions -------------------
def generate_assistant_summary(code_content, max_new_tokens=150):
    """
    Generates the assistant summary for a given code string using the model.
    """
    messages = [
        {"role": "system", "content": system_prompt_summarize},
        {"role": "user", "content": code_content}
    ]
    input_text = tokenizer.apply_chat_template(messages, tokenize=False)
    inputs = tokenizer.encode(input_text, return_tensors="pt").to(device)
    
    outputs = model.generate(
        inputs, 
        max_new_tokens=max_new_tokens, 
        temperature=0.2, 
        top_p=0.9, 
        do_sample=False
    )
    
    decoded = tokenizer.decode(outputs[0])
    start_token = "<|im_start|>assistant"
    start_index = decoded.find(start_token)
    if start_index != -1:
        decoded = decoded[start_index + len(start_token):].strip()
    
    return decoded

def process_directory_combined_json(directory_path, output_json_path="combined_meta.json"):
    """
    Recursively processes all .py files in a directory and generates a single combined JSON.
    """
    combined_meta = []

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                with open(file_path, "r", encoding="utf-8") as f:
                    code_content = f.read()
                
                assistant_summary = generate_assistant_summary(code_content)
                combined_meta.append({
                    "file_path": file_path,
                    "assistant_summary": assistant_summary
                })
    
    # Save combined JSON
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(combined_meta, f, indent=4)
    
    print(f"\nCombined JSON file created at: {output_json_path}")
    return output_json_path


# ------------------- Example Usage -------------------
# input_directory = "path_to_your_directory"  # Replace with your directory path
# process_directory_combined_json(input_directory)
