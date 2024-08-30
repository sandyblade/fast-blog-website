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

from sqlalchemy import Column, ForeignKey, String, DateTime,  Text
from sqlalchemy.dialects.mysql import  BIGINT, TINYINT, LONGTEXT, INTEGER
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mariadb_engine': 'InnoDB'}
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True)
    email = Column(String(180), index=True, nullable=False, unique=True)
    phone = Column(String(64), index=True, nullable=True, unique=True)
    password = Column(String(255), index=True, nullable=False, unique=False)
    image = Column(String(255), index=True, nullable=True, unique=False)
    first_name = Column(String(191), index=True, nullable=True, unique=False)
    last_name = Column(String(191), index=True, nullable=True, unique=False)
    gender = Column(String(2), index=True, nullable=True, unique=False)
    job_title = Column(String(191), index=True, nullable=True, unique=False)
    country = Column(String(191), index=True, nullable=True, unique=False)
    instagram = Column(String(255), index=True, nullable=True)
    facebook = Column(String(255), index=True, nullable=True)
    twitter = Column(String(255), index=True, nullable=True)
    linked_in = Column(String(255), index=True, nullable=True)
    address = Column(Text(), nullable=True)
    about_me = Column(Text(), nullable=True)
    reset_token = Column(String(36), index=True, nullable=True)
    confirm_token = Column(String(36), index=True, nullable=True)
    confirmed = Column(TINYINT(unsigned=True), index=True, default=0)
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    activities = relationship("Activity", back_populates="user")
    articles = relationship("Article", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    viewers = relationship("Viewer", back_populates="user")
    
class Activity(Base):
    __tablename__ = 'activities'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mariadb_engine': 'InnoDB'}
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey('users.id'))
    event = Column(String(191), index=True, nullable=False, unique=False)
    description = Column(String(255), index=True, nullable=False, unique=False)
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="activities")
    
class Article(Base):
    __tablename__ = 'articles'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mariadb_engine': 'InnoDB'}
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey('users.id'))
    image = Column(String(255), index=True, nullable=True, unique=False)
    title = Column(String(255), index=True, nullable=False, unique=True)
    slug = Column(String(255), index=True, nullable=False, unique=True)
    description = Column(String(255), index=True, nullable=False, unique=False)
    content = Column(LONGTEXT(), nullable=False)
    categories = Column(LONGTEXT(), nullable=True)
    tags = Column(LONGTEXT(), nullable=True)
    total_viewer = Column(INTEGER(unsigned=True), index=True, default=0)
    total_comment = Column(INTEGER(unsigned=True), index=True, default=0)
    status = Column(TINYINT(unsigned=True), index=True, default=0)
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="articles")
    viewers = relationship("Viewer", back_populates="user")
    
class Comment(Base):
    __tablename__ = 'comments'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mariadb_engine': 'InnoDB'}
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True)
    parent_id = Column(BIGINT(unsigned=True), ForeignKey('comments.id'), nullable=True)
    article_id = Column(BIGINT(unsigned=True), ForeignKey('articles.id'))
    user_id = Column(BIGINT(unsigned=True), ForeignKey('users.id'))
    message = Column(Text(), nullable=True)
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    article = relationship("Article", back_populates="viewers")
    user = relationship("User", back_populates="comments")
    parent = relationship("Comment", backref='comments',remote_side=[id])
    
class Notification(Base):
    __tablename__ = 'notifications'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mariadb_engine': 'InnoDB'}
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey('users.id'))
    subject = Column(String(191), index=True, nullable=False, unique=False)
    message = Column(String(255), index=True, nullable=False, unique=False)
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    user = relationship("User", back_populates="notifications")
    
class Viewer(Base):
    __tablename__ = 'viewers'
    __table_args__ = {'mysql_engine': 'InnoDB', 'mariadb_engine': 'InnoDB'}
    
    id = Column(BIGINT(unsigned=True), primary_key=True, index=True)
    user_id = Column(BIGINT(unsigned=True), ForeignKey('users.id'))
    article_id = Column(BIGINT(unsigned=True), ForeignKey('articles.id'))
    status = Column(TINYINT(unsigned=True), index=True, default=0)
    created_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, index=True, default=datetime.datetime.utcnow)
    article = relationship("Article", back_populates="viewers")
    user = relationship("User", back_populates="viewers")