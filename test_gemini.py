import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_api_key():
    print("Testing Google Gemini API Key Configuration")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY")
    print(f"API Key loaded: {'Yes' if api_key else 'No'}")
    print(f"API Key length: {len(api_key) if api_key else 0}")
    print(f"API Key starts with: {api_key[:10]}..." if api_key and len(api_key) > 10 else "No key or too short")
    
    if not api_key:
        print("❌ No API key found in environment variables")
        return False
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Try to create a model instance
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Model initialized successfully")
        
        # Test with a simple request
        print("\nTesting simple generation...")
        response = model.generate_content("Say hello in one word")
        
        if response and response.text:
            print(f"✅ API Response: {response.text}")
            return True
        else:
            print("❌ No response received")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_api_key()
