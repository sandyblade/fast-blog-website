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