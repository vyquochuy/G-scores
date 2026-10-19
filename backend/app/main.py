from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppEntityNotFoundException, AppValidationException

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(AppEntityNotFoundException)
async def entity_not_found_handler(
    request: Request,
    exc: AppEntityNotFoundException,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(AppValidationException)
async def validation_exception_handler(
    request: Request,
    exc: AppValidationException,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": {"code": exc.code, "message": exc.message}},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    errors = exc.errors()
    message = "Du lieu dau vao khong hop le."
    if errors:
        first_error = errors[0]
        msg = first_error.get("msg", "")
        if "Value error," in msg:
            message = msg.split("Value error,")[-1].strip()
        elif msg:
            message = msg

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": message,
                "details": errors,
            }
        },
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
