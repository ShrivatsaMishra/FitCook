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

        resultValue2 = cur.execute("Select Dish_ID, Name, Price, Rating FROM Dish")
        DishSDetails = cur.fetchall()

        if(resultValue1>0):
            return render_template("publicity.html", userDetails=Userdetails, dishSDetails=DishSDetails) 
        return render_template("publicity.html", userDetails=Userdetails, dishSDetails=DishSDetails) 
         


    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    return app