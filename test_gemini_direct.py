import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    print("🔍 Testing Google Gemini API Connection")
    print("=" * 45)
    
    # Load environment variables from backend/.env
    load_dotenv("backend/.env")
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ No API key found")
        return False
    
    print(f"✅ API Key loaded: {api_key[:10]}...{api_key[-4:]} (length: {len(api_key)})")
    
    try:
        # Configure the API
        genai.configure(api_key=api_key)
        print("✅ API configured successfully")
        
        # Create model
        model = genai.GenerativeModel('gemini-pro')
        print("✅ Model initialized")
        
        # Test with a simple request
        print("\n🧪 Testing API call...")
        response = model.generate_content("Say hello in one word only")
        
        if response and response.text:
            print(f"✅ API Response: '{response.text.strip()}'")
            print("✅ Google Gemini API is working perfectly!")
            return True
        else:
            print("❌ No response received from API")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        print(f"❌ Error Type: {type(e).__name__}")
        
        # Check for common error types
        error_str = str(e).lower()
        if "api_key" in error_str or "invalid" in error_str:
            print("💡 This looks like an API key issue")
        elif "quota" in error_str or "limit" in error_str:
            print("💡 This looks like a quota/rate limit issue")
        elif "permission" in error_str:
            print("💡 This looks like a permissions issue")
        
        return False

if __name__ == "__main__":
    test_gemini_api()
