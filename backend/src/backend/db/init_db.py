from .pool import pool

PROMPTS = [
    "A haunted lighthouse",
    "A cat riding a skateboard",
    "A futuristic city skyline",
    "A dragon eating a taco",
    "A robot gardener",
    "A pirate ship in a bottle",
    "An alien having a picnic",
    "A superhero eating vegetables",
    "A clock melting over a tree",
    "A pizza playing guitar",
]

CREATE_USERS = """
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        elo_rating INTEGER DEFAULT 1200,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_PROMPTS = """
    CREATE TABLE IF NOT EXISTS prompts (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        text TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_REFRESH_TOKENS = """
    CREATE TABLE IF NOT EXISTS refresh_tokens (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        token_hash VARCHAR(255) UNIQUE NOT NULL,
        expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
"""

CREATE_DRAWINGS = """
    CREATE TABLE IF NOT EXISTS drawings (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID REFERENCES users(id) ON DELETE CASCADE,
        prompt_id UUID REFERENCES prompts(id) ON DELETE SET NULL,
        final_image_url TEXT NOT NULL,
        stroke_data_url TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
"""


async def init_db() -> None:
    async with pool.connection() as conn:
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        await conn.execute(CREATE_USERS)
        await conn.execute(CREATE_PROMPTS)
        await conn.execute(CREATE_REFRESH_TOKENS)
        await conn.execute(CREATE_DRAWINGS)

        cur = await conn.execute("SELECT COUNT(*) AS count FROM prompts")
        row = await cur.fetchone()
        if row is None or row["count"] == 0:
            for text in PROMPTS:
                await conn.execute("INSERT INTO prompts (text) VALUES (%s)", (text,))

        await conn.commit()