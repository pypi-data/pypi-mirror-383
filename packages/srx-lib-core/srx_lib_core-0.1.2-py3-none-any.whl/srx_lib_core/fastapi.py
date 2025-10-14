from typing import Iterable, Callable, Optional
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


def create_app(
    title: str,
    routers: Iterable[APIRouter] = (),
    middlewares: Iterable[Callable[[FastAPI], None]] = (),
    lifespan: Optional[Callable] = None,
) -> FastAPI:
    app = FastAPI(title=title, lifespan=lifespan)

    # CORS
    import os

    cors = os.getenv("CORS_ORIGIN")
    if cors:
        origins = [o.strip() for o in cors.split(",") if o.strip()]
    else:
        origins = []
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    for r in routers:
        app.include_router(r)

    # Extra middlewares as callables
    for mw in middlewares:
        mw(app)

    # Health route if not provided
    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app

