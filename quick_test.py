import requests
import json

def test_simple_chat():
    """Test a simple chat request"""
    url = "http://localhost:8000/chat"
    payload = {
        "message": "Hello, what can you help me with?",
        "conversation_history": []
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {data['response'][:200]}...")
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_simple_chat()
