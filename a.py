import json
import requests
from datetime import datetime
from typing import List

# ---------- Configuration ----------
# 1. FIX: Removed the leading space before the URL.
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
API_KEY = ""
INPUT_FILE_PATH = "input_prompts.txt"
OUTPUT_FILE_PATH = "llm_responses.json"


# ---------- Helper Functions ----------
def read_prompts_from_file(file_path: str) -> List[str]:
    """Reads lines from a text file and returns them as a list of prompts."""
    with open(file_path, "r", encoding="utf-8") as file:
        prompts = [line.strip() for line in file if line.strip()]
    return prompts


def call_llm_api(prompt: str) -> str:
    """Sends a single prompt to the LLM API and returns the model's response text."""
    
    # 2. FIX: Use the correct header for API Key authentication
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
    }

    # 3. FIX: Use the correct Gemini API request body structure (contents, role, parts)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        # Use a config block for parameters like max tokens
        "config": {
            "max_output_tokens": 150
        }
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        # This will raise an exception for 4xx or 5xx errors (like 401 or 404)
        response.raise_for_status() 
        data = response.json()
        
        # 4. FIX: Use correct parsing logic for the Gemini API response
        if data.get("candidates"):
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        else:
            # Handle cases where the prompt was blocked or response is empty
            feedback = data.get('promptFeedback', {}).get('blockReason', 'Unknown reason')
            return f"Error: API response missing content or blocked. Feedback: {feedback}"
            
    except Exception as e:
        print(f" Error processing prompt: {prompt}\n→ {e}")
        return f"Error: {str(e)}"


def save_responses_to_json(prompts: List[str], responses: List[str], output_path: str):
    """Saves prompts and responses as JSON."""
    result = []
    # Note: Using utcnow is deprecated. You might see a warning, but it's okay for this script.
    timestamp = datetime.utcnow().isoformat() + "Z" 
    
    for prompt, response in zip(prompts, responses):
        result.append({
            "prompt": prompt,
            "response": response,
            "timestamp": timestamp 
        })

    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=4, ensure_ascii=False)


# ---------- Main Execution ----------
def main():
    """Main entry point of the script."""
    print("Reading prompts...")
    prompts = read_prompts_from_file(INPUT_FILE_PATH)

    print(f" Sending {len(prompts)} prompts to the LLM API...")
    responses = [call_llm_api(prompt) for prompt in prompts]

    print("Saving responses to JSON file...")
    save_responses_to_json(prompts, responses, OUTPUT_FILE_PATH)

    print(f" All done! Results saved to {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    main()