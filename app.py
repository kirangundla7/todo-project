
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# Connect to MongoDB
mongo_uri = os.getenv("MONGODB_URI")

if not mongo_uri:
    raise RuntimeError("Please set MONGODB_URI in your .env file")

client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

# Select database and collection
db = client["todoDatabase"]
collection = db["todoItems"]


# Frontend page
@app.route("/")
def home():
    return render_template("index.html")


# Backend API
@app.route("/submittodoitem", methods=["POST"])
def submit_todo_item():
    try:
        data = request.get_json(silent=True) or {}

        item_name = data.get("itemName")
        item_description = data.get("itemDescription")

        # Validate input
        if (
            not isinstance(item_name, str)
            or not isinstance(item_description, str)
            or not item_name.strip()
            or not item_description.strip()
        ):
            return jsonify({
                "message": "Item name and description are required."
            }), 400

        # Store item in MongoDB
        todo_item = {
            "itemName": item_name.strip(),
            "itemDescription": item_description.strip()
        }

        result = collection.insert_one(todo_item)

        return jsonify({
            "message": "To-Do item saved successfully!",
            "id": str(result.inserted_id)
        }), 201

    except Exception:
        app.logger.exception("Failed to save To-Do item")
        return jsonify({
            "message": "Failed to save To-Do item. Check the server logs."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
