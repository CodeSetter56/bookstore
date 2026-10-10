import os
from pathlib import Path
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent

load_dotenv(dotenv_path=ROOT_DIR / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in the root .env file!")

if "localhost" not in DATABASE_URL and not os.getenv("RUNNING_IN_DOCKER"):
    DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")

pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={"row_factory": dict_row},
    min_size=1,
    max_size=10
)

def get_db_connection():
    with pool.connection() as conn:
        yield conn
