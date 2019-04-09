import pymysql
from app import app
from db_config import mysql
from flask import flash, render_template, request, redirect
from tables import Result


@app.route("/", methods=['GET'])
def show_home():
    return render_template("home.html")


@app.route("/showUsers")
def show_users():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM testingUsers")
        rows = cursor.fetchall()
        table = Result(rows)
        table.border = True
        cursor.close()
        conn.close()
        return render_template("show_users.html", table=table)
    except Exception as e:
        print(e)


@app.route("/login", methods=['GET', 'POST'])
def user_login():
    error = None
    username = request.form['user_name']
    user_password = request.form['user_password']
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        sql = "SELECT username, user_password FROM auth WHERE username = %s "
        cursor.execute(sql, username)
        result = cursor.fetchone()
        # Check if the user exists
        if not result:
            error = "This username does not exist please try again"
            flash(error)
            return render_template("home.html", error=error)
        # If user exists, check complete credentials
        if username == result[0] and user_password == result[1]:
            # Find a way to display a proper message for the user that he is logged in
            return render_template("welcome_user.html")
        else:
            error = "Password did not match, please try again"
            return render_template("home.html", error=error)
    except Exception as e:
        print(e)
        return render_template("home.html")
    finally:
        conn.close()


@app.route('/redirectRegister', methods=['GET','POST'])
def redirect_register():
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)