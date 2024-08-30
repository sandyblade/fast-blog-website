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


def token_response(token: str):
    return {
        "access_token": token
    }  

def signJWT(UserId: str) -> Dict[str, str]:
    load_dotenv()
    JWT_SECRET = os.getenv("JWT_SECRET_KEY")
    payload = {
        "UserId": UserId,
        "expires": time.time() + 9000000000
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    return token_response(token)


def decodeJWT(token: str) -> dict:
    load_dotenv()
    JWT_SECRET = os.getenv("JWT_SECRET_KEY")
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}