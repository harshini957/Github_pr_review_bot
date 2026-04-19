# test_models.py
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("Available models that support generateContent:")
for model in genai.list_models():
    if "generateContent" in model.supported_generation_methods:
        print(f"  → {model.name}")