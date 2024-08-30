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

import time
import jwt
import os

from typing import Dict
from dotenv import load_dotenv
from .database import get_db
from .model import User

def token_response(token: str):
    return {
        "access_token": token
    }  

def signJWT(UserId: str) -> Dict[str, str]:
    load_dotenv()
    JWT_SECRET = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    payload = {
        "UserId": UserId,
        "expires": time.time() + 9000000000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm= ALGORITHM)
    return token_response(token)


def decodeJWT(token: str) -> dict:
    load_dotenv()
    JWT_SECRET = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}
    
def auth_user(token: str) -> dict:
    db = next(get_db())
    user_decode = decodeJWT(token)
    email = user_decode["UserId"]
    result = db.query(User).filter(User.email == email).first().__dict__
    result.pop("password")
    return result