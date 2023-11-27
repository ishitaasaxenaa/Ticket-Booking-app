from application.models import Shows, Venue, VS_mapping, User, Booking_log
import os
from application.database import db
from flask import Flask
from flask import render_template
from flask import url_for, redirect
from flask import request
import requests
from flask import redirect
from flask_restful import Api


from application.api import VenueApi, VenueShowApi, DashboardApi
app = Flask(__name__)

# creates a Flask instance and name is the name of current file
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))


# loading configurations in the app and assigning a path for the database
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(basedir, "database.db")

db.init_app(app)
app.app_context().push()

# Add api
api = Api(app)
app.app_context().push()
api.add_resource(VenueApi,'/api/venue', '/api/venue/<int:venue_id>')
api.add_resource(VenueShowApi, '/api/venueshow/<int:venue_id>/<int:show_id>')
api.add_resource(DashboardApi, '/api/dash')


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        new_user = User.query.filter_by(
            username=request.form['username']).first()
        if new_user is None:
            n_user = User(
                username=request.form['username'], password=request.form['password'], role=0)
            db.session.add(n_user)
            db.session.commit()
            return redirect(url_for('home'))
        else:
            return render_template('usexist.html')

@app.route('/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'GET':
        return render_template('user_login.html')
    if request.method == 'POST':
        user = User.query.filter(
            User.username == request.form['username'], User.password == request.form['password']).first()
        if user != None:
            
            return redirect(url_for('.dash', user=user.id))
        else:
            return render_template('login_error.html')

@app.route('/home')
def dash():
    user = User.query.filter(User.id == int(request.args['user'])).first()
    url=f"http://localhost:8080/api/dash"
    response=requests.get(url=url)
    vs_map=response.json()
    return render_template('user_dash.html', vs=vs_map, user=user)

@app.route('/book/<int:user_id>/<int:vs_id>', methods=['GET', 'POST'])
def book(user_id, vs_id):
    if request.method == 'GET':
        book_data = {}
        vsmp = VS_mapping.query.filter(VS_mapping.id == vs_id).first()
        capacity = vsmp.capacity
        show_id = vsmp.show_id
        time = vsmp.time
        show_ = Shows.query.filter(Shows.id == show_id).first()
        show_name = show_.name
        show_price = show_.price
        book_data = {'available_seats': capacity,
                     'show_name': show_name, 'time': time, 'show_price': show_price}
        return render_template('book.html', book_data=book_data, user_id=user_id, vs_id=vs_id)

    if request.method == 'POST':
        new_booking = Booking_log(
            user_id=user_id, vs_id=vs_id, tickets=int(request.form['number-input']))
        current_vs = VS_mapping.query.filter(VS_mapping.id == vs_id).first()
        current_vs.capacity -= int(request.form['number-input'])
        db.session.add(new_booking)
        db.session.commit()
        return render_template('booking_confirmation.html', user_id=user_id)

@app.route('/booking')
def show_booking():
    user = User.query.filter(User.id == int(request.args['user'])).first()
    bookings = Booking_log.query.filter(
        Booking_log.user_id == int(request.args['user'])).all()
    bookings_list = []
    print(bookings)
    for i in bookings:
        if (i.vs_id != None):

            vs = VS_mapping.query.filter(VS_mapping.id == i.vs_id).first()
            print(vs)
            venue_name = Venue.query.filter(Venue.id == vs.venue_id).first().name
            show_name = Shows.query.filter(Shows.id == vs.show_id).first().name
            tickets = i.tickets
            time = vs.time
            curr_booking = {'venue': venue_name, 'show': show_name,
                            'tickets': tickets, 'time': time}
            bookings_list.append(curr_booking)
        print(bookings_list)
    return render_template('Your_bookings.html', bookings_list=bookings_list, user=user)

@app.route('/logout')
def logout():
    return redirect('/')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        user = User.query.filter(
            User.username == request.form['username'], User.password == request.form['password'], User.role == 1).first()
        if user == None:
            return render_template("Not_admin.html")
        else:
            return redirect(url_for('.admin_dash'))

@app.route('/admin_dash')
def admin_dash():
    vs_map = []
    vs = Venue.query.all()

    for i in vs:
        show_time = VS_mapping.query.filter(VS_mapping.venue_id == i.id).all()
        v_shows = []

        for j in show_time:
            show = Shows.query.filter(Shows.id == j.show_id).first()
            show_dict = {'name': show.name, 'price': show.price, 'ratings': show.ratings, 'time': j.time, 'vs_id': j.id,
                         'show_id': show.id , 'tags': show.tags}
            v_shows.append(show_dict)

        venue_dict = {}
        venue_dict = {'name': i.name, 'place': i.place,
                      'show': v_shows, 'id': i.id}
        vs_map.append(venue_dict)
    return render_template('admin_dashboard.html', vs=vs_map)


@app.route('/create_venue', methods=['GET', 'POST'])
def create_venue():
    if request.method == 'GET':
        return render_template('create_venue.html')
    if request.method == 'POST':
        s = request.form.to_dict()
        print(s)
        url = f"http://localhost:8080/api/venue"
        response = requests.post(url=url, data=s)

        if (response.ok):
            return render_template('venue_added.html')

@app.route('/create_show',methods = ['GET','POST'])
def creat_show():
    if request.method == 'GET':
        venues = Venue.query.all()
        return render_template('create_show_form.html',venues = venues)
    if request.method == 'POST':
            
        s = request.form.to_dict()
        venues = request.form.getlist('venue')  # get a list of all selected venues
        for i in venues:
            venue_id = int(i)
            url = f"http://localhost:8080/api/venue/{venue_id}"
            requests.post(url=url, data=s)

        return render_template("show_added.html")

@app.route('/add_show/<int:venue_id>', methods=['GET', 'POST'])
def add_show(venue_id):
    if request.method == "GET":
        return render_template("add_show_venue.html", venue_id=venue_id)
    if request.method == "POST":
        s = request.form.to_dict()
        url = f"http://localhost:8080/api/venue/{venue_id}"
        response=requests.post(url=url, data=s)
        
        if (response.ok):   
            return render_template("show_added.html")

@app.route('/delete_show/<int:venue_id>/<int:show_id>')
def delete_show(venue_id, show_id):
    url = f"http://localhost:8080/api/venueshow/{venue_id}/{show_id}"
    response = requests.delete(url=url)

    if (response.ok):
        return redirect('/admin_dash')

@app.route('/edit_show/<int:venue_id>/<int:show_id>', methods=['GET', 'POST'])
def edit_show(venue_id, show_id):
    if request.method == 'GET':
        show = Shows.query.filter(Shows.id == show_id).first()
        vs = VS_mapping.query.filter(
            VS_mapping.venue_id == venue_id, VS_mapping.show_id == show_id).first()
        return render_template('edit_show.html', show=show, vs=vs, venue_id=venue_id)
    if request.method == 'POST':
        s = request.form.to_dict()
        url = f"http://localhost:8080/api/venueshow/{venue_id}/{show_id}"
        response = requests.put(url=url, data=s)

        if (response.ok):
            return redirect('/admin_dash')

@app.route('/delete_venue/<int:venue_id>')
def delete_venue(venue_id):
    url = f"http://localhost:8080/api/venue/{venue_id}"
    response = requests.delete(url=url)

    if (response.ok):
        return redirect('/admin_dash')

@app.route('/edit_venue/<int:venue_id>', methods=["GET","POST"])
def edit_venue(venue_id):
    if request.method=="GET":
        venue=Venue.query.filter(Venue.id==venue_id).first()
        return render_template("edit_venue.html", venue=venue)
    if request.method=="POST":
        s=request.form.to_dict()
        url = f"http://localhost:8080/api/venue/{venue_id}"
        response=requests.put(url=url, data=s)
        if (response.ok):
            return redirect("/admin_dash")


@app.route('/search',methods= ['GET','POST'])
def search():
    query = request.form['searched']
    user = User.query.filter(User.id == int(request.args['user'])).first()
    shows = Shows.query.filter((Shows.name.like('%' + query + '%'))  | (Shows.tags.like('%' + query + '%')) | (Shows.ratings.like('%' + query + '%'))).all()
    print(shows)
    print(shows)

    if (shows != []):
        venues_with_show = []
        for i in shows:
            
            vs_map = {}
            vs_ = VS_mapping.query.filter(VS_mapping.show_id == i.id).first()
            if vs_ is not None:
                print(vs_.time)
                show_dict = {'name': i.name, 'price': i.price,
                                    'ratings': i.ratings, 'time': vs_.time,'tags':i.tags, 'vs_id': vs_.id,'vs_capacity':vs_.capacity}
                venue = Venue.query.filter(Venue.id == vs_.venue_id).first()
                vs_map = {'name':venue.name, 'location':venue.place, 'show':show_dict}
                venues_with_show.append(vs_map)
            
        print(venues_with_show)
        return render_template('search.html',results =venues_with_show,user = user)
    else:
        vs_map = []
        venue = Venue.query.filter(Venue.place.like('%' + query + '%')).all()
        print(venue)
        for i in venue:
            show_time = VS_mapping.query.filter(VS_mapping.venue_id == i.id).all()
            v_shows = []
            for j in show_time:
                show = Shows.query.filter(Shows.id == j.show_id).first()
                show_dict = {'name': show.name, 'price': show.price,
                            'ratings': show.ratings, 'time': j.time, 'tags':show.tags,'vs_id': j.id,'vs_capacity':j.capacity}
                v_shows.append(show_dict)

            venue_dict = {}
            venue_dict = {'name': i.name, 'place': i.place, 'show': v_shows}
            
            vs_map.append(venue_dict)
        return render_template('user_dash.html', vs=vs_map, user=user)


        
app.run(
    host='0.0.0.0',
    debug=True,
    port=8080)
