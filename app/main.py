from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.database import Base, engine
from app.exceptions import (
    NotFoundError,
    ForbiddenError,
    ConflictError,
    BadRequestError,
    AuthenticationError,
)
from app.routers import auth, expenses, admin
from app.routers.auth import limiter

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense & Reimbursement API", version="0.1.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def _error_handler(status_code: int):
    async def handler(request: Request, exc: Exception):
        return JSONResponse(status_code=status_code, content={"detail": exc.message})
    return handler


app.add_exception_handler(NotFoundError, _error_handler(404))
app.add_exception_handler(ForbiddenError, _error_handler(403))
app.add_exception_handler(ConflictError, _error_handler(409))
app.add_exception_handler(BadRequestError, _error_handler(400))
app.add_exception_handler(AuthenticationError, _error_handler(401))


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


app.include_router(auth.router)
app.include_router(expenses.router)
app.include_router(admin.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}
