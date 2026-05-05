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
    
    if len(source_code) > 100_000:
        return jsonify({"error": "file_too_large", "message": "File exceeds maximum size of 100KB."})

    try:
        scan_data = scan_code(source_code)
    except SyntaxError as e:
        return jsonify({
            "filename": filename,
            "error": "syntax_error",
            "message": f"Syntax error on line {e.lineno}: {e.msg}"
        })

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