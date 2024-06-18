from fastapi import FastAPI

app = FastAPI()

@app.get("/api/healthchecker")
def healthchecher():
  return {"status": "success", "message": "healthy"}