from flask import Blueprint, render_template, request, jsonify
from complexityScanner import calculate_complexity

views = Blueprint(__name__, "/")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("scanHistory")
def scanHistory():
    return render_template("scanHistory.html")

@views.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    source_code = data["source"]
    filename = data["filename"]

    results = calculate_complexity(source_code)

    return jsonify({
        "filename": filename,
        "functions": results
    })

@views.route("/scanResult")
def scanResults():
    return render_template("scanResult.html")