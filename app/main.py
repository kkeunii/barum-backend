from fastapi import FastAPI

app = FastAPI(title="Speech Learning API")


@app.get("/health")
async def health_check():
    return {"status": "ok"}