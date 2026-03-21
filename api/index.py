from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello from Vercel Serverless!"}

@app.get("/sync")
def run_sync():
    return {"status": "Sync triggered successfully"}