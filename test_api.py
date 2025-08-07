"""
Simple test script to verify the medical chatbot API is working
Run this after starting the backend server to test basic functionality
"""

import requests
import json

def test_api_connection():
    """Test basic API connectivity"""
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("✓ API is accessible")
            return True
        else:
            print(f"✗ API returned status code: {response.status_code}")
            return False
    except requests.ConnectionError:
        print("✗ Cannot connect to API. Make sure the backend server is running.")
        return False

def test_health_endpoint():
    """Test health check endpoint"""
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print("✓ Health check passed")
            print(f"  API configured: {data.get('api_configured', 'unknown')}")
            print(f"  Active sessions: {data.get('active_sessions', 0)}")
            return True
        else:
            print(f"✗ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False

def test_chat_endpoint():
    """Test the main chat endpoint with a simple query"""
    try:
        payload = {
            "message": "What should I do for a minor headache?",
            "conversation_history": [],
            "session_id": "test_session"
        }
        
        response = requests.post(
            "http://localhost:8000/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✓ Chat endpoint working")
            print("Sample response:")
            print(f"  {data['response'][:100]}...")
            return True
        else:
            print(f"✗ Chat endpoint failed with status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Chat endpoint error: {e}")
        return False

def main():
    print("Testing Medical Chatbot API")
    print("=" * 40)
    
    # Test basic connectivity
    if not test_api_connection():
        return
    
    print()
    
    # Test health endpoint
    test_health_endpoint()
    
    print()
    
    # Test chat endpoint (only if API key is configured)
    print("Testing chat functionality...")
    print("Note: This requires a valid GEMINI_API_KEY in backend/.env")
    test_chat_endpoint()
    
    print()
    print("=" * 40)
    print("Test completed!")

if __name__ == "__main__":
    main()
