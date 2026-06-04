import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://router.huggingface.co/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {os.getenv('HF_TOKEN')}",
    "Content-Type": "application/json"
}

payload = {
    "model": "openai/gpt-oss-20b",
    "messages": [
        {
            "role": "user",
            "content": "What is petroleum engineering?"
        }
    ]
}

response = requests.post(
    API_URL,
    headers=headers,
    json=payload,
    timeout=60
)

print(response.status_code)
print(response.text)