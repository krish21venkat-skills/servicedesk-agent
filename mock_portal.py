# mock_portal.py — run separately: uvicorn mock_portal:app --port 8080
from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/admin/reset")
def reset_page():
    return FileResponse("portal/reset.html")