from flask import Flask, render_template, request, redirect, url_for
from datetime import date
from flask_mysqldb import MySQL
import yaml, random

def create_app():
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'fitcook.cwx1jntgf3ei.us-east-2.rds.amazonaws.com'
    app.config['MYSQL_USER'] = 'admin'
    app.config['MYSQL_PASSWORD'] = 'fitcook123'
    app.config['MYSQL_DB'] = 'fitcook'

    mysql = MySQL(app)

    
    @app.route('/User_profile')
    def User_profile():
        cur = mysql.connection.cursor()
        resultValue = cur.execute("Select * FROM Dish")
        if(resultValue>0):
            userDetails = cur.fetchall()
            return render_template("user_profile.html", userDetails=userDetails) 
        return render_template("user_profile.html") 

    @app.route('/publicity')
    def Publicity():
        id=1
        cur = mysql.connection.cursor()
        resultValue1 = cur.execute("SELECT * FROM Customer WHERE USER_ID = %s", (id,))
        Userdetails = cur.fetchall()
        #print("hi",len(Orderdetails))

        resultValue2 = cur.execute("Select Dish_ID, Name, Cost, Rating FROM Dish")
        DishDetails = cur.fetchall()

        DishDetails = sorted(DishDetails, key=lambda x: -x[2])

        if(resultValue1>0):
            return render_template("publicity.html", Userdetails=Userdetails, DishDetails=DishDetails) 
        return render_template("publicity.html", Userdetails=Userdetails, DishDetails=DishDetails) 
            
    
    @app.route('/login')
    def login():
        return render_template("login.html")

    @app.route('/logout')
    def logout():
        return "<h2>Log Out</h2>"


    @app.route('/signup')
    def signup():
        return render_template("signup.html")

    @app.route('/user_profile')
    def user_profile():
        return render_template("user_profile.html")

    return app