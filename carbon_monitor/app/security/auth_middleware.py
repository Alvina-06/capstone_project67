# app/security/auth_middleware.py

from flask import request, jsonify
from app.security.jwt_handler import decode_token
from functools import wraps


def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        # Step 1: Check header exists
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "error": "No token provided. Please login."
            }), 401

        # Step 2: Extract token
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({
                "error": "Invalid token format. "
                         "Use: Bearer <token>"
            }), 401

        # Step 3: Verify + Decode
        try:
            decoded = decode_token(token)
        except Exception:
            return jsonify({
                "error": "Invalid or expired token. "
                         "Please login again."
            }), 401

        # Step 4: Attach user to request
        request.user = decoded

        # Route function runs now
        return f(*args, **kwargs)

    return wrapper