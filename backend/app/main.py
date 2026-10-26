from fastapi import FastAPI, File, HTTPException, Query, UploadFile

from .parser import StatementError
from .processor import process_statement

MAX_BYTES = 2 * 1024 * 1024

app = FastAPI(title="Statement Categorizer")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), purchases_positive: bool = Query(False)):
    if not (file.filename or "").lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")
    raw = await file.read()
    if len(raw) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="File too large (max 2 MB)")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 text")
    try:
        return process_statement(text, purchases_positive)
    except StatementError as exc:
        raise HTTPException(status_code=422, detail=str(exc))