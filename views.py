from flask import Blueprint, render_template, request, jsonify
from tdiScanner import scan_code

views = Blueprint(__name__, "/")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("/scan", methods=["POST"])
def scan():
    data = request.get_json()
    source_code = data["source"]
    filename = data["filename"]

    scan_data = scan_code(source_code)

    return jsonify({
        "filename": filename,
        **scan_data
    })

@views.route("/scanResult")
def scanResults():
    return render_template("scanResult.html")

@views.route("/scanHistory")
def scan_history():
    return render_template("scanHistory.html")