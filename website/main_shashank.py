from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import date
from flask_mysqldb import MySQL
import random


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'fitcook.cwx1jntgf3ei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'fitcook123'
app.config['MYSQL_DB'] = 'fitcook'
app.config['SECRET_KEY'] = 'pokemon pokemon'

mysql = MySQL(app)


@app.route('/Place_Order/<string:id>', methods=['GET', 'POST'])
def Place_Order(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Dish")
    Dishdetails = cur.fetchall()

    if request.method == 'POST':
        if request.form['submit_button'] == 'Order Now':
            input = request.form.getlist('mycheckbox')
            # id = input['id']
            if len(input) > 0:
                # print(input)
                cost = 0
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

                cur.execute("""UPDATE Customer SET Wallet = %s WHERE User_ID = %s""", (walletint - cost, id))

                resultValue4 = cur.execute("SELECT Order_ID FROM Orders ORDER BY Order_ID DESC LIMIT 1;")
                lastentry = cur.fetchall()
                lastid = int(lastentry[0][0]) + 1
                today = date.today()
                d1 = today.strftime("%Y/%m/%d")

                cur.execute(
                    """INSERT INTO Orders (User_ID,Order_ID,Price,Date,DeliveryP_ID,Delivered_status) VALUES (%s,%s,%s,%s,%s,%s)""",
                    (id, lastid, cost, d1, random.randrange(1, 100), 2))
                mysql.connection.commit()

                for i in range(len(input)):
                    resultValue = cur.execute("SELECT Cost FROM Dish WHERE Dish_ID = %s", (input[i],))
                    price = cur.fetchall()
                    cost += int(price[0][0])
                    cur.execute("""INSERT INTO contains (Dish_ID,Order_ID) VALUES (%s,%s)""", (input[i], lastid))
                    mysql.connection.commit()

                # cur.execute("""UPDATE Orders SET Price = %s WHERE Order_ID = %s""",(cost,lastid))
                # mysql.connection.commit()
                cur.close()
            flash("Your order is has been placed, its on the way!!!", "success")
            return redirect(url_for('customer'))

        if request.form['submit_button'] == 'Back':
            # cur.execute("""DELETE FROM Orders WHERE Order_ID = %s""",(lastid,))
            return redirect(url_for('customer'))
    return render_template('PlaceOrder.html', Dishdetails=Dishdetails)

@app.route('/customer', methods=['GET', 'POST'])
def customer():
    cur = mysql.connection.cursor()
    id = session['ID']
    resultValue1 = cur.execute("SELECT * FROM Customer WHERE USER_ID = %s", (id,))
    Userdetails = cur.fetchall()

    resultValue2 = cur.execute(
        "SELECT Order_ID, COUNT(*), Price, Date FROM (SELECT * FROM Orders WHERE User_ID = %s AND Delivered_status= '1') as T NATURAL JOIN contains GROUP BY Order_ID",
        (id,))
    Orderdetails = cur.fetchall()
    # print("hi",len(Orderdetails))

    resultValue3 = cur.execute(
        "SELECT Order_ID, COUNT(*), Price, Date FROM (SELECT * FROM Orders WHERE User_ID = %s AND Delivered_status= '2') as T NATURAL JOIN contains GROUP BY Order_ID",
        (id,))
    Orderonwaydetails = cur.fetchall()

    if resultValue1 > 0:
        if request.method == 'POST':
            return redirect(url_for('Place_Order', id=id))
    return render_template("user_profile.html", Userdetails=Userdetails, Orderdetails=Orderdetails,
                           Orderonwaydetails=Orderonwaydetails)


@app.route('/Order_confirm/<string:id>', methods=['GET', 'POST'])
def Order_confirm(id):
    cur = mysql.connection.cursor()
    ID = session['ID']
    cur.execute("select * from contains where Order_ID = %s", (id,))
    Dishes = cur.fetchall()

    flag = 0
    for i in range(len(Dishes)):  # dishid
        cur.execute("select Dish_ID, ingredient_ID,Amount from ingredient_list where Dish_ID = %s", (Dishes[i][0],))
        Ingredients = cur.fetchall()
        for j in range(len(Ingredients)):  # ingredients
            cur.execute(
                """select Ingredient_ID, Quantity_stored, Warehouse_ID from Warehouse natural join Delivery_person where DeliveryP_ID = %s and Ingredient_ID = %s""",
                (ID, Ingredients[j][1]))
            temp2 = cur.fetchall()
            a = int(temp2[0][1]) - int(Ingredients[j][2])
            if (a < 0):
                flag = 1
                break

    if (flag == 0):

        for i in range(len(Dishes)):  # dishid
            cur.execute("select Dish_ID, ingredient_ID,Amount from ingredient_list where Dish_ID = %s", (Dishes[i][0],))
            Ingredients = cur.fetchall()
            for j in range(len(Ingredients)):  # ingredients
                cur.execute(
                    """select Ingredient_ID, Quantity_stored, Warehouse_ID from Warehouse natural join Delivery_person where DeliveryP_ID = 1 and Ingredient_ID = %s""",
                    (Ingredients[j][1],))
                temp2 = cur.fetchall()
                a = int(temp2[0][1]) - int(Ingredients[j][2])
                c = temp2[0][2]
                b = Ingredients[j][1]
                print(Dishes[i][0], Ingredients[j][1])
                cur.execute(
                    """UPDATE Warehouse SET Quantity_stored = %s WHERE Warehouse_ID = %s and  Ingredient_ID = %s""",
                    (a, c, b))
                mysql.connection.commit()

        cur.execute("""UPDATE Orders SET delivered_status = 1 WHERE Order_ID = %s """, (id,))
        mysql.connection.commit()
        flash("Order Delivered!", "success")
    else:

        cur.execute("""UPDATE Orders SET delivered_status = 3 WHERE Order_ID = %s """, (id,))
        mysql.connection.commit()
        flash("Order Canceled! Insufficient Ingredients.", "danger")

    cur.close()
    return redirect(url_for('delivery_edit'))


@app.route('/delivery_edit', methods=['GET', 'POST'])
def delivery_edit():
    cur = mysql.connection.cursor()
    ID = session['ID']
    resultValue1 = cur.execute(
        "select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = %s and delivered_status = 2) as t1 join Customer t2 on t1.user_id = t2.user_id;",(ID,))
    userDetails1 = cur.fetchall()

    resultValue2 = cur.execute(
        "select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = %s and delivered_status = 1) as t1 join Customer t2 on t1.user_id = t2.user_id;",(ID,))
    userDetails2 = cur.fetchall()

    if request.method == 'POST':
        if request.form['submit_button'] == 'Deliver':
            input = request.form
            id = input['id']
            cur.close()
            return redirect(url_for('Order_confirm', id=id))
        else:
            return redirect(url_for('delivery'))
    return render_template('Delivery_person_edit.html', userDetails1=userDetails1, userDetails2=userDetails2)


@app.route('/delivery', methods=['GET', 'POST'])
def delivery():
    cur = mysql.connection.cursor()
    ID = session['ID']
    resultValue1 = cur.execute(
        "select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = %s and delivered_status = 2) as t1 join Customer t2 on t1.user_id = t2.user_id;",(ID,))
    userDetails1 = cur.fetchall()

    resultValue2 = cur.execute(
        "select t2.User_ID,  t2.Name, t1.Order_ID, t2.Address from (select User_ID, Order_ID from Orders natural join Delivery_person where deliveryP_Id = %s and delivered_status = 1) as t1 join Customer t2 on t1.user_id = t2.user_id;",(ID,))
    userDetails2 = cur.fetchall()

    if request.method == 'POST':
        return redirect(url_for('delivery_edit'))
    return render_template('Delivery_person.html', userDetails1=userDetails1, userDetails2=userDetails2)

@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        #fetch form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO login(name, email) VALUES(%s, %s)", (name, email))
        mysql.connection.commit()
        cur.close()
        return 'success'
    return render_template('index.html')


@app.route('/Dish')
def dish():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM Dish")

    if resultValue > 0:
        dishDetails = cur.fetchall()
        return render_template('dish.html', dishDetails=dishDetails)



@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Login':
            cursor = mysql.connection.cursor()
            type = request.form.get('type')
            if type == 'Customer':
                email = request.form.get('email')
                cursor.execute("select User_ID from Customer where email = %s", (email,))
                User_ID = cursor.fetchone()[0]
                cursor.execute("select password from Customer where email = %s", (email,))
                realPassword = cursor.fetchone()[0]
                password = request.form.get('password')
                if password != realPassword:
                    flash("Password does not match", "danger")
                    return redirect(request.url)
                else:
                    session['ID'] = User_ID
                    return redirect(url_for('customer'))
            elif type == 'Dietician':
                email = request.form.get('email')
                cursor.execute("select Dietician_ID from Dietician where email = %s", (email,))
                User_ID = cursor.fetchone()[0]
                cursor.execute("select password from Dietician where email = %s", (email,))
                realPassword = cursor.fetchone()[0]
                password = request.form.get('password')
                if password != realPassword:
                    flash("Password does not match", "danger")
                    return redirect(request.url)
                else:
                    session['ID'] = User_ID
                    return redirect(url_for('customer')) #CHANGE
            elif type == 'Manager':
                email = request.form.get('email')
                cursor.execute("select Manager_ID from Manager where email = %s", (email,))
                User_ID = cursor.fetchone()[0]
                cursor.execute("select password from Manager where email = %s", (email,))
                realPassword = cursor.fetchone()[0]
                password = request.form.get('password')
                if password != realPassword:
                    flash("Password does not match", "danger")
                    return redirect(request.url)
                else:
                    session['ID'] = User_ID
                    return redirect(url_for('customer')) #CHANGE
            elif type == 'DeliveryPerson':
                email = request.form.get('email')
                cursor.execute("select DeliveryP_ID from Delivery_person where email = %s", (email,))
                User_ID = cursor.fetchone()[0]
                cursor.execute("select password from Delivery_person where email = %s", (email,))
                realPassword = cursor.fetchone()[0]
                password = request.form.get('password')
                if password != realPassword:
                    flash("Password does not match", "danger")
                    return redirect(request.url)
                else:
                    session['ID'] = User_ID
                    return redirect(url_for('delivery'))
            elif type == 'PR':
                email = request.form.get('email')
                cursor.execute("select PR_ID from PR where email = %s", (email,))
                User_ID = cursor.fetchone()[0]
                cursor.execute("select password from PR where email = %s", (email,))
                realPassword = cursor.fetchone()[0]
                password = request.form.get('password')
                if password != realPassword:
                    flash("Password does not match", "danger")
                    return redirect(request.url)
                else:
                    session['ID'] = User_ID
                    return redirect(url_for('customer')) #CHANGE

    return render_template("login.html")

@app.route('/logout')
def logout():
    return "<h2>Log Out</h2>"


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/customer_signup', methods=['POST','GET'])
def customer_signup():
    if request.method == 'POST':
        if request.form['submit_button'] == 'Register':
            cursor = mysql.connection.cursor()
            Name = request.form.get('name')
            password = request.form.get('password')
            email = request.form.get('email')
            age = int(request.form.get('age'))
            gender = request.form.get('gender')
            homeAddress = request.form.get('homeAddress')
            phone = request.form.get('phone')
            height = int(request.form.get('height'))
            weight = int(request.form.get('weight'))
            password = request.form.get('password')
            password2 = request.form.get('password2')
            Wallet = 0
            cursor.execute('SELECT User_ID FROM Customer')
            rows = cursor.rowcount
            User_ID = str(rows + 1)
            if password != password2:
                flash("Password does not match", "danger")
                return redirect(request.url)
            BMI = weight/(height*height)
            TDEE = (10*weight) + (6.25*height) - (5*age)
            if gender == "Male":
                TDEE = TDEE + 5
            else:
                TDEE = TDEE - 161
            cursor.execute('SELECT Warehouse_ID FROM Warehouse_List')
            rows = cursor.rowcount
            alloted_Warehouse_ID = random.randint(1,rows)
            cursor.execute('SELECT Dietician_ID FROM Dietician')
            rows = cursor.rowcount
            Dietician_ID = random.randint(1,rows)

            sql_formula = "INSERT INTO Customer(User_ID,email,password,Name,Age,Address,Mobile,Height,Weight,BMI, Wallet,TDEE, alloted_Warehouse_ID, Dietician_ID) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            user = (User_ID, email, password, Name, age, homeAddress, phone, height, weight, BMI, Wallet, TDEE, alloted_Warehouse_ID, Dietician_ID)
            cursor.execute(sql_formula, user)
            mysql.connection.commit()
            cursor.close()
            #print(Name, password, Username, Income, Locality, District, Zip)

            return redirect(url_for('login'))

    return render_template("customer_signup.html")

@app.route('/manager_signup', methods=['POST','GET'])
def manager_signup():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        Name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        cursor.execute('SELECT Manager_ID FROM Manager')
        rows = cursor.rowcount
        Manager_ID = str(rows + 1)
        if password != password2:
            flash("Password does not match", "danger")
            return redirect(request.url)

        sql_formula = "INSERT INTO Manager(Manager_ID,email,password,Name) VALUES(%s,%s,%s,%s)"
        user = (Manager_ID, email, password, Name)
        cursor.execute(sql_formula, user)
        mysql.connection.commit()
        cursor.close()
        # print(Name, password, Username, Income, Locality, District, Zip)
        return redirect(url_for('login'))

    return render_template("manager_signup.html")


@app.route('/deliveryperson_signup', methods=['POST','GET'])
def deliveryperson_signup():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        Name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        cursor.execute('SELECT DeliveryP_ID FROM Delivery_person')
        rows = cursor.rowcount
        DeliveryP_ID = str(rows + 1)
        if password != password2:
            flash("Password does not match", "danger")
            return redirect(request.url)
        cursor.execute('SELECT Warehouse_ID FROM Warehouse_List')
        rows = cursor.rowcount
        Warehouse_ID = random.randint(1, rows)
        sql_formula = "INSERT INTO Delivery_person(DeliveryP_ID,email,password,Name, Warehouse_ID) VALUES(%s,%s,%s,%s, %s)"
        user = (DeliveryP_ID, email, password, Name, Warehouse_ID)
        cursor.execute(sql_formula, user)
        mysql.connection.commit()
        cursor.close()
        # print(Name, password, Username, Income, Locality, District, Zip)
        return redirect(url_for('login'))

    return render_template("deliveryperson_signup.html")

@app.route('/chef_signup', methods=['POST','GET'])
def chef_signup():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        Name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        cursor.execute('SELECT Dietician_ID FROM Dietician')
        rows = cursor.rowcount
        Dietician_ID = str(rows + 1)
        if password != password2:
            flash("Password does not match", "danger")
            return redirect(request.url)
        qualification = request.form.get('qualification')
        experience = request.form.get('experience')
        phone = request.form.get('phone')
        sql_formula = "INSERT INTO Dietician(Dietician_ID,email,password,Name, Dietician_Qualification,Dietician_Experience, Dietician_Contact) VALUES(%s,%s,%s,%s, %s,%s,%s,%s)"
        user = (Dietician_ID, email, password, Name, qualification,experience,phone)
        cursor.execute(sql_formula, user)
        mysql.connection.commit()
        cursor.close()
        # print(Name, password, Username, Income, Locality, District, Zip)
        return redirect(url_for('login'))

    return render_template("chef_signup.html")

@app.route('/publicity_signup', methods=['POST','GET'])
def publicity_signup():
    if request.method == 'POST':
        cursor = mysql.connection.cursor()
        Name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password2 = request.form.get('password2')
        cursor.execute('SELECT PR_ID FROM PR')
        rows = cursor.rowcount
        PR_ID = str(rows + 1)
        if password != password2:
            flash("Password does not match", "danger")
            return redirect(request.url)
        phone = request.form.get('phone')
        sql_formula = "INSERT INTO Dietician(Dietician_ID,email,password,Name,Mobile) VALUES(%s,%s,%s,%s, %s,%s,%s,%s)"
        user = (PR_ID, email, password, Name, phone)
        cursor.execute(sql_formula, user)
        mysql.connection.commit()
        cursor.close()
        # print(Name, password, Username, Income, Locality, District, Zip)
        return redirect(url_for('login'))
    return render_template("publicity_signup.html")


if __name__ == '__main__':
    app.run(debug=True)