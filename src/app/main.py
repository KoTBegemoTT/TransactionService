import uvicorn
from fastapi import FastAPI

from app.transaction_service.urls import router as transactions_router

app = FastAPI()
app.include_router(transactions_router)


@app.get('/')
async def root():
    """Стартовая страница."""
    return {'message': 'Hello World'}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        reload=True,
        host='0.0.0.0',  # noqa: S104
        port=8002,  # noqa: WPS432
    )
