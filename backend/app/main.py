from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import select

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.coupon import Coupon
from app.routers import addresses, auth, cart, catalog, coupons, orders, payments, reviews, wishlist


async def _seed_default_coupon() -> None:
    """Idempotently ensure at least one active coupon exists (SAVE100)."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Coupon).where(Coupon.code == "SAVE100"))
        if result.scalar_one_or_none() is None:
            session.add(Coupon(code="SAVE100", discount_amount=100, discount_pct=None, active=True))
            await session.commit()


def _ensure_override_cover_art() -> None:
    """Regenerates the hand-authored override books' placeholder cover SVGs
    on every startup. These live on the container's local filesystem (not
    the Postgres volume), so a container recreate wipes them even though
    the DB rows that reference their URLs survive — this call is what makes
    them come back without rerunning the full Open Library seed. Pure
    local file writes, no DB/network access, safe to run unconditionally.
    """
    from app.seed.cover_art import write_cover
    from app.seed.seed_catalog import OVERRIDE_BOOKS, slugify

    for spec in OVERRIDE_BOOKS:
        slug = slugify(f"{spec['title']}-{spec['author_name']}")
        write_cover(slug, spec["title"], spec["author_name"], spec["cover_bg"], spec["cover_fg"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_override_cover_art()
    await _seed_default_coupon()
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="Book Worm API",
        description=(
            "REST API for the Book Worm e-bookstore capstone project. Covers the full "
            "customer journey: authentication, catalog browsing, product details with "
            "reviews, wishlist, cart, checkout with address and coupons, simulated "
            "payment, and order history with cancellation."
        ),
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        first_error = exc.errors()[0] if exc.errors() else None
        if first_error:
            loc = ".".join(str(p) for p in first_error.get("loc", []) if p != "body")
            message = first_error.get("msg", "Invalid request")
            detail = f"{loc}: {message}" if loc else message
        else:
            detail = "Invalid request"
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": detail})

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    static_dir = Path(__file__).resolve().parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    app.include_router(auth.router)
    app.include_router(catalog.router)
    app.include_router(reviews.router)
    app.include_router(wishlist.router)
    app.include_router(cart.router)
    app.include_router(addresses.router)
    app.include_router(coupons.router)
    app.include_router(orders.router)
    app.include_router(payments.router)

    return app


app = create_app()
