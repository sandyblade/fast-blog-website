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

from fastapi import APIRouter, Depends, Security, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from .security import JWTBearer
from .auth import auth_user
from .database import get_db
from .schema import *
from .model import *

comment_route = APIRouter()
security = HTTPBearer()

def BuildTree(elements: list, parent_id: int | None = None):
    result = []
    for element in elements:
        if element["parent_id"] == parent_id:
            children = BuildTree(elements, element["id"])
            if len(children) > 0:
                element["children"] = children
            else:
                element["children"] = []
            result.append(element)
    return result

@comment_route.get("/api/comment/list/{id}", tags=["comment_list"])
def comment_list(id: int, db: Session = Depends(get_db)):
    
    article = db.query(Article).filter(Article.id == id).first()
    
    if not article:
        return JSONResponse(content=f"Article with id {id} was not found.!!", status_code=400)
    
    data = db.query(Comment, User).join(User).order_by(text("comments.id desc")).filter(Comment.article_id == id).all()
    result = []
    
    for comment in data:
        result.append({
            'id': comment[0].id,
            'parent_id': comment[0].parent_id,
            'message': comment[0].message,
            'created_at': comment[0].created_at,
            'user': {
                'image': comment[1].image,
                'first_name': comment[1].first_name,
                'last_name': comment[1].last_name,
                'gender': comment[1].gender,
                'email': comment[1].email
            }
        })
    
    payload = {
        'message': 'ok',
        'data': BuildTree(result)
    }
    
    return JSONResponse(content=jsonable_encoder(payload), status_code=200)


@comment_route.post("/api/comment/create/{id}",  dependencies=[Depends(JWTBearer())], tags=["comment_create"])
def comment_create(id: int, input: ArticleCommentSchema, db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Security(security)):
    
    article = db.query(Article).filter(Article.id == id).first()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    
    if not article:
        return JSONResponse(content=f"Article with id {id} was not found.!!", status_code=400)
    
    date_now = datetime.datetime.now()
    comment = Comment(
        article_id = id,
        user_id = user_id,
        parent_id = input.parent_id,
        message = input.comment,
        created_at = date_now,
        updated_at = date_now
    )
    db.add(comment)
    db.commit()
    
    activity = Activity(
        user = session_user,
        event = input.parent_id is not None if input.parent_id == "Reply comment to article" else "Create comment to article",
        description = input.parent_id is not None if input.parent_id == f"Comment of article {article.title} as been replied" else f"Comment of article ${article.title} as been created",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    if user_id != article.user_id:
        notification = Notification(
            user = session_user,
            subject = input.parent_id is not None if input.parent_id == "Reply comment to article" else "Create comment to article",
            message = input.parent_id is not None if input.parent_id == f"Comment of article {article.title} as been replied" else f"Comment of article ${article.title} as been created",
            created_at = date_now,
            updated_at = date_now,
        )
        db.add(notification)
        db.commit()
        
    total_comment = db.query(Comment).filter(Comment.article == article).count()
    db.query(Article).filter(Article.id == article.id).update({ 'total_comment': total_comment, 'updated_at': date_now }, synchronize_session=False)
    db.commit()
    
    return JSONResponse(content="ok", status_code=200)

@comment_route.delete("/api/comment/remove/{id}",  dependencies=[Depends(JWTBearer())], tags=["comment_remove"])
def comment_remove(id: int, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    comment = db.query(Comment).filter(and_(Comment.id == id, Comment.user == session_user)).first()
    
    if not comment:
        return JSONResponse(content=f"Comment with id {id} was not found.!!", status_code=400)
    
    db.delete(comment)
    db.commit()
    
    article = db.query(Article).filter(Article.id == comment.article_id).first()
    
    activity = Activity(
        user = session_user,
        event = "Delete comment",
        description = f"The user delete comment of article with title {article.title}",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    total_comment = db.query(Comment).filter(Comment.article == article).count()
    db.query(Article).filter(Article.id == article.id).update({ 'total_comment': total_comment, 'updated_at': date_now }, synchronize_session=False)
    db.commit()
    
    return JSONResponse(content="ok", status_code=200)