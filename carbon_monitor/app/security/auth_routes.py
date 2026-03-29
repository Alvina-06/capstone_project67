# app/security/auth_routes.py

from flask import Blueprint, request, jsonify
from app.security.jwt_handler import create_token
from app.security.password_handler import (
    hash_password,
    verify_password
)
from app.database.db_operations import (
    save_user,
    get_user_by_email
)

auth_bp = Blueprint("auth", __name__)


# ─────────────────────────────────
# REGISTER
# ─────────────────────────────────

@auth_bp.route("/api/auth/register", methods=["POST"])
def register():

    data = request.get_json()

    name     = data.get("name")
    email    = data.get("email")
    password = data.get("password")
    role     = data.get("role", "user")

    # Check all fields present
    if not name or not email or not password:
        return jsonify({
            "error": "name, email and password are required"
        }), 400

    # Check if email already exists
    existing = get_user_by_email(email)
    if existing:
        return jsonify({
            "error": "Email already registered"
        }), 400

    # Hash password and save
    hashed = hash_password(password)
    save_user(name, email, hashed, role)

    return jsonify({
        "status":  "success",
        "message": f"User {name} registered successfully"
    }), 201


# ─────────────────────────────────
# LOGIN
# ─────────────────────────────────

@auth_bp.route("/api/auth/login", methods=["POST"])
def login():

    data = request.get_json()

    email    = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({
            "error": "email and password are required"
        }), 400

    # Find user
    user = get_user_by_email(email)
    if not user:
        return jsonify({
            "error": "User not found"
        }), 401

    # Verify password
    if not verify_password(password, user["password_hash"]):
        return jsonify({
            "error": "Wrong password"
        }), 401

    # Create token
    token = create_token(
        user_id = str(user["_id"]),
        email   = user["email"],
        role    = user["role"]
    )

    return jsonify({
        "status": "success",
        "token":  token,
        "name":   user["name"],
        "role":   user["role"]
    }), 200