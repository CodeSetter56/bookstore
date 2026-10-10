from fastapi import FastAPI, Depends
from .db.db import get_db_connection

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello from your backend!"}

@app.get("/health")
def check_database_connection(conn = Depends(get_db_connection)):
    try:
        result = conn.execute("SELECT 1")
        if result.fetchone():
            return {"status": "ok", "message": "Database is connected!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}