import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ Error: GEMINI_API_KEY is missing.")
    exit(1)

genai.configure(api_key=api_key)

def check_connectivity():
    print("🔄 Checking Gemini API Connectivity...\n")

    try:
        print("--- Available Models for Generation ---")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"✅ {m.name}")
                
    except Exception as e:
        print(f"❌ Failed to connect. Error: {e}")
        return

    # Explicitly using a model we know is on your account
    test_model_name = "models/gemini-2.5-flash"

    print(f"\n--- Testing connection using: {test_model_name} ---")
    
    try:
        model = genai.GenerativeModel(test_model_name)
        response = model.generate_content("Hello! This is an API connectivity test. Please reply only with: 'Connection successful!'")
        
        print("\nResponse received:")
        print(f"> {response.text.strip()}\n")
        print("✅ API Connectivity is fully functional!")
        
    except Exception as e:
        print(f"❌ Failed to generate content with {test_model_name}.\nError Details: {e}")

if __name__ == "__main__":
    check_connectivity()
