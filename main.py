from fastapi import FastAPI
from router import router as rout

app = FastAPI()

app.include_router(rout)