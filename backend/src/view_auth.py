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

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from password_strength import PasswordPolicy
from passlib.context import CryptContext
from random import randint
from .model import *
from .auth import signJWT
from .database import get_db
from .schema import * 

import datetime
import uuid

auth_route = APIRouter()

@auth_route.post("/api/auth/login", tags=["auth_login"])
def auth_login(user: UserLoginSchema, db: Session = Depends(get_db)):
    
    auth_user =  db.query(User).filter(User.email == user.email).first()
    
    if auth_user != None:
        
        date_now = datetime.datetime.now()
        user_password = auth_user.password
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        verify = pwd_context.verify(user.password, user_password)
        
        # Check password from current user
        if verify == False:
            return JSONResponse(content="The password your entered is incorrect. Please try again.", status_code=401)
        
        # Check Confirmation
        verification = db.query(User).filter(and_(User.email == user.email, User.confirmed == 1)).count()
        if verification == 0:
            return JSONResponse(content="We have sent you an email confirmation. Please confirm your email and then we will active your account.", status_code=401)
        
        activity = Activity(
            user = auth_user,
            event = "Sign In",
            description = "Sign in to application",
            created_at = date_now,
            updated_at = date_now,
        )
        db.add(activity)
        db.commit()
        
        return signJWT(auth_user.email)
        
    # Account was not founded
    return JSONResponse(content="You have entered an invalid credential and password. Please try again.", status_code=401)


@auth_route.post("/api/auth/register", tags=["auth_register"])
def auth_register(user: UserRegisterSchema, db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    user_email = db.query(User).filter(User.email == user.email).first()
    
    if user_email != None:
        return JSONResponse(content="User with e-mail address `"+user.email+"` already exists. Please try with another one.", status_code=400)
    
    if user.password != user.password_confirm:
        return JSONResponse(content="Please make sure your passwords match.", status_code=400)
        
    policy = PasswordPolicy.from_names(length=8, uppercase=1, numbers=1,  special=1, nonletters=1)
    check_policy = policy.test(user.password)
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash_password = pwd_context.hash(user.password)
    
    if len(check_policy) > 0:
        return JSONResponse(content="Password is weak. Recommended passwords contain at least 8 characters, one uppercase, one lowercase, one number, and one special character.", status_code=400)
    
    new_user = User(
        email = user.email,
        password = hash_password,
        updated_at = date_now,
        confirmed = 1
    )
    db.add(new_user)
    db.commit()

    activity = Activity(
        user = new_user,
        event = "Sign Up",
        description = "Register new user account",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()

    return JSONResponse(content="Your account has been created. Please check your email for the confirmation message we just sent you.", status_code=200)

@auth_route.get("/api/auth/confirm/{token}", tags=["auth_confirm"])
def auth_confirm(token: str, db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    user = db.query(User).filter(and_(User.confirm_token == token, User.confirmed == 0)).first()
    
    if not user:
        return JSONResponse(content="This e-mail confirmation token is invalid.", status_code=400)
     
    update_user = {
        'confirmed' : 1,
        'confirm_token': None,
        'updated_at' : date_now
    }
    db.query(User).filter(User.id == user.id).update(update_user, synchronize_session=False)
    db.commit()
    
    activity = Activity(
        user = user,
        event = "Email Verification",
        description = "Confirm new member registration account",
        created_at = date_now,
        updated_at = date_now,
    )
    db.add(activity)
    db.commit()
    
    db.refresh(user)
    
    return JSONResponse(content="Your registration is complete. Now you can login.", status_code=200)

@auth_route.post("/api/auth/email/forgot", tags=["auth_email_forgot"])
def auth_email_forgot(user: UserForgotSchema, db: Session = Depends(get_db)):
    
    date_now = datetime.datetime.now()
    auth_user = db.query(User).filter(User.email == user.email).first()
    
    if auth_user != None:
        
        verification = db.query(User).filter(and_(User.email == user.email, User.confirmed == 0)).count()
        if verification > 0:
            return JSONResponse(content="We have sent you an email confirmation. Please confirm your email and then we will active your account.", status_code=401)
         
        update_user = {
            'reset_token': str(uuid.uuid4()),
            'updated_at' : date_now
        }
        db.query(User).filter(User.id == auth_user.id).update(update_user, synchronize_session=False)
        db.commit()
        
        activity = Activity(
            user = auth_user,
            event = "Forgot Password",
            description = "Request reset password link",
            created_at = date_now,
            updated_at = date_now,
        )
        db.add(activity)
        db.commit()
        
        db.refresh(auth_user)
        
        return JSONResponse(content="An email has been sent to "+user.email+" with further password reset information. Thank you.", status_code=200)
    
    # Account with email was not founded
    return JSONResponse(content="A user was not found for this e-mail address.", status_code=401)

@auth_route.post("/api/auth/email/reset/{token}", tags=["auth_email_reset"])
def auth_email_reset(token: str, user: UserResetSchema, db: Session = Depends(get_db)):
    
    auth_user = db.query(User).filter(User.email == user.email).first()
    date_now = datetime.datetime.now()
    
    if auth_user != None:
        
        # Check Reset Token
        password_reset = db.query(User).filter(and_(User.email == user.email, User.reset_token == token, User.reset_token != None)).count()
        if password_reset == 0:
            return JSONResponse(content="We can't find a user with that e-mail address or password reset token is invalid.", status_code=400)
        
        if user.password != user.password_confirm:
            return JSONResponse(content="Please make sure your passwords match.", status_code=400)
        
        policy = PasswordPolicy.from_names(length=8, uppercase=1, numbers=1,  special=1, nonletters=1)
        check_policy = policy.test(user.password)
        
        if len(check_policy) > 0:
            return JSONResponse(content="This password reset token is invalid.", status_code=400)
            
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hash_password = pwd_context.hash(user.password)
        
        update_user = {
            'reset_token': None,
            'confirm_token': None,
            'confirmed': 1,
            'password': hash_password,
            'updated_at': datetime.datetime.now()
        }
        
        db.query(User).filter(User.id == auth_user.id).update(update_user, synchronize_session=False)
        db.commit()
        
        activity = Activity(
            user = auth_user,
            event = "Reset Password",
            description = "Reset account password",
            created_at = date_now,
            updated_at = date_now,
        )
        db.add(activity)
        db.commit()
        
        db.refresh(auth_user)
        
        return JSONResponse(content="You have successfully updated your password.", status_code=200)
    
    # Account with email was not founded
    return JSONResponse(content="A user was not found for this credential.", status_code=401)