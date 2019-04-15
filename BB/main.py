import pymysql
from app import app
from db_config import mysql
from flask import flash, render_template, request, session, redirect, url_for


@app.route("/", methods=['GET'])
def show_home():
    return render_template("home.html")


@app.route("/login", methods=['GET', 'POST'])
def user_login():
    username = request.form['user_name']
    user_password = request.form['user_password']
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        sql = "SELECT username, user_password FROM authorization WHERE username = %s "
        cursor.execute(sql, username)
        result = cursor.fetchone()
        # Check if the user exists
        if not result:
            error = "This username does not exist please sign up"
            return render_template("home.html", error=error)
        # If user exists, check complete credentials
        if username == result[0] and user_password == result[1]:
            # Check if the user is a client or a property owner:
            cursor.execute('CALL user_type(%s)', username)
            type_of_user = cursor.fetchone()
            print(type_of_user)
            session['username'] = str(username)
            cursor.execute('CALL return_first_name(%s)', (session['username'],))
            name = cursor.fetchone()
            session['first_name'] = name
            print(session['first_name'])
            if type_of_user[0] == 1:
                # This means user is a client
                return render_template("userHome.html")
            elif type_of_user[0] == 2:
                # This user is a property owner
                return render_template("propertyOwnerHome.html")
            else:
                return render_template("adminPage.html")
        else:
            error = "Password did not match, please try again"
            return render_template("home.html", error=error)
    except Exception as e:
        print(e)
        return render_template("home.html", error='Database error, please try back again')
    finally:
        cursor.close()
        conn.close()


