from flask import Flask,flash, render_template, request, redirect, url_for
from datetime import date
from flask_mysqldb import MySQL


app = Flask(__name__)
app.config['SECRET_KEY'] = 'pokemon pokemon'

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
                resultValue4 = cur.execute("SELECT Order_ID FROM Orders ORDER BY Order_ID DESC LIMIT 1;")
                lastentry = cur.fetchall()
                lastid = int(lastentry[0][0])+1
                today = date.today()
                d1 = today.strftime("%Y/%m/%d")
                #query = """INSERT INTO Orders (User_ID,Order_ID,Price,Date,DeliveryP_ID,Delivered_status) VALUES ('%s','%s','%s','%s','%s','%s');"""
                cur.execute("""INSERT INTO Orders (User_ID,Order_ID,Price,Date,DeliveryP_ID,Delivered_status) VALUES (%s,%s,%s,%s,%s,%s)""",(id,lastid,0,d1,random.randrange(1, 100),2))
                mysql.connection.commit()
                cost=0
                for i in range(len(input)):
                    resultValue = cur.execute("SELECT Cost FROM Dish WHERE Dish_ID = %s", (input[i],))
                    price = cur.fetchall()
                    cost += int(price[0][0])
                    cur.execute("""INSERT INTO contains (Dish_ID,Order_ID) VALUES (%s,%s)""",(input[i],lastid))
                    mysql.connection.commit()

                cur.execute("""UPDATE Orders SET Price = %s WHERE Order_ID = %s""",(cost,lastid))
                mysql.connection.commit()
                cur.close()
            return redirect(url_for('customer'))

        if request.form['submit_button'] == 'Back':
            #cur.execute("""DELETE FROM Orders WHERE Order_ID = %s""",(lastid,))
            return redirect(url_for('customer'))
    return render_template('PlaceOrder.html', Dishdetails=Dishdetails)



@app.route('/customer', methods=['GET', 'POST'])
def customer():
    cur = mysql.connection.cursor()
    id=1
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


@app.route('/Order_confirm/<string:id>',methods=['GET', 'POST'])
def Order_confirm(id):
    cur = mysql.connection.cursor()
    cur.execute("select * from contains where Order_ID = %s",(id,))
    Dishes = cur.fetchall()

    flag=0
    for i in range(len(Dishes)): #dishid
        cur.execute("select Dish_ID, ingredient_ID,Amount from ingredient_list where Dish_ID = %s",(Dishes[i][0],))
        Ingredients = cur.fetchall()
        for j in range(len(Ingredients)): #ingredients
            cur.execute("""select Ingredient_ID, Quantity_stored, Warehouse_ID from Warehouse natural join Delivery_person where DeliveryP_ID = 1 and Ingredient_ID = %s""",(Ingredients[j][1],))
            temp2 = cur.fetchall()
            a = int(temp2[0][1]) - int(Ingredients[j][2])
            if(a<0):
                flag=1
                break

    if(flag==0):

        for i in range(len(Dishes)): #dishid
            cur.execute("select Dish_ID, ingredient_ID,Amount from ingredient_list where Dish_ID = %s",(Dishes[i][0],))
            Ingredients = cur.fetchall()
            for j in range(len(Ingredients)): #ingredients
                cur.execute("""select Ingredient_ID, Quantity_stored, Warehouse_ID from Warehouse natural join Delivery_person where DeliveryP_ID = 1 and Ingredient_ID = %s""",(Ingredients[j][1],))
                temp2 = cur.fetchall()
                a = int(temp2[0][1]) - int(Ingredients[j][2])
                c = temp2[0][2]
                b = Ingredients[j][1]
                print(Dishes[i][0],Ingredients[j][1])
                cur.execute("""UPDATE Warehouse SET Quantity_stored = %s WHERE Warehouse_ID = %s and  Ingredient_ID = %s""",(a,c,b))
                mysql.connection.commit()

        cur.execute("""UPDATE Orders SET delivered_status = 2 WHERE Order_ID = %s """,(id,))
        mysql.connection.commit()
        flash("Order Delivered!","success")
    else:
        
        cur.execute("""UPDATE Orders SET delivered_status = 3 WHERE Order_ID = %s """,(id,))
        mysql.connection.commit()
        flash("Order Canceled!","danger")
        # return redirect(url_for('delivery_edit'))

    cur.close()
    return redirect(url_for('delivery_edit'))


@app.route('/delivery_edit',methods=['GET', 'POST'])
def delivery_edit():
    cur = mysql.connection.cursor()
    resultValue1 = cur.execute("select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = 10 and delivered_status = 1) as t1 join Customer t2 on t1.user_id = t2.user_id;")
    userDetails1 = cur.fetchall()


    resultValue2 = cur.execute("select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = 10 and delivered_status = 2) as t1 join Customer t2 on t1.user_id = t2.user_id;")
    userDetails2 = cur.fetchall()

    if request.method == 'POST':
        if request.form['submit_button'] == 'Deliver':
            input = request.form
            id = input['id']
            cur.close()
            return redirect(url_for('Order_confirm', id=id))
        else:
            return redirect(url_for('delivery'))
    return render_template('Delivery_person_edit.html',userDetails1=userDetails1,userDetails2=userDetails2)


@app.route('/delivery',methods=['GET', 'POST'])
def delivery():
    cur = mysql.connection.cursor()
    resultValue1 = cur.execute("select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = 10 and delivered_status = 1) as t1 join Customer t2 on t1.user_id = t2.user_id;")
    userDetails1 = cur.fetchall()

    resultValue2 = cur.execute("select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = 10 and delivered_status = 2) as t1 join Customer t2 on t1.user_id = t2.user_id;")
    userDetails2 = cur.fetchall()

    if request.method == 'POST':
        return redirect(url_for('delivery_edit'))
    return render_template('Delivery_person.html',userDetails1=userDetails1,userDetails2=userDetails2)


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


