# mock_api.py — run separately: uvicorn mock_api:app --port 8001

from fastapi import FastAPI
app = FastAPI()

@app.get("/account/{email}/status")
def account_status(email: str):
    return {"email": email, "status": "active", "locked": False}

