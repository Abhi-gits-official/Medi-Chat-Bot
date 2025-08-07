"""
Final System Status Check
This script provides a comprehensive overview of the medical chatbot setup
"""

import requests
import json
import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: Missing")
        return False

def check_servers():
    """Check if both servers are running"""
    print("\n🖥️  Server Status Check")
    print("-" * 30)
    
    # Check backend
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend Server: Running (Port 8000)")
            print(f"   - API Configured: {data.get('api_configured', 'Unknown')}")
            print(f"   - Active Sessions: {data.get('active_sessions', 0)}")
        else:
            print(f"⚠️  Backend Server: Responding but status {response.status_code}")
    except requests.ConnectionError:
        print("❌ Backend Server: Not accessible")
        return False
    except Exception as e:
        print(f"❌ Backend Server: Error - {e}")
        return False
    
    # Check frontend (by checking if port is in use)
    try:
        response = requests.get("http://localhost:5174", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend Server: Running (Port 5174)")
        elif response.status_code in [404, 500]:
            print("✅ Frontend Server: Running (Port 5174) - Vite dev server active")
        else:
            print(f"⚠️  Frontend Server: Unusual response {response.status_code}")
    except:
        try:
            response = requests.get("http://localhost:5173", timeout=5)
            if response.status_code in [200, 404, 500]:
                print("✅ Frontend Server: Running (Port 5173)")
            else:
                print(f"⚠️  Frontend Server: Unusual response {response.status_code}")
        except:
            print("❌ Frontend Server: Not accessible on ports 5173 or 5174")
            return False
    
    return True

def test_chat_functionality():
    """Test the chat endpoint"""
    print("\n💬 Chat Functionality Test")
    print("-" * 30)
    
    try:
        payload = {
            "message": "What is first aid?",
            "conversation_history": []
        }
        
        response = requests.post("http://localhost:8000/chat", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            if 'technical difficulties' in response_text.lower():
                print("⚠️  Chat API: Working but Gemini API has issues")
                print("   This usually means:")
                print("   - API key might be invalid or expired")
                print("   - Rate limits exceeded")
                print("   - Network connectivity issues")
                return "warning"
            elif len(response_text) > 50:
                print("✅ Chat API: Working perfectly!")
                print(f"   Sample response: {response_text[:100]}...")
                return True
            else:
                print("⚠️  Chat API: Unusual short response")
                return "warning"
        else:
            print(f"❌ Chat API: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chat API: Error - {e}")
        return False

def main():
    print("🏥 Medical Assistance Chatbot - System Status")
    print("=" * 50)
    
    # Check project structure
    print("\n📁 Project Structure")
    print("-" * 20)
    
    files_to_check = [
        ("frontend/src/MedicalChatbot.tsx", "Main Chat Component"),
        ("frontend/src/App.tsx", "Frontend App"),
        ("backend/main.py", "Backend Server"),
        ("backend/.env", "Environment Configuration"),
        ("README.md", "Documentation"),
    ]
    
    structure_ok = True
    for filepath, description in files_to_check:
        if not check_file_exists(filepath, description):
            structure_ok = False
    
    # Check API key
    print(f"\n🔑 API Key Configuration")
    print("-" * 25)
    if Path("backend/.env").exists():
        try:
            with open("backend/.env", "r") as f:
                content = f.read()
                if "GEMINI_API_KEY=" in content and "your_gemini_api_key_here" not in content:
                    print("✅ API Key: Configured")
                else:
                    print("❌ API Key: Not configured properly")
        except Exception as e:
            print(f"❌ API Key: Error reading .env - {e}")
    else:
        print("❌ API Key: .env file missing")
    
    # Check servers
    servers_ok = check_servers()
    
    # Test functionality
    chat_status = test_chat_functionality()
    
    # Summary
    print(f"\n🎯 Summary")
    print("=" * 15)
    print(f"Project Structure: {'✅ Good' if structure_ok else '❌ Issues'}")
    print(f"Servers Running: {'✅ Good' if servers_ok else '❌ Issues'}")
    if chat_status == True:
        print("Chat Functionality: ✅ Excellent")
    elif chat_status == "warning":
        print("Chat Functionality: ⚠️  Needs API Key Fix")
    else:
        print("Chat Functionality: ❌ Not Working")
    
    print(f"\n🌐 Access URLs:")
    print(f"Frontend: http://localhost:5174")
    print(f"Backend:  http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    
    if chat_status == "warning":
        print(f"\n💡 Next Steps:")
        print("1. Verify your Google Gemini API key is valid")
        print("2. Visit https://makersuite.google.com/app/apikey")
        print("3. Check if you have API quota/credits available")
        print("4. Try testing with a new API key")

if __name__ == "__main__":
    main()
