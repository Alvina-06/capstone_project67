# app/security/jwt_handler.py

import jwt
import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))))
from config import SECRET_KEY, TOKEN_EXPIRY


def create_token(user_id, email, role):
    payload = {
        "user_id": str(user_id),
        "email":   email,
        "role":    role,
        "exp":     datetime.datetime.utcnow() +
                   datetime.timedelta(hours=TOKEN_EXPIRY)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token


def decode_token(token):
    decoded = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=["HS256"]
    )
    return decoded


# TEST
if __name__ == "__main__":
    print("Testing jwt_handler...")

    token = create_token("U001", "test@bmsit.in", "admin")
    print(f"Token created ✅")

    decoded = decode_token(token)
    print(f"Decoded ✅")
    print(f"user_id : {decoded['user_id']}")
    print(f"email   : {decoded['email']}")
    print(f"role    : {decoded['role']}")