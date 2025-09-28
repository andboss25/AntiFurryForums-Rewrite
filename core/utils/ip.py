"""Ip adress util"""

try:
    from core.utils import config
except ModuleNotFoundError:
    import config

try:
    from core.utils import log
except ModuleNotFoundError:
    import log

import flask
from flask import request

import sqlite3

import os


config_loader = config.ConfigSet()
logger = log.DataLogger("ip-util-anomaly","anomaly").get_logger()
breach_logger = log.DataLogger("ratelimit-breaches","security").get_logger()

forward_ip_header = config_loader.get_value(
    config_loader.main_config_file_path,
    "reverse-proxy.real-ip-header"
)

forward_ip_enabled = False

if forward_ip_header != '':
    forward_ip_enabled = True

def initialize_ip_banlist():
    """Initialize the ip banlist db and get a connection"""
    banned_ips_db = sqlite3.connect(
        os.path.join(
            "data",
            "ip_banlist.db"
        ),
        autocommit=True
    )

    banned_ips_db.execute('''
    CREATE TABLE IF NOT EXISTS banned_ip (
        ip TEXT PRIMARY KEY UNIQUE,
        reason TEXT
    )
    ''')

    return banned_ips_db

def get_real_ip(request: flask.Request) -> str:
    """Get the real ip adress taking into account reverse proxies and such"""
    
    if not forward_ip_enabled:
        return request.remote_addr
    
    if request.headers.get(forward_ip_header) is not None:
        return request.headers.get(forward_ip_header)
    else:
        logger.exception("'reverse-proxy.real-ip-header' exists but a request didnt provide such header. Returned the normal ip.")
        return request.remote_addr

def get_real_ip_no_params() -> str:
    """Get the real ip adress taking into account reverse proxies and such"""
    
    if not forward_ip_enabled:
        return request.remote_addr
    
    if request.headers.get(forward_ip_header) is not None:
        return request.headers.get(forward_ip_header)
    else:
        logger.exception("'reverse-proxy.real-ip-header' exists but a request didnt provide such header. Returned the normal ip.")
        return request.remote_addr

def ratelimit_breached(request_limit):
    """Callback to when a ratelimit gets breached and log it"""

    real_ip = get_real_ip(request)

    breach_logger.info(
        f"[{real_ip} RATELIMIT REACHED] - {request.full_path}"
    )

def ban_ip(ip:str,reason:str):
    """Ban an ip adress with a reason"""
    db = initialize_ip_banlist()
    try:
        db.execute("INSERT INTO banned_ip (ip,reason) VALUES (?,?)",(ip,reason))
        return 0
    except sqlite3.IntegrityError:
        return 1

def list_banned_ips():
    db = initialize_ip_banlist()
    return db.execute("SELECT * FROM banned_ip").fetchall()

def is_ip_banned(ip:str):
    db = initialize_ip_banlist()
    data = db.execute("SELECT * FROM banned_ip WHERE ip=?",(ip,)).fetchone()
    if data is None:
        return False
    
    return True

def ip_ban_details(ip:str):
    db = initialize_ip_banlist()
    data = db.execute("SELECT * FROM banned_ip WHERE ip=?",(ip,)).fetchone()

    return data

# idk how to test this