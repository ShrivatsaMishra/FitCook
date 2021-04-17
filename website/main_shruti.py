from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
from flask_mysqldb import MySQL
import yaml, random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokemon pokemon'
#db = yaml.load(open('db.yaml'))
#app.config['MYSQL_HOST'] = db['mysql_host']
#app.config['MYSQL_USER'] = db['mysql_user']
#app.config['MYSQL_PASSWORD'] = db['mysql_password']
#app.config['MYSQL_DB'] = db['mysql_db']

app.config['MYSQL_HOST'] = 'fitcook.cwx1jntgf3ei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'fitcook123'
app.config['MYSQL_DB'] = 'fitcook'

mysql = MySQL(app)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/Place_Order/<string:id>',methods=['GET', 'POST'])
def Place_Order(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Dish")
    Dishdetails = cur.fetchall()

    if request.method == 'POST':
        if request.form['submit_button'] == 'Order Now':
            input = request.form.getlist('mycheckbox')
                #id = input['id']
            if len(input)>0:
                #print(input)
                cost=0
                for i in range(len(input)):
                    selected = cur.execute("SELECT Cost FROM Dish WHERE Dish_ID = %s", (input[i],))
                    price = cur.fetchall()
                    cost += int(price[0][0])
                
                selected2 = cur.execute("SELECT Wallet FROM Customer WHERE User_ID = %s", (id,))
                wallet = cur.fetchall()
                walletint = int(wallet[0][0])
                if walletint < cost:
                    flash("You don't have enough money in your wallet", "danger")
                    return redirect(request.url)

                cur.execute("""UPDATE Customer SET Wallet = %s WHERE User_ID = %s""",(walletint-cost,id))

                resultValue4 = cur.execute("SELECT Order_ID FROM Orders ORDER BY Order_ID DESC LIMIT 1;")
                lastentry = cur.fetchall()
                lastid = int(lastentry[0][0])+1
                today = date.today()
                d1 = today.strftime("%Y/%m/%d")
                
                cur.execute("""INSERT INTO Orders (User_ID,Order_ID,Price,Date,DeliveryP_ID,Delivered_status) VALUES (%s,%s,%s,%s,%s,%s)""",(id,lastid,cost,d1,random.randrange(1, 100),2))
                mysql.connection.commit()

                for i in range(len(input)):
                    resultValue = cur.execute("SELECT Cost FROM Dish WHERE Dish_ID = %s", (input[i],))
                    price = cur.fetchall()
                    cost += int(price[0][0])
                    cur.execute("""INSERT INTO contains (Dish_ID,Order_ID) VALUES (%s,%s)""",(input[i],lastid))
                    mysql.connection.commit()

                #cur.execute("""UPDATE Orders SET Price = %s WHERE Order_ID = %s""",(cost,lastid))
                #mysql.connection.commit()
                cur.close()
            flash("Your order is has been placed, its on the way!!!", "success")
            return redirect(url_for('customer'))

        if request.form['submit_button'] == 'Back':
            #cur.execute("""DELETE FROM Orders WHERE Order_ID = %s""",(lastid,))
            return redirect(url_for('customer'))
    return render_template('PlaceOrder.html', Dishdetails=Dishdetails)



@app.route('/customer', methods=['GET', 'POST'])
def customer():
    cur = mysql.connection.cursor()
    id= 23
    resultValue1 = cur.execute("SELECT * FROM Customer WHERE USER_ID = %s", (id,))
    Userdetails = cur.fetchall()

    resultValue2 = cur.execute("SELECT Order_ID, COUNT(*), Price, Date FROM (SELECT * FROM Orders WHERE User_ID = %s AND Delivered_status= '1') as T NATURAL JOIN contains GROUP BY Order_ID", (id,))
    Orderdetails = cur.fetchall()
    #print("hi",len(Orderdetails))

    resultValue3 = cur.execute("SELECT Order_ID, COUNT(*), Price, Date FROM (SELECT * FROM Orders WHERE User_ID = %s AND Delivered_status= '2') as T NATURAL JOIN contains GROUP BY Order_ID", (id,))
    Orderonwaydetails = cur.fetchall()

    if resultValue1 > 0:
        if request.method == 'POST':
            return redirect(url_for('Place_Order', id=id))
    return render_template("user_profile.html", Userdetails=Userdetails, Orderdetails=Orderdetails, Orderonwaydetails=Orderonwaydetails)


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


if __name__ == '__main__':
    app.run(debug=True)


