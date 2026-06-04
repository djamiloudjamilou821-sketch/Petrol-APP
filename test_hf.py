import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_TOKEN")

headers = {
    "Authorization": f"Bearer {token}"
}

response = requests.get(
    "https://huggingface.co/api/whoami-v2",
    headers=headers
)

print(response.status_code)
print(response.text)