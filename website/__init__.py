from flask import Flask, render_template, request, redirect, url_for, flash, session
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

    @app.route('/publicityBest')
    def Publicity_best():
        id=1
        cur = mysql.connection.cursor()
        resultValue1 = cur.execute("SELECT * FROM Customer WHERE USER_ID = %s", (id,))
        Userdetails = cur.fetchall()
        #print("hi",len(Orderdetails))

        resultValue2 = cur.execute("Select Dish_ID, Name, Cost, Rating FROM Dish")
        DishDetails = cur.fetchall()

        resultValue3 = cur.execute("Select Dish_ID, Name, Rating FROM Dish WHERE Rating =(SELECT MAX(Rating) FROM Dish)")
        BestDishDetails = cur.fetchall()

        resultValue4 = cur.execute("Select Dish_ID, Name, Rating FROM Dish WHERE Rating =(SELECT MIN(Rating) FROM Dish)")
        WorstDishDetails = cur.fetchall()

        DishDetails = sorted(DishDetails, key=lambda x: -x[3])

        print(BestDishDetails)

        if(resultValue1>0):
            return render_template("bestpublicity.html", Userdetails=Userdetails, DishDetails=DishDetails, BestDishDetails=BestDishDetails, WorstDishDetails=WorstDishDetails) 
        return render_template("bestpublicity.html", Userdetails=Userdetails, DishDetails=DishDetails, BestDishDetails=BestDishDetails, WorstDishDetails=WorstDishDetails) 
            
    
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



    @app.route('/user_profile')
    def user_profile():
        return render_template("user_profile.html")

    return app