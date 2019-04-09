from flask_table import Table, Col, LinkCol

class Result(Table):
    id = Col('UserID')
    username = Col('username')