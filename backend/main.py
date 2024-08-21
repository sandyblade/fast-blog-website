from src.models.model_auth import *
from src.models.model_reference import *
from src.models.model_core import *
from src.configs.database import engine
from src.configs import database
from src.data.seeds import Seed
from src.views.view_account import *
from src.views.view_auth import *
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


database.Base.metadata.create_all(bind=engine)

seed = Seed()
seed.run()

app = FastAPI()
app.include_router(view_account)
app.include_router(view_auth)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])