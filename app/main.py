from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from app.utils.limit import limiter
from app.api import auth
from app.api import docs

from dotenv import load_dotenv
load_dotenv()

from app.core.logger import setup_logger
from app.core.errors import add_exception_handlers
setup_logger()

app = FastAPI()

app.state.limiter = limiter
add_exception_handlers(app)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(docs.router, tags=["Document"])

# docker-compose up --build