from flask import Flask, render_template,request,url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'fitcook.cwx1jntgf3ei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'fitcook123'
app.config['MYSQL_DB'] = 'fitcook'

mysql = MySQL(app)


@app.route('/Dish_edit/<string:id>',methods=['GET', 'POST'])
def Dish_edit(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM fitcook.Dish WHERE Dish_ID = %s",(id,))
    if resultValue > 0:
        Dishdetails = cur.fetchall()
        if request.method == 'POST':
            if request.form['submit_button'] == 'Update':
                input = request.form
                attribute = input['attribute']
                updated_value = input['updated_attribute']
                print(attribute)
                print(updated_value)
                cur.execute("UPDATE fitcook.Dish SET %s = '%s' WHERE Dish_ID = %s"%(attribute,updated_value,id))

                resultValue1 = cur.execute("SELECT * FROM fitcook.Dish WHERE Dish_ID = %s",(id,))
                Dishdetails = cur.fetchall()

                mysql.connection.commit()
                cur.close()

        return render_template('Dietician_Dish_EDIT.html', Dishdetails= Dishdetails)



@app.route('/NewDish/<string:Dietician_ID>',methods=['GET', 'POST'])
def newDish(Dietician_ID):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM fitcook.Dish")
    Dishdetails = cur.fetchall()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Insert New Dish !':
            input = request.form
            Name = input['Name']
            Cost = input['Cost']
            Category = input['Category']
            Calories = input['Calories']
            Rating = input['Rating']
            Fats = input['Fats']
            Carbs = input['Carbs']
            Protein = input['Protein']
            Recipe = input['Recipe']
            resultValue2 = cur.execute("SELECT Dish_ID FROM fitcook.Dish ORDER BY Dish_ID DESC LIMIT 1;")
            lastentry = cur.fetchall()
            lastid = int(lastentry[0][0])+1
            cur.execute("""INSERT INTO fitcook.Dish (Dish_ID,Name,Cost,Category,Calories,Rating,Fats,Carbs,Protein,Recipe) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(lastid,Name,Cost,Category,Calories,Rating,Fats,Carbs,Protein,Recipe))
            cur.execute("""INSERT INTO fitcook.assesses(Dish_ID,Dietician_ID) VALUES (%s,%s)""",(lastid,Dietician_ID))
            resultValue2 = cur.execute("SELECT * FROM fitcook.Dish")
            Dishdetails = cur.fetchall()
            mysql.connection.commit()
            cur.close()
            
        if request.form['submit_button'] == 'Back':
            return redirect(url_for('index1'))

    return render_template('Dietician_New_DISH.html',Dishdetails= Dishdetails)


@app.route('/Dish',methods=['GET', 'POST'])
def index1():
    cur = mysql.connection.cursor()
    cur1 = mysql.connection.cursor()
    Dietician_ID = 11
    resultValue = cur.execute(" SELECT * FROM (fitcook.Dish NATURAL JOIN fitcook.assesses) WHERE Dietician_ID = %s",(Dietician_ID,))
    resultValue123 = cur1.execute(" SELECT * FROM fitcook.Dietician WHERE Dietician_ID = %s",(Dietician_ID,))
    if resultValue > 0:
        Dishdetails = cur.fetchall()
        Dietician_Details = cur1.fetchall()
        if request.method == 'POST':
            if request.form['submit_button'] == 'Select':
                input = request.form
                id = input['id']
                print(id)
                cur.close()
                return redirect(url_for('Dish_edit', id=id))
            if request.form['submit_button'] == 'Insert New Entry':
                return redirect(url_for('newDish',Dietician_ID= Dietician_ID))
            if request.form['submit_button'] == 'Delete_Entry':
                #here fitst extract input id then write delete command then refresh
                input = request.form
                id = input['Dish_id_fordelete']
                cur.execute("""DELETE FROM fitcook.assesses WHERE Dish_ID = %s""",(id,))
                cur.execute("""DELETE FROM fitcook.Dish WHERE Dish_ID = %s""",(id,))

                resultValue1 = cur.execute(" SELECT * FROM (fitcook.Dish NATURAL JOIN fitcook.assesses) WHERE Dietician_ID = %s",(Dietician_ID,))
                Dishdetails = cur.fetchall()

                mysql.connection.commit()
                cur.close()
        return render_template("Dietician_Profile.html", Dishdetails= Dishdetails,Dietician_Details = Dietician_Details)

@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

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

if __name__ == "__main__":
	app.run(debug = True)
