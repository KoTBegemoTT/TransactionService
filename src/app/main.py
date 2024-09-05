from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.external.jaeger import initialize_jaeger_tracer
from app.middleware import tracing_middleware
from app.transaction_service.urls import router as transactions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Настройка при запуске и остановке приложения."""
    initialize_jaeger_tracer()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(transactions_router, prefix='/api')

app.add_middleware(BaseHTTPMiddleware, dispatch=tracing_middleware)


@app.get('/')
async def root():
    """Стартовая страница."""
    return {'message': 'Hello World'}


@app.get('/ready', status_code=status.HTTP_200_OK)
async def ready_check():
    """Проверка состояния сервиса."""
    return {'message': 'Service is ready'}


@app.get('/live', status_code=status.HTTP_200_OK)
async def live_check():
    """Проверка состояния сервиса."""
    return {'message': 'Service is live'}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host='0.0.0.0',  # noqa: S104
        port=8002,  # noqa: WPS432
    )
