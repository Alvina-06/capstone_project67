# run.py

from flask import Flask
from app.routes.sensor_routes import sensor_bp
from app.security.auth_routes import auth_bp

app = Flask(__name__)

# Register all blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(sensor_bp)

@app.route("/")
def home():
    return {"message": "Carbon Monitor API is running ✅"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)