@app.route('/redirectRegister', methods=['GET', 'POST'])
def redirect_register():
    return render_template("register.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = mysql.connect()
    cursor = conn.cursor()
    user_username = request.form['username']
    user_first_name = request.form['first_name']
    user_last_name = request.form['last_name']
    user_email = request.form['email']
    user_password = request.form['user_password']
    user_address = request.form['address']
    user_phone = request.form['phone']
    user_type = request.form['options']
    # Check if this user already exists:
    try:
        sql = "SELECT username, user_password FROM authorization WHERE username = %s "
        cursor.execute(sql, user_username)
        result = cursor.fetchone()
        if result:
            error = "This username already exists, please take another username"
            return render_template("home.html", error=error)
    except Exception as e:
        print(e)
        return render_template("home.html", error='Database error while retrieving data, please try again later')
    try:
        if user_type == 'owner':
            cursor.callproc('property_user_registration', [user_username, user_password, user_first_name, user_last_name,
                                                           user_email, user_address, user_phone, ])
            conn.commit()
            session['username'] = user_username
            session['first_name'] = user_first_name
            return render_template('propertyOwnerHome.html', user=session['first_name'])
        else:
            cursor.callproc('client_user_registration', [user_username, user_password, user_first_name, user_last_name,
                                                         user_email, user_address, user_phone, ])
            conn.commit()
            session['username'] = user_username
            session['first_name'] = user_first_name
            return render_template('userHome.html', user=session['first_name'])
    except Exception as e:
        print(e)
        error = "Something went wrong with the database, please try again"
        return render_template("home.html", error=error)
    finally:
        cursor.close()
        conn.close()


@app.route('/findProperties', methods=['GET', 'POST'])
def find_properties():
    conn = mysql.connect()
    cursor = conn.cursor()
    city = request.form['city']
    max_rent = request.form['max_rent']
    min_rent = request.form['min_rent']
    check_in = request.form['check_in_date']
    check_out = request.form['check_out_date']
    session['property_filter'] = (session['username'], check_in, check_out)
    if max_rent < min_rent:
        error = "Please ensure that minimum rent is less that maximum rent"
        return render_template("userHome.html", error=error)
    if check_in > check_out:
        error = "Please ensure that check in date is after the check out date"
        return render_template("userHome.html", error=error)
    try:
        cursor.execute('CALL client_user_filtering(%s,%s,%s,%s,%s)', (city, min_rent, max_rent, check_in,
                                                                      check_out,))
        result = cursor.fetchall()
        return render_template('show_properties.html', result=result)
    except Exception as e:
        print(e)
        error = "Something went wrong please try again"
        return render_template("userHome.html", error=error)
    finally:
        cursor.close()
        conn.close()


@app.route('/bookProperty', methods=['GET', 'POST'])
def book_property():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        value_of_radio = request.form['propertyOptions']
        procedure_inputs = session['property_filter'] + (value_of_radio,)
        session.pop('property_filter', None)
        cursor.callproc('client_user_booking', procedure_inputs)
        conn.commit()
        return render_template('userHome.html', info='Successfully booked your stay, what '
                                                     'else would you like to do?')
    except Exception as e:
        print(e)
        error = "Something went wrong, please try again"
        return render_template("userHome.html", error=error)
    finally:
        cursor.close()
        conn.close()


@app.route('/showChangeBooking', methods=['GET', 'POST'])
def show_change_booking():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        username = session['username']
        cursor.execute('CALL client_view_booking(%s)', (username,))
        result = cursor.fetchall()
        print(result)
        if result:
            return render_template("userHome.html", result=result, update=True)
        else:
            return render_template("userHome.html", error="You don't have any bookings")
    except Exception as e:
        print(e)
        error = "Something went wrong while fetching data, please try again"
        return render_template("userHome.html", error=error)
    finally:
        cursor.close()
        conn.close()


@app.route('/changeBooking', methods=['GET', 'POST'])
def change_booking():
    conn = mysql.connect()
    cursor = conn.cursor()
    property_id = request.form['changeBookingOptions']
    check_in_date = request.form['new_check_in_date']
    check_out_date = request.form['new_check_out_date']
    if check_in_date > check_out_date:
        error = "Check in date cannot be after the check out date"
        return redirect(url_for('show_change_booking'))
    try:
        if cursor.callproc('client_update_booking', [property_id, check_in_date, check_out_date, ]):
            conn.commit()
            return render_template('userHome.html', info="We successfully updated your stay")
        else:
            return render_template('changeBooking.html', update=True, error='Could not update, please try again')
    except Exception as e:
        print(e)
        return render_template('changeBooking.html', update=True, error='Something went wrong, please try again')
    finally:
        cursor.close()
        conn.close()


@app.route('/showCancelBooking', methods=['GET', 'POST'])
def show_cancel_booking():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        username = session['username']
        cursor.execute('CALL client_view_booking(%s)', (username,))
        result = cursor.fetchall()
        print(result)
        if not result:
            return render_template("userHome.html", error="You don't have any bookings")
        else:
            return render_template("userHome.html", cancel=result)
    except Exception as e:
        print(e)
        error = "Something went wrong while fetching data, please try again"
        return render_template("userHome.html", error=error)
    finally:
        cursor.close()
        conn.close()


@app.route('/cancelBooking', methods=['GET', 'POST'])
def cancel_booking():
    conn = mysql.connect()
    cursor = conn.cursor()
    booking_id = request.form['cancelBookingOptions']
    try:
        if cursor.callproc('client_delete_booking', [booking_id, ]):
            conn.commit()
            return render_template('userHome.html', info="We successfully cancelled your booking")
        else:
            return render_template('userHome.html', error='Could not update your data')
    except Exception as e:
        print(e)
        return render_template('userHome.html', error='Something went wrong, sorry')
    finally:
        cursor.close()
        conn.close()


@app.route('/showOwnerProperties', methods=['GET', 'POST'])
def show_owner_properties():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('CALL return_first_name(%s)', (session['username'],))
    name = cursor.fetchone()
    try:
        cursor.execute('CALL owner_property_list(%s)', (session['username'],))
        result = cursor.fetchall()
        if result:
            return render_template('propertyOwnerHome.html', result=result)
        else:
            return render_template('propertyOwnerHome.html', error='Sorry, you do not have any properties listed yet')
    except Exception as e:
        print(e)
        return render_template('propertyOwnerHome.html', error='Database error, please try again')
    finally:
        cursor.close()
        conn.close()


@app.route('/updateOrDeleteProperties', methods=['GET', 'POST'])
def update_or_delete_properties():
    button_value = request.form['update_delete_property']
    property_id = request.form['updatePropertySelectPID']
    print(property_id)
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if button_value == 'update_property':
            # call update procedure
            new_rent = request.form['update_property_rent']
            if cursor.callproc('owner_update_property', [property_id, new_rent, ]):
                conn.commit()
                return render_template('propertyOwnerHome.html', info='Property was updated')
            else:
                return render_template('propertyOwnerHome.html', error='Failed to updated rent, please try again!')
        else:
            # delete property procedure
            if cursor.callproc('owner_delete_property', [property_id, ]):
                conn.commit()
                return render_template('propertyOwnerHome.html', info='Property was deleted')
            else:
                return render_template('propertyOwnerHome.html', error='Failed to delete property, please try again!')
    except Exception as e:
        print(e)
        return render_template('propertyOwnerHome.html', error='Database error, please try again')
    finally:
        cursor.close()
        conn.close()


@app.route('/addProperty', methods=['GET', 'POST'])
def add_property():
    property_name = request.form['property_name']
    property_street = request.form['property_street']
    property_city = request.form['property_city']
    property_postcode = request.form['property_postcode']
    property_rent = request.form['property_rent']
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if cursor.callproc('property_add', [session['username'], property_name, property_street, property_city,
                                            property_postcode, property_rent, ]):
            conn.commit()
            return render_template('propertyOwnerHome.html', info='Property added successfully.')
        else:
            return render_template('propertyOwnerHome.html', error='Property was not added, please try again')
    except Exception as e:
        print(e)
        return render_template('propertyOwnerHome.html', error='Database error, please try again!')
    finally:
        cursor.close()
        conn.close()


@app.route('/updateUser', methods=['GET', 'POST'])
def update_user():
    new_first_name = request.form['new_first_name']
    new_last_name = request.form['new_last_name']
    new_password = request.form['new_password']
    new_address = request.form['new_address']
    new_email = request.form['new_email']
    new_number = request.form['new_number']
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if cursor.callproc('update_user_profile', [session['username'], new_password, new_first_name, new_last_name,
                                                   new_email, new_address, new_number, ]):
            conn.commit()
            return render_template('userHome.html', info='Successfully updated user profile')
        else:
            return render_template('userHome.html', error='Failed updating user profile, please try again!')
    except Exception as e:
        print(e)
        return render_template('userHome.html', error='Database Error')
    finally:
        cursor.close()
        conn.close()


@app.route('/deleteUserAccount', methods=['GET', 'POST'])
def delete_user():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        if cursor.callproc('delete_user_profile', [session['username'], ]):
            conn.commit()
            return render_template('home.html')
        else:
            return render_template('userHome.html', error='Failed deleting user profile, please try again')
    except Exception as e:
        print(e)
        return render_template('userHome.html', error='Database error, please try again')
    finally:
        cursor.close()
        conn.close()


@app.route('/showAllBookings', methods=['GET', 'POST'])
def show_booking_history():
    conn = mysql.connect()
    cursor = conn.cursor()
    try:
        cursor.execute('CALL client_view_history(%s)', (session['username'], ))
        result = cursor.fetchall()
        if result:
            return render_template('userHome.html', history=result)
        else:
            return render_template('userHome.html', info='Sorry, no bookings for this username were found')
    except Exception as e:
        print(e)
        return render_template('userHome.html', error='Database error, please try again later')
    finally:
        cursor.close()
        conn.close()


@app.route('/logOut')
def sign_out():
    session.pop('username')
    return redirect(url_for('show_home'))


if __name__ == "__main__":
    app.run(debug=True)
