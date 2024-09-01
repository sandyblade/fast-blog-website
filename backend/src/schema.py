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

from pydantic import BaseModel, EmailStr, Field
from typing import List

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
    
class UserForgotSchema(BaseModel):
    email: EmailStr
    
class UserResetSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    
class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    
class UserProfileSchema(BaseModel):
    email: EmailStr
    phone: str = Field(..., min_length=7)
    first_name: str = Field(..., min_length=3)
    last_name: str = Field(..., min_length=3)
    gender: str = Field(..., min_length=1)
    address: str | None = None
    country: str | None = None
    instagram: str | None = None
    facebook: str | None = None
    twitter: str | None = None
    linked_in: str | None = None
    job_title: str | None = None
    about_me: str | None = None
    
class UserPasswordSchema(BaseModel):
    current_password: str = Field(..., min_length=8)
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)
    
class ArticleSchema(BaseModel):
    title: str = Field(..., min_length=7)
    description: str = Field(..., min_length=10)
    content: str = Field(..., min_length=10)
    status: int
    categories: List[str] | None = None
    tags: List[str] | None = None
    
class ArticleCommentSchema(BaseModel):
    comment: str = Field(..., min_length=10)
    parent_id: int | None = None