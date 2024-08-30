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

import random
import os
import uuid
import datetime

from faker import Faker
from faker.providers import internet, job
from .database import get_db
from dotenv import load_dotenv
from random import randint
from passlib.context import CryptContext
from .model import * 

load_dotenv()

class Seed:
    
    def run(self):
        APP_ENV = os.getenv("APP_ENV")
        if(APP_ENV == 'development'):
            self.seed_user()
            
    def hash_pass(self, password:str):
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        return pwd_context.hash(password)
            
    def seed_user(self):
        db = next(get_db())
        total_user = db.query(User).count()
        _max = 100
        if total_user == 0:
            for _ in range(_max):
                fake = Faker()
                fake.add_provider(job)
                gender = random.randint(1,2)
                gender_char = "M" if gender == 1 else "F"
                first_name = fake.first_name_male() if gender == 1 else fake.first_name_female()
                last_name = fake.last_name()
                email = fake.ascii_safe_email()
                password = self.hash_pass("P@ssw0rd!123")
                user = User(
                    email = email,
                    phone = fake.phone_number(),
                    password = password,
                    first_name = first_name,
                    last_name = last_name,
                    gender = gender_char,
                    job_title = fake.job(),
                    instagram = fake.user_name(),
                    facebook = fake.user_name(),
                    twitter = fake.user_name(),
                    linked_in = fake.user_name(),
                    country =  fake.country(),
                    address = fake.street_address(),
                    about_me = fake.paragraph(nb_sentences=5),
                    confirmed = 1
                )
                db.add(user)
            db.commit()