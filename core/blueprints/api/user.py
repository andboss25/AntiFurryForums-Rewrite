"""The user api , this will also contain functions related to users."""

import sqlite3
import os
import time
import random
import json

from flask import Blueprint

from core.utils import log
from core.utils import config
from core.utils import hash

config_loader = config.ConfigSet()
logger = log.DataLogger("users-created","general").get_logger()
blueprint = Blueprint("users",__name__)

def initialize_database():
    db = sqlite3.connect(
        os.path.join(
            "data",
            "users.db"
        ),
        autocommit=True
    )

    init_script_path = ["core","blueprints","api","queries","user_table.sql"]

    f = open(os.path.join(*init_script_path))
    script = f.read()
    f.close()

    db.executescript(script)

    return db

# Raw token functions
class Token:
    """A class for all token related tasks"""
    def generate(username:str):
        data = {
            "username":username,
            "gts_":time.time(),
            "sec_":random.randint(
                1_000_000,
                9_999_999
            )
        }

        data = json.dumps(data)
        return hash.encode_base_64(data)

# Raw CRUD functions
class Sanitize:
    """A class for cleanup filter functions for security purposes and constrains"""
    def constraint_username(username:str):
        if len(username) > 32 or len(username) < 3:
            return False,"Username must be between 3 and 32 characters!"
        
        banned_characters = ''' <>/?'!@#$%^&*()-+="\\`~|;,:'''

        if any(c in banned_characters for c in username):
            return False,"Username must not contain special characters or spaces (. and _ are an exception)"
        
        return True,None

class RawUserCRUD:
    """Raw CRUD functions for users"""

    # CREATE
    def create_user(username:str,password:str):
        """
        Create a user with given password

        Returns a tuple of (sccuess:bool,token,error_code)
        
        """

        sanitize_result = Sanitize.constraint_username(username)
        
        if not sanitize_result[0]:
            return False,None,sanitize_result[1]
        
        db = initialize_database()
        password = hash.generate_hash_512_HEXDIGEST(password)
        tk = Token.generate(username)
        try:
            db.execute(
                "INSERT INTO users(username,password_hash,token) VALUES (?,?,?)",
                (
                    username,
                    password,
                    tk
                )
            )

            return True,tk,None
        except sqlite3.IntegrityError:
            return False,None,"Username already used!"
        
    # READ
    def list_users() -> dict[str]:
        """List all users as a dictionary"""
        db = initialize_database()
        data = db.execute("SELECT * FROM users").fetchall()
        return_users = {}
        for user in data:
            return_users[user[0]] = {
                "token":user[1],
                "password":user[2],
                "creation_date":user[3]
            }
        
        return return_users
    
    def list_users_safe() -> dict[str]:
        """List all users as a dictionary (safe for user access)"""
        data = RawUserCRUD.list_users()
        
        for user in data:
            data[user].pop("password")
            data[user].pop("token")
        
        return data
    
    def view_user(username:str) -> dict[str]:
        """Return all data of a user"""
        db = initialize_database()
        data = db.execute(
            "SELECT * FROM users WHERE username=?",(username,)
        ).fetchone()

        if data is None:
            return None
        
        return_user = {}
        return_user['username'] = data[0]
        return_user['token'] = data[1]
        return_user['password'] = data[2]
        return_user['creation_date'] = data[3]
        
        return return_user

    def view_user_safe(username:str):
        """Return all data of a user (safe for user access)"""
        data = RawUserCRUD.view_user(username)

        if data == None:
            return None
        data.pop("password")
        data.pop("token")

        return data
