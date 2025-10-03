
from flask import request
from flask import jsonify

from functools import wraps

import core.blueprints.api.user as user_utils

def authenticate(f = None):
    def inner(f):
        def e(*a, **ka):
            given_token = request.headers.get("X-Auth")

            if not user_utils.Token.is_valid_token(given_token):
                return jsonify({"error":"Invalid authorization"}),403
            
            return f(*a, **ka)
            
        return e
    return inner