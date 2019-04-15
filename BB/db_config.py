from app import app
from flaskext.mysql import MySQL

mysql = MySQL()

# MySQL configurations

app.config['MYSQL_DATABASE_USER'] = 'master_root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'master_password'
app.config['MYSQL_DATABASE_DB'] = 'dbms_airbnb'
app.config['MYSQL_DATABASE_HOST'] = 'kspatildb.cl2qfzprykvu.us-east-1.rds.amazonaws.com'
mysql.init_app(app)

# Local config::
#
# app.config['MYSQL_DATABASE_USER'] = 'root'
# app.config['MYSQL_DATABASE_PASSWORD'] = 'Expert123'
# app.config['MYSQL_DATABASE_DB'] = 'dbms_airbnb'
# app.config['MYSQL_DATABASE_HOST'] = 'localhost'
# mysql.init_app(app)
