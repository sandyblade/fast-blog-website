"""
 * This file is part of the Sandy Andryanto Blog Application.
 *
 * @author     Sandy Andryanto <sandy.andryanto.blade@gmail.com>
 * @copyright  2024
 *
 * For the full copyright and license information,
 * please view the LICENSE.md file that was distributed
 * with this source code.
"""

from src.model import *
from src.database import engine, Base
from src import database
from src.view_auth import auth_route
from src.view_account import account_route
from src.view_notification import notification_route
from src.view_article import article_route
from src.seed import Seed
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

Base.metadata.create_all(bind=engine)

seed = Seed()
seed.run()

Path("uploads").mkdir(parents=True, exist_ok=True)

app = FastAPI()
app.include_router(auth_route)
app.include_router(account_route)
app.include_router(notification_route)
app.include_router(article_route)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])