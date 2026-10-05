import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_root():
    print("\n--- Test: Root Endpoint ---")
    try:
        res = requests.get(f"{BASE_URL}/")
        print(f"Status: {res.status_code}, Response: {res.json()}")
    except Exception as e:
        print(f"Error: {e}")

def test_chat(text, lang):
    print(f"\n--- Test: Chat ({lang}) ---")
    print(f"Query: {text}")
    payload = {
        "text": text,
        "language": lang,
        "conversation_id": -1
    }
    try:
        res = requests.post(f"{BASE_URL}/api/chat", json=payload)
        data = res.json()
        print(f"Emergency: {data.get('emergency')}")
        print(f"Emotion: {data.get('emotion')}")
        print(f"Response Snippet: {data.get('response')[:100]}...")
    except Exception as e:
        print(f"Error: {e}")

def run_tests():
    test_root()
    
    # Test RAG / Normal Chat
    test_chat("Quels sont les symptômes du diabète ?", "Français")
    test_chat("What are the signs of hypertension?", "English")
    test_chat("كيفاش نقص في السكر؟", "العربية")
    
    # Test Emergency
    test_chat("J'ai une crise cardiaque, aidez-moi !", "Français")
    test_chat("I am having a severe chest pain and can't breathe", "English")

if __name__ == "__main__":
    print("Assurez-vous que le serveur backend est lancé (python server.py)")
    run_tests()
