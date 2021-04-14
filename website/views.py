from flask import Blueprint, render_template

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/User_profile')
def User_profile():
    return render_template("user_profile.html")
