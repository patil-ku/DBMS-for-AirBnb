from flask_table import Table, Col, LinkCol

class Result(Table):
    id = Col('UserID')
    username = Col('username')


class ResultProperties(Table):
    property_id = Col('p.property_id')
    property_name = Col('property_name')
    street = Col('street')
    city = Col('city')
    postcode = Col('postcode')
    rent_price = Col('rent_price')
    property_rating = Col('property_rating')
