from flask_restful import Resource
from flask import request
from application.models import Shows,Venue,Booking_log,User,VS_mapping
from application.database import db


class VenueApi(Resource):
    def post(self,venue_id = None):
        if (venue_id == None):
            v_name = request.form['name']
            v_place = request.form['location']
            v_capacty = request.form['capacity']
            new_venue = Venue(name = v_name, place = v_place, v_capacity = v_capacty)
            db.session.add(new_venue)
            db.session.commit()
            return "Venue Created"
        else:
            print(request.form.get('name'))
            
            print(venue_id)
            s_name = request.form['name']
            s_rating = request.form['rating']
            s_timing = request.form['timing']
            s_tag = request.form['tag']
            s_price = request.form['price']
            venue_capacity = Venue.query.filter(Venue.id == venue_id).first().v_capacity
            new_show = Shows(name = s_name,ratings =s_rating,tags = s_tag,price = s_price)
            db.session.add(new_show)
            db.session.commit()
            new_vs = VS_mapping(venue_id = venue_id,show_id = new_show.id,time= s_timing, capacity = venue_capacity)
            db.session.add(new_vs)
            db.session.commit()
            return "Show added to the Venue"
    
    # def delete(self,venue_id):
    #     delete_vs = VS_mapping.query.filter(VS_mapping.venue_id == venue_id).all()
    #     for i in delete_vs:
    #         showidtodelete=i.show_id
    #         a=Shows.query.filter(Shows.id==showidtodelete).first()
    #         db.session.delete(a)
    #         db.session.delete(i)
    #     delete_venue = Venue.query.filter(Venue.id == venue_id).first()
    #     db.session.delete(delete_venue)
    #     db.session.commit()
    #     return "Venue Deleted"
    def delete(self,venue_id):
        delete_vs = VS_mapping.query.filter(VS_mapping.venue_id == venue_id).all()
        for i in delete_vs:
            showidtodelete=i.show_id
            a=Shows.query.filter(Shows.id==showidtodelete).first()
            bookingstodelete = Booking_log.query.filter(Booking_log.vs_id == i.id).all()
            print("deleting bookings")
            for j in bookingstodelete:
                db.session.delete(j)
            db.session.delete(a)
            print("deleted show")
            db.session.delete(i)
            print("deleted vs_map")
        db.session.commit()
        delete_venue = Venue.query.filter(Venue.id == venue_id).first()
        db.session.delete(delete_venue)
        db.session.commit()
        print("call done")
        return "Venue Deleted"
    
    def put(self,venue_id):
        v_name = request.form['name']
        v_place = request.form['location']
        v_capacty = request.form['capacity']
        
        change_venue = Venue.query.filter(Venue.id == venue_id).first()
        change_venue.name = v_name
        change_venue.place = v_place
        change_venue.v_capacity = v_capacty
        
        db.session.commit()
        return "Venue Edited"
    
class VenueShowApi(Resource):
    # def delete(self,venue_id,show_id):
        
    #     vs = VS_mapping.query.filter(VS_mapping.venue_id == venue_id, VS_mapping.show_id == show_id).first()
    #     db.session.delete(vs)
    #     db.session.commit()
    #     return "Show deleted from the venue"
    def delete(self,venue_id,show_id):

        vs = VS_mapping.query.filter(VS_mapping.venue_id == venue_id, VS_mapping.show_id == show_id).first()
        bookingstodelete = Booking_log.query.filter(Booking_log.vs_id == vs.id).all()
        for i in bookingstodelete:
            db.session.delete(i)
        show = Shows.query.filter(Shows.id == show_id).first()
        db.session.delete(vs)
        db.session.delete(show)
        db.session.commit()
        return "Show deleted from the venue"
        
    def put(self,venue_id,show_id):

        s_name = request.form['name']
        s_rating = request.form['rating']
        s_timing = request.form['timing']
        s_tag = request.form['tag']
        s_price = request.form['price']
        changed_show = Shows.query.filter(Shows.id == show_id).first()
        changed_show.name = s_name
        changed_show.ratings = s_rating
        changed_show.tags = s_tag
        changed_show.price = s_price
        
        changed_vs = VS_mapping.query.filter(VS_mapping.venue_id == venue_id, VS_mapping.show_id == show_id).first()
        changed_vs.time = s_timing
        db.session.commit()
        return "Edited show details at the particular venue"

class DashboardApi(Resource):
    def get(self):
        vs_map = []
        vq = Venue.query.all()
        for i in vq:
            show_time = VS_mapping.query.filter(VS_mapping.venue_id == i.id).all()
            v_shows = []
            for j in show_time:
                show = Shows.query.filter(Shows.id == j.show_id).first()
                show_dict = {'name': show.name, 'price': show.price,
                            'ratings': show.ratings, 'time': j.time,'tags':show.tags, 'vs_id': j.id, 'vs_capacity':j.capacity}
                v_shows.append(show_dict)
        
            venue_dict = {}
            venue_dict = {'name': i.name, 'place': i.place, 'show': v_shows}
            vs_map.append(venue_dict)
        return vs_map
    