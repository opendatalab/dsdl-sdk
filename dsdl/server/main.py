import uvicorn
from dsdl.server.routers import api_parser


def create_fast_api_app(cors: bool = True, health_check: bool = True, **kwargs):
    from fastapi import FastAPI
    from starlette.middleware.cors import CORSMiddleware

    app = FastAPI(**kwargs)
    if cors:
        # 跨域
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    if health_check:
        @app.get("/health-check")
        async def health_check_view():
            return {"code": "0000", "msg": "health"}

    return app


app = create_fast_api_app(
    title="dsdl checkout server",
    version="0.0.0",
    description="bankend of dsdl",
    openapi_prefix="",
)

# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


app.include_router(api_parser.router, prefix="/parser", tags=["parser api"])


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8080)
