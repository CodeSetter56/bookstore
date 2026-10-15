from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from ..utils.config import settings

pool = AsyncConnectionPool(
    conninfo=settings.db_dsn,
    kwargs={"row_factory": dict_row},
    min_size=1,
    max_size=10,
    open=False,
)


async def get_db_conn():
    print(settings.db_dsn)
    async with pool.connection() as conn:
        yield conn