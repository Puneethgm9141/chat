from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["student"]
collection = db["collection"]

@app.route("/check_rank", methods=["POST"])
def check_rank():
    rank = request.json.get("rank")
    exam_type = request.json.get("exam_type")

    if not rank or not exam_type:
        return jsonify({"message": "Please provide a valid rank and exam type (CET or COMEDK)."}), 400

    # Determine the appropriate fields based on the exam type
    if exam_type.lower() == "cet":
        min_rank_field, max_rank_field = "cet rank", "cet rankl"
    elif exam_type.lower() == "comedk":
        min_rank_field, max_rank_field = "cometk rank", "cometk rankl"
    else:
        return jsonify({"message": "Invalid exam type provided."}), 400

    # Query MongoDB based on the rank range and exam type
    colleges = list(collection.find({
        min_rank_field: {"$lte": rank},
        max_rank_field: {"$gte": rank}
    }))

    college_list = []
    for college in colleges:
        college_list.append({
            "clgname": college["clgname"],
            "department": college["department"],
            "cet_rank_range": f"{college.get('cet rank')} - {college.get('cet rankl')}",
            "cometk_rank_range": f"{college.get('cometk rank')} - {college.get('cometk rankl')}"
        })

    if college_list:
        return jsonify({"colleges": college_list})
    else:
        return jsonify({"message": "Oops, sorry! No college matches the provided rank and exam type."})

@app.route("/college_details", methods=["POST"])
def college_details_route():
    college_name = request.json.get("college_name")

    if not college_name:
        return jsonify({"message": "Please provide a college name."}), 400

    # Search for the college in MongoDB, allowing partial and case-insensitive matches
    college = collection.find_one({"clgname": {"$regex": college_name, "$options": "i"}})

    if college:
        # Format and return the college details
        details = {
            "clgname": college["clgname"],
            "address": college.get("address", "Address not available"),
            "courses": college.get("courses", "").split(",")  # Assuming courses are stored as a comma-separated string
        }
        return jsonify(details)
    else:
        return jsonify({"message": "Oops, sorry! No details found for the specified college."})

if __name__ == "__main__":
    app.run(debug=True)
