from flask import Flask, render_template,request,url_for, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'fitcook.cwx1jntgf3ei.us-east-2.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'fitcook123'
app.config['MYSQL_DB'] = 'fitcook'

mysql = MySQL(app)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Fetch form data
        userDetails = request.form
        name = userDetails['name']
        email = userDetails['email']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO login(name, email) VALUES(%s, %s)",(name, email))
        mysql.connection.commit()
        cur.close()
        return 'sucess!'
    return render_template('index.html')
    
    




@app.route('/Dish_edit/<string:id>',methods=['GET', 'POST'])
def Dish_edit(id):
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM fitcook.Dish WHERE Dish_ID = %s",id)
    if resultValue > 0:
        Dishdetails = cur.fetchall()
        if request.method == 'POST':
            if request.form['submit_button'] == 'Update':
                input = request.form
                attribute = input['attribute']
                updated_value = input['updated_attribute']
                print(attribute)
                print(updated_value)
                
                cur.execute("UPDATE fitcook.Dish SET %s = %s WHERE Dish_ID = %s"%(attribute,updated_value,id))

                resultValue1 = cur.execute("SELECT * FROM fitcook.Dish WHERE Dish_ID = %s",id)
                Dishdetails = cur.fetchall()

                mysql.connection.commit()
                cur.close()

        return render_template('Dish_edit.html', Dishdetails= Dishdetails)




@app.route('/Dish',methods=['GET', 'POST'])
def index1():
    cur = mysql.connection.cursor()
    resultValue = cur.execute("SELECT * FROM fitcook.Dish")
    if resultValue > 0:
        Dishdetails = cur.fetchall()
        if request.method == 'POST':
            input = request.form
            id = input['id']
            print(id)
            cur.close()
            return redirect(url_for('Dish_edit', id=id))
        return render_template("Dish_details.html", Dishdetails= Dishdetails)

if __name__ == "__main__":
	app.run(debug = True)
