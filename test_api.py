import requests
import os

API_KEY = os.environ.get("HF_TOKEN", "")
URL = "https://router.huggingface.co/v1/chat/completions"

# List of likely free/available models
models = [
    "HuggingFaceH4/zephyr-7b-beta",
    "google/gemma-2-2b-it",
    "microsoft/Phi-3-mini-4k-instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3" 
]

if not API_KEY:
    print("Missing HF_TOKEN environment variable. Set it before running.")
    raise SystemExit(1)

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

print(f"Testing endpoint: {URL}")

for model in models:
    print(f"\nTrying model: {model}")
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello!"}],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("SUCCESS! Response:", response.json())
            print(f"!!! USE THIS MODEL: {model} !!!")
            exit()
        else:
            print("Failed:", response.text[:200])
    except Exception as e:
        print(f"Error: {e}")
