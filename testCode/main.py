import os
import pymysql
from bookmanager import app
from db_config import mysql
from flask import flash, render_template, request, redirect
from tables import Result


@app.route("/", methods=['GET', 'POST'])
def add_user():
    try:
        sql = "INSERT INTO testingUsers (username) VALUES (%s)"
        username = request.form['user_name']
        data = username
        conn = mysql.connect()
        cursor = conn.cursor()
        cursor.execute(sql, data)
        conn.commit()
        flash('User added successfully')
        cursor.close()
        conn.close()
    except Exception as e:
        print(e)
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



if __name__ == "__main__":
    app.run(debug=True)