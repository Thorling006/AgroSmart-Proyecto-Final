import requests
import json
import os

# Cargar la API Key desde credenciales.json
CRED_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'credenciales.json')
with open(CRED_FILE, 'r') as f:
    creds = json.load(f)
API_KEY = creds.get('GEMINI_API_KEY')
MODEL = 'models/gemini-2.5-pro'


def ask_gemini(message):
    url = f'https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={API_KEY}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{"parts": [{"text": message}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text
        else:
            return f"Error: {response.status_code} {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"
