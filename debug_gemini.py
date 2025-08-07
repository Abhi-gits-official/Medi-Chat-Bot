import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {'Yes' if api_key else 'No'}")

if api_key:
    print(f"API Key length: {len(api_key)}")
    print(f"API Key starts with: {api_key[:10]}...")
    
    try:
        # Configure API
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        
        # Initialize model
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Model initialized successfully")
        
        # Test simple generation
        print("\nTesting generation...")
        response = model.generate_content("Hello, respond with just 'Hi there!'")
        print(f"✅ Response received: {response.text}")
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"❌ Error type: {type(e)}")
        import traceback
        print("❌ Full traceback:")
        traceback.print_exc()
else:
    print("❌ No API key found")
