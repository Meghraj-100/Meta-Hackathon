import requests

def test_reset():
    """
    Test the /reset endpoint to ensure the environment 
    initializes correctly without raising errors.
    """
    try:
        r = requests.post("http://localhost:8000/reset", json={"task_id": "task_1_easy"})
        if r.status_code == 200:
            print("✅ Reset test passed - Server returns 200 OK")
        else:
            print(f"❌ Reset test failed - Server returned {r.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Reset test failed - Could not connect to server (is it running on port 8000?)")

if __name__ == "__main__":
    print("Running basic local API test...")
    test_reset()
