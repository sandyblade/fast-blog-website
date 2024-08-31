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

from fastapi import APIRouter, Depends, Security
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.encoders import jsonable_encoder
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .security import JWTBearer
from .auth import auth_user
from .database import get_db
from .schema import *
from .model import *

notification_route = APIRouter()
security = HTTPBearer()

@notification_route.get("/api/notification/list",  dependencies=[Depends(JWTBearer())], tags=["account_notification_list"])
def notification_list(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db),
        page: int = 1,
        limit: int = 10,
        order_dir: str = "notifications.id",
        order_desc: str = "desc",
        search: str | None = None
    ):
   
    offset = ((page-1)*limit)
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    total = db.query(Notification).filter(User.id == user_id).count()
    data = db.query(Notification).order_by(text(f"{order_dir} {order_desc}")).filter(User.id == user_id)
    
    if search != None:
        data = data.filter(or_(Notification.subject.ilike(f'%{search}%'), Notification.message.ilike(f'%{search}%')))
        
    data = data.limit(limit).offset(offset)

    payload = {
        "total": total,
        "data": data.all()
    }
   
    return JSONResponse(content=jsonable_encoder(payload), status_code=200)

@notification_route.get("/api/notification/read/{id}",  dependencies=[Depends(JWTBearer())], tags=["account_notification_read"])
def notification_read(id: int, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    notification = db.query(Notification).filter(and_(Notification.id == id, Notification.user == session_user)).first()
    
    if not notification:
        return JSONResponse(content=f"Notification with id {id} was not found.!!", status_code=400)
    
    return JSONResponse(content=jsonable_encoder(notification), status_code=200)

@notification_route.delete("/api/notification/remove/{id}",  dependencies=[Depends(JWTBearer())], tags=["account_notification_remove"])
def notification_remove(id: int, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    notification = db.query(Notification).filter(and_(Notification.id == id, Notification.user == session_user)).first()
    
    if not notification:
        return JSONResponse(content=f"Notification with id {id} was not found.!!", status_code=400)
    
    db.delete(notification)
    db.commit()
    
    activity = Activity(
        user = session_user,
        event = "Delete notification",
        description = f"The user delete notification with subject {notification.subject}",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    return JSONResponse(content="ok", status_code=200)