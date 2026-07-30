
# api_tool.py
import requests

def check_account_status(email):
    try:
        r = requests.get(f"http://localhost:8001/account/{email}/status", timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        return {"error": "mock_api server not running on port 8001"}
    except requests.exceptions.Timeout:
        return {"error": "mock_api server timed out"}
    except requests.exceptions.HTTPError as e:
        return {"error": f"mock_api returned an error: {e}"}

"""if __name__ == "__main__":
    result = check_account_status("test@company.com")
    print(result)"""
