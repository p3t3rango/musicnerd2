from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/api/test")
async def test():
    return JSONResponse({"message": "API is working"})

# For Vercel serverless functions
handler = app 