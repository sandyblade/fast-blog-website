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
from sqlalchemy import or_, and_, select
from sqlalchemy.orm import Session, load_only
from sqlalchemy.sql import text
from slugify import slugify
from faker import Faker
from .security import JWTBearer
from .auth import auth_user
from .database import get_db
from .schema import *
from .model import *

import shutil
import uuid
import pathlib

article_route = APIRouter()
security = HTTPBearer()

@article_route.get("/api/article/list", tags=["article_list"])
def article_list(
        db: Session = Depends(get_db),
        page: int = 1,
        limit: int = 10,
        order_dir: str = "articles.id",
        order_desc: str = "desc",
        search: str | None = None
    ):
   
    offset = ((page-1)*limit)
    total = db.query(Article).filter(Article.status == 1).count()
    
    data = db.query(Article, User).join(User).order_by(text(f"{order_dir} {order_desc}")).filter(Article.status == 1)
        
    if search != None:
        data = data.filter(or_(
            Article.title.ilike(f'%{search}%'), 
            Article.description.ilike(f'%{search}%'),
            Article.content.ilike(f'%{search}%'),
            Article.categories.ilike(f'%{search}%'),
            Article.tags.ilike(f'%{search}%')
        ))
        
    data = data.limit(limit).offset(offset)
    results = data.all()
    articles = []
    
    for row in results:
        articles.append({
            "id": row[0].id,
            "image": row[0].image,
            "title": row[0].title,
            "slug": row[0].slug,
            "description": row[0].description,
            "categories": row[0].categories.split(','),
            "tags": row[0].tags.split(','),
            "total_viewer": row[0].total_viewer,
            "total_comment": row[0].total_comment,
            "created_at": row[0].created_at,
            "updated_at": row[0].updated_at,
            "user": {
                "image":row[1].image,
                "first_name":row[1].first_name,
                "last_name":row[1].last_name,
                "gender":row[1].gender  
            },
        })
    
    payload = {
        "total": total,
        "list": articles
    }

    return JSONResponse(content=jsonable_encoder(payload), status_code=200)

@article_route.post("/api/article/create",  dependencies=[Depends(JWTBearer())], tags=["article_create"])
def article_create(form: ArticleSchema, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    
    _article = db.query(Article).filter(Article.title == form.title).first()
    
    if _article != None:
        return JSONResponse(content=f"Article with title {form.title} already exists. Please try with another one.", status_code=400)
    
    article = Article(
        user = session_user,
        title = form.title,
        slug = slugify(form.title),
        description = form.description,
        content = form.content,
        categories = ','.join(form.categories),
        tags = ','.join(form.tags),
        status = form.status,
        created_at = date_now,
        updated_at = date_now
    )
    db.add(article)
    db.commit()
    
    activity = Activity(
        user = session_user,
        event = "Create New Article",
        description = f"A new article with title {form.title} has been created.",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    article = db.query(Article).filter(Article.slug == slugify(form.title)).first()
    
    return JSONResponse(content=jsonable_encoder(article), status_code=200)


@article_route.get("/api/article/read/{slug}",  dependencies=[Depends(JWTBearer())], tags=["article_read"])
def article_read(slug: str, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    article = db.query(Article).filter(Article.slug == slug).first()
    
    if not article:
        return JSONResponse(content=f"Article with slug {slug} was not found.!!", status_code=400)
    
    total = db.query(Viewer).filter(and_(Viewer.article == article, Viewer.user == session_user)).count()
    
    if total == 0:
        
        viewer = Viewer(
            article = article,
            user = session_user,
            created_at = date_now,
            updated_at = date_now,
        )
        db.add(viewer)
        db.commit()
        
        db.query(Article).filter(Article.id == article.id).update({ 'total_viewer': (article.total_viewer + 1), 'updated_at': date_now }, synchronize_session=False)
        db.commit()
        
        activity = Activity(
            user = session_user,
            event = "Read Article",
            description = f"The user {session_user.email} view to your article with title {article.title}.",
            created_at = date_now,
            updated_at = date_now,
        )
        db.add(activity)
        db.commit()
        
    payload = {
        "message": "ok",
        "data": {
            "id": article.id,
            "image": article.image,
            "title": article.title,
            "slug": article.slug,
            "description": article.description,
            "categories": article.categories.split(','),
            "tags": article.tags.split(','),
            "total_viewer": article.total_viewer,
            "total_comment": article.total_comment,
            "created_at": article.created_at,
            "updated_at": article.updated_at,
            "user": {
                "image": article.user.image,
                "first_name":article.user.first_name,
                "last_name":article.user.last_name,
                "gender":article.user.gender,
                "facebook":article.user.facebook,
                "instagram":article.user.instagram,
                "twitter":article.user.twitter,
                "linked_in":article.user.linked_in,
                "about_me":article.user.about_me
            }
        }
    }
            
    return JSONResponse(content=jsonable_encoder(payload), status_code=200)

@article_route.delete("/api/article/remove/{id}",  dependencies=[Depends(JWTBearer())], tags=["article_remove"])
def article_remove(id: int, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    article = db.query(Article).filter(and_(Article.id == id, Article.user == session_user)).first()
    
    if not article:
        return JSONResponse(content=f"Article with id {id} was not found.!!", status_code=400)
    
    db.delete(article)
    db.commit()
    
    activity = Activity(
        user = session_user,
        event = "Delete article",
        description = f"An a article with title {article.title} has been deleted.",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
        
    return JSONResponse(content="ok", status_code=200)

@article_route.get("/api/article/user", tags=["article_user"])
def article_user(
        credentials: HTTPAuthorizationCredentials = Security(security),
        db: Session = Depends(get_db),
        page: int = 1,
        limit: int = 10,
        order_dir: str = "articles.id",
        order_desc: str = "desc",
        search: str | None = None
    ):
   
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    offset = ((page-1)*limit)
    total = db.query(Article).filter(Article.user_id == user_id).count()
    
    data = db.query(Article, User).join(User).order_by(text(f"{order_dir} {order_desc}")).filter(Article.status == 1)
        
    if search != None:
        data = data.filter(or_(
            Article.title.ilike(f'%{search}%'), 
            Article.description.ilike(f'%{search}%'),
            Article.content.ilike(f'%{search}%'),
            Article.categories.ilike(f'%{search}%'),
            Article.tags.ilike(f'%{search}%')
        ))
        
    data = data.limit(limit).offset(offset)
    results = db.execute(data).all()
    articles = []
    
    for row in results:
        articles.append({
            "id": row[0].id,
            "image": row[0].image,
            "title": row[0].title,
            "slug": row[0].slug,
            "description": row[0].description,
            "categories": row[0].categories.split(','),
            "tags": row[0].tags.split(','),
            "total_viewer": row[0].total_viewer,
            "total_comment": row[0].total_comment,
            "created_at": row[0].created_at,
            "updated_at": row[0].updated_at,
            "user": {
                "image":row[1].image,
                "first_name":row[1].first_name,
                "last_name":row[1].last_name,
                "gender":row[1].gender  
            },
        })
    
    payload = {
        "total": total,
        "list": articles
    }

    return JSONResponse(content=jsonable_encoder(payload), status_code=200)


@article_route.put("/api/article/update/{id}",  dependencies=[Depends(JWTBearer())], tags=["article_update"])
def article_update(id: int, form: ArticleSchema, credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    
    _article = db.query(Article).filter(and_(Article.id != id, Article.title == form.title)).first()
    
    if _article != None:
        return JSONResponse(content=f"Article with title {form.title} already exists. Please try with another one.", status_code=400)
    

    update_article = {
        'title' : form.title,
        'slug' : slugify(form.title),
        'description' : form.description,
        'content' : form.content,
        'categories' : ','.join(form.categories),
        'tags' : ','.join(form.tags),
        'status' : form.status,
        'updated_at' : date_now
    }
    db.query(Article).filter(Article.id == id).update(update_article, synchronize_session=False)
    db.commit()
    
    activity = Activity(
        user = session_user,
        event = "Edit Article",
        description = f"An article with title {form.title} has been modified.",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    article = db.query(Article).filter(Article.id == id).first()
    
    return JSONResponse(content=jsonable_encoder(article), status_code=200)


@article_route.get("/api/article/words",  dependencies=[Depends(JWTBearer())], tags=["article_words"])
def article_words(max: int = 10):
    
    result = []
    
    for _ in range(max):
        fake = Faker()
        result.append(' '.join(fake.words(2)).title())
    
    result.sort()
    
    return JSONResponse(content=jsonable_encoder(result), status_code=200)

@article_route.post("/api/article/upload/{id}",  dependencies=[Depends(JWTBearer())], tags=["account_upload"])
def article_upload(id: int, file_image: UploadFile = File(...), db: Session = Depends(get_db), credentials: HTTPAuthorizationCredentials = Security(security)):
    
    date_now = datetime.datetime.now()
    access_token = credentials.credentials
    session = auth_user(access_token)
    user_id = session["id"]
    session_user = db.query(User).filter(User.id == user_id).first()
    article = db.query(Article).filter(and_(Article.id == id, Article.user == session_user)).first()
    
    if not article:
        return JSONResponse(content=f"Article with id {id} was not found.!!", status_code=400)
    
    image = article.image
    ext = file_image.filename.split(".")[-1]
    file_name = str(uuid.uuid4())
    path = f"uploads/{file_name}.{ext}"
    with open(path, 'w+b') as file:
        shutil.copyfileobj(file_image.file, file)
        
        if image != None:
            pathlib.Path(f"./{image}").unlink(missing_ok=True)
        
        image = path
        
    update_article = { 'image': image,  'updated_at' : date_now }
    db.query(Article).filter(Article.id == id).update(update_article, synchronize_session=False)
    db.commit()
    
    activity = Activity(
        user = session_user,
        event = "Upload Article Image",
        description = "Upload new user article image",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    payload = {
        "image": image,
        "message": "Your article image has been changed"
    }
    
    return JSONResponse(content=jsonable_encoder(payload), status_code=200)