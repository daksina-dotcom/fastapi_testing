from fastapi import FastAPI
from .routers import users
from .database import engine
from . import models

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router)
