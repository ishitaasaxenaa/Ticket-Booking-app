from application.database import db

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column( db.Integer, autoincrement = True , primary_key = True)
    username= db.Column(db.String,nullable = False)
    password =db.Column(db.String,nullable = False)
    role = db.Column(db.Integer, nullable = False)
    bookings = db.relationship('Booking_log',backref = 'user')

class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, autoincrement = True , primary_key = True)
    name = db.Column(db.String )
    place = db.Column(db.String)
    v_capacity = db.Column(db.Integer)
    
class Shows(db.Model):
    __tablename__ = 'Shows'
    id = db.Column(db.Integer, autoincrement = True , primary_key = True)
    name = db.Column(db.String )
    tags = db.Column(db.String)
    ratings = db.Column(db.Integer)
    price = db.Column(db.Integer)

class VS_mapping(db.Model):
    __tablename__ ='VS_mapping'
    id = db.Column(db.Integer,autoincrement = True , primary_key = True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id') , primary_key = True , nullable = False)
    show_id = db.Column(db.Integer, db.ForeignKey('Shows.id') , primary_key = True , nullable = False)
    time = db.Column(db.String)
    capacity = db.Column(db.Integer)
    
    # users= db.relationship('User',secondary = 'Booking_log',overlaps="bookings")

class Booking_log(db.Model):
    __tablename__ = "Booking_log"
    id = db.Column(db.Integer,autoincrement = True,primary_key = True)
    vs_id = db.Column(db.Integer, db.ForeignKey('VS_mapping.id') , primary_key = True , nullable = False)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id') , primary_key = True , nullable = False)
    tickets = db.Column(db.Integer)
