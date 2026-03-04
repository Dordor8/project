from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from src.routers.deployments import router as deployment_router
from src.exceptions import ServiceException
import uvicorn

app = FastAPI()

@app.exception_handler(ServiceException)
async def unicorn_exception_handler(request: Request, exc: ServiceException):
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )


app.include_router(deployment_router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
