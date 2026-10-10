import os
from pathlib import Path
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row

# 1. Point to the .env file at the project root (backend/)
# db.py -> src/db -> src -> backend (root)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# 2. Get the connection string securely
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL found in the root .env file!")

# *NOTE*: In your .env, the url is 'postgres://tigur:tigur@db:5432/tigurDB'
# If you are running FastAPI locally on your computer (outside of Docker),
# 'db' will not resolve. We swap it to 'localhost' automatically here to be safe.
if "localhost" not in DATABASE_URL and not os.getenv("RUNNING_IN_DOCKER"):
    DATABASE_URL = DATABASE_URL.replace("@db:", "@localhost:")

# 3. Create the Connection Pool using purely psycopg (v3)
# dict_row means the database will return rows as dictionaries automatically,
# which makes it much easier to return them as JSON in FastAPI.
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    kwargs={"row_factory": dict_row},
    min_size=1,
    max_size=10
)

# 4. Create a FastAPI Dependency to get a single connection for a route function
def get_db_connection():
    """
    Checks out a connection from the pool, yields it to the route,
    and reliably returns it to the pool when the request ends.
    """
    with pool.connection() as conn:
        yield conn