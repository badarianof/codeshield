from flask import Blueprint, render_template

views = Blueprint(__name__, "/")

@views.route("/")
def home():
    return render_template("home.html")

@views.route("scanHistory")
def scanHistory():
    return render_template("scanHistory.html")

# @views.route("scanResults")
# def scanResults():
#     return render_template("scanResults.html")