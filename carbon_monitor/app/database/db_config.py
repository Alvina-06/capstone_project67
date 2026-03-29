# app/database/db_config.py

from pymongo import MongoClient

# Paste your connection string here
MONGO_URI = "mongodb+srv://carbon_admin:capstone67carbon@cluster0.rfidcmu.mongodb.net/?appName=Cluster0"

# Connect to MongoDB
client = MongoClient(MONGO_URI)

# Your database
db = client["carbon_db"]

# All collections (like tables in SQL)
sensor_readings    = db["sensor_readings"]
carbon_predictions = db["carbon_predictions"]
anomalies          = db["anomalies"]
recommendations    = db["recommendations"]
users              = db["users"]


# TEST CONNECTION
if __name__ == "__main__":
    try:
        client.server_info()
        print("MongoDB connected ✅")
        print("Collections ready:")
        print("  → sensor_readings")
        print("  → carbon_predictions")
        print("  → anomalies")
        print("  → recommendations")
        print("  → users")
    except Exception as e:
        print("Connection failed ❌")
        print("Error:", e)