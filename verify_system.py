import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def wait_for_server():
    print("Waiting for server to start...")
    for _ in range(10):
        try:
            requests.get(f"{BASE_URL}/docs")
            print("Server is up!")
            return True
        except:
            time.sleep(1)
    return False

def test_user_flow():
    print("Testing User Submission...")
    payload = {
        "rating": 4,
        "review": "The interface is very clean, but it loads a bit slow."
    }
    try:
        res = requests.post(f"{BASE_URL}/reviews", json=payload)
        if res.status_code == 200:
            data = res.json()
            if data['success'] and "ai_response" in data:
                print(f"User Submission Success! AI Response: {data['ai_response'][:50]}...")
                return True
        print(f"User Submission Failed: {res.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

def test_admin_flow():
    print("Testing Admin Retrieval...")
    try:
        res = requests.get(f"{BASE_URL}/admin/reviews")
        if res.status_code == 200:
            data = res.json()
            # print(data)
            if data['count'] > 0:
                latest = data['data'][0]
                print(f"Admin Retrieval Success! Found {data['count']} reviews.")
                print(f"Latest Review Summary: {latest.get('summary', 'N/A')}")
                return True
        print(f"Admin Retrieval Failed: {res.text}")
    except Exception as e:
        print(f"Exception: {e}")
    return False

if __name__ == "__main__":
    if not wait_for_server():
        print("Server failed to start.")
        sys.exit(1)
    
    if test_user_flow() and test_admin_flow():
        print("Verification PASSED")
    else:
        print("Verification FAILED")
        sys.exit(1)
