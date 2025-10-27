import json
import requests
from datetime import datetime
from typing import List

# ---------- Configuration ----------
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
    headers = { "Content-Type": "application/json", "x-goog-api-key": API_KEY }

    payload = { "contents": [ { "role": "user", "parts": [{"text": prompt}] } ], "config": { "max_output_tokens": 150 } }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        # Adjust based on actual API response format
        return data["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print(f" Error processing prompt: {prompt}\n→ {e}")
        return f"Error: {str(e)}"


def save_responses_to_json(prompts: List[str], responses: List[str], output_path: str):
    """Saves prompts and responses as JSON."""
    result = []
    for prompt, response in zip(prompts, responses):
        result.append({
            "prompt": prompt,
            "response": response,
            "timestamp": datetime.utcnow().isoformat() + "Z"
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
