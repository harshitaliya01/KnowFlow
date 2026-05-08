from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv
load_dotenv()
import ssl
import certifi
import os
from sqlalchemy.pool import NullPool
DB_URL = os.getenv("DATABASE_URL")

# ssl_context = ssl.create_default_context(cafile=certifi.where())
# ssl_context.check_hostname = False   # 👈 IMPORTANT
# ssl_context.verify_mode = ssl.CERT_REQUIRED

engine = create_async_engine(
    DB_URL,
    poolclass=NullPool,
    connect_args={"ssl":"require","statement_cache_size": 0},
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

Base = declarative_base()

from supabase import acreate_client, AsyncClient

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

_client = AsyncClient = None
async def get_supabase() -> AsyncClient:
    global _client
    if _client is None:
        _client= await acreate_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client