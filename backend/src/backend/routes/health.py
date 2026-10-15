from fastapi import APIRouter, HTTPException, Depends
from ..db.pool import get_db_conn

router = APIRouter(tags=["health"])

@router.get("/")
def read_root():
    return {"message": "Hello from your backend!"}


@router.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running!"}

 
@router.get("/db-health")
async def db_health(conn=Depends(get_db_conn)):
    try:
        cur = await conn.execute("SELECT 1 AS ok")
        row = await cur.fetchone()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database health check failed: {e}")

    if row is None or row["ok"] != 1:
        raise HTTPException(status_code=500, detail="Database health check failed.")

    return {"status": "ok", "message": "Database connection is healthy!"}