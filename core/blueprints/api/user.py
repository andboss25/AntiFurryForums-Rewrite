"""The user api , this will also contain functions related to users."""

import sqlite3
import os
import time
import random
import json

from flask import request
from flask import jsonify
from flask import Blueprint
from flask_limiter import Limiter

from core.utils import log
from core.utils import config
from core.utils import hash
from core.utils import ip
from core.utils import auth

config_loader = config.ConfigSet()
logger = log.DataLogger("users-created","general").get_logger()
security_logger = log.DataLogger("user-security","security").get_logger()
user_blueprint = Blueprint("users",__name__)

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
        
    def is_valid_token(token:str):
        db = initialize_database()
        data = db.execute(
            "SELECT * FROM users WHERE token=?",(token,)
        ).fetchone()
        
        if data is not None:
            return True
        
        return False

# Raw CRUD functions
class Sanitize:
    """A class for cleanup filter functions for security purposes and constrains"""
    def constraint_username(username:str):
        if len(username) > 32 or len(username) < 3:
            return False,{"error":"Username must be between 3 and 32 characters!"}
        
        banned_characters = ''' <>/?'!@#$%^&*()-+="\\`~|;,:'''

        if any(c in banned_characters for c in username):
            return False,{"error":"Username must not contain special characters or spaces (. and _ are an exception)"}
        
        return True,None

class RawUserCRUD:
    """Raw CRUD functions for users"""

    # CREATE
    def create_user(username:str,password:str):
        """
        Create a user with given password

        Returns a tuple of (sccuess:bool,token,error_code)
        
        """

        if type(username) is not str:
            security_logger.info(f"Username of unusual type detected '{username}'!")
            return False,None,"Request blocked, skid detected!"
        
        if type(password) is not str:
            security_logger.info(f"Password of unusual type detected '{password}'!")
            return False,None,"Request blocked, skid detected!"

        sanitize_result = Sanitize.constraint_username(username)

        if username is None or password is None:
            return False,None,{"error":"Username or password is empty!"}
        
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

            logger.info(f"Account created with username: {username}")
            return True,tk,None
        except sqlite3.IntegrityError:
            return False,None,{"error":"Username already used!"}
        
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
    
    def get_token(username:str):
        data = RawUserCRUD.view_user(username)
        return data.get("token")


@user_blueprint.route("/signup",methods = ["post"])
def create_user_api():
    data = request.json
    user_result = RawUserCRUD.create_user(
        data.get("username"),
        data.get("password")
    )

    if not user_result[0]:
        return jsonify(user_result[2])
    
    return jsonify({"token":user_result[1]})

@user_blueprint.route("/login",methods = ["post"])
def login_user_api():
    data = request.json
        
    username = data.get("username")
    password = data.get("password")

    if type(username) is not str:
        security_logger.info(f"Username of unusual type detected '{username}'!")
        return "Request blocked, skid detected!",403
    
    if type(password) is not str:
        security_logger.info(f"Password of unusual type detected '{password}'!")
        return "Request blocked, skid detected!",403

    password = hash.generate_hash_512_HEXDIGEST(password)

    user_data = RawUserCRUD.view_user(username)

    if user_data == None:
        return jsonify({"error":"User does not exist"})
    
    if not password == user_data.get("password"):
        return jsonify({"error":"Invalid password"})
    
    token = RawUserCRUD.get_token(username)

    return jsonify({"token":token})

@auth.authenticate()
@user_blueprint.route("/viewall")
def view_all_users_api():
    
    users = RawUserCRUD.list_users_safe()

    data = {
        "users": users,
        "count": len(users)
    }
    
    return jsonify(data)

@auth.authenticate()
@user_blueprint.route("/viewuser")
def view_user_api():
    data = request.args
    username = data.get("username")
    return RawUserCRUD.view_user_safe(username) or jsonify({})

