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
    address: str
    country: str
    instagram: str
    facebook: str
    twitter: str
    linked_in: str
    job_title: str
    about_me: str
    
class UserPasswordSchema(BaseModel):
    current_password: str = Field(..., min_length=8)
    password: str = Field(..., min_length=8)
    password_confirm: str = Field(..., min_length=8)