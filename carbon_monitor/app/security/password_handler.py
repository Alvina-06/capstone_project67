# app/security/password_handler.py

import bcrypt


def hash_password(plain_password):
    salt   = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode(), salt)
    return hashed.decode()


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(
        plain_password.encode(),
        hashed_password.encode()
    )


# TEST
if __name__ == "__main__":
    print("Testing password_handler...")

    hashed = hash_password("mypassword123")
    print(f"Hashed ✅ : {hashed[:30]}...")

    result = verify_password("mypassword123", hashed)
    print(f"Correct password ✅ : {result}")

    result = verify_password("wrongpassword", hashed)
    print(f"Wrong password ✅   : {result}")