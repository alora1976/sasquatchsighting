# import the function that will return an instance of a connection
from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re
from flask_app.models import user
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask_bcrypt import Bcrypt
DB = "sighting"

class Sighting:
    
    def __init__(self, sighting):
        self.id = sighting["id"]
        self.location = sighting["location"]
        self.what_happened = sighting["what_happened"]
        self.num_sasquatches = sighting["num_sasquatches"]
        self.date_made = sighting["date_made"]
        self.created_at = sighting["created_at"]
        self.updated_at = sighting["updated_at"]
        self.user = None

    @classmethod
    def create_valid_sighting(cls, sighting_dict):
        if not cls.is_valid(sighting_dict):
            return False
        
        query = """INSERT INTO sightings (location, what_happened, num_sasquatches, date_made, user_id) VALUES (%(location)s, %(what_happened)s,%(num_sasquatches)s, %(date_made)s, %(user_id)s);"""
        sighting_id = connectToMySQL(DB).query_db(query, sighting_dict)
        sighting = cls.get_by_id(sighting_id)

        return sighting

    @classmethod
    def get_by_id(cls, sighting_id):

        data = {"id": sighting_id}
        query = "SELECT * FROM sightings WHERE id = %(id)s;"
        result = connectToMySQL(DB).query_db(query,data)[0]
        sighting = cls(result)

        user_obj = user.User.get_by_id(result["user_id"])

        sighting.user = user_obj

        return sighting

    @classmethod
    def delete_sighting_by_id(cls, sighting_id):

        data = {"id": sighting_id}
        query = "DELETE from sightings WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return sighting_id


    @classmethod
    def update_sighting(cls, sighting_dict, session_id):

        # Authenticate User first
        sighting = cls.get_by_id(sighting_dict["id"])
        if sighting.user.id != session_id:
            flash("You must be the creator to update this sighting.")
            return False

        # Validate the input
        if not cls.is_valid(sighting_dict):
            return False
        
        # Update the data in the database.
        query = """UPDATE sightings
                    SET location = %(location)s, what_happened = %(what_happened)s, num_sasquatches = %(num_sasquatches)s, date_made = %(date_made)s
                    WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,sighting_dict)
        sighting = cls.get_by_id(sighting_dict["id"])
        
        return sighting

    @classmethod
    def get_all(cls):
        # Get all sightings, and the user info for the creators
        query = """SELECT 
                    sightings.id, sightings.created_at, sightings.updated_at, what_happened, location, num_sasquatches, date_made,users.id as user_id,first_name,last_name,email,users.created_at as uc,users.updated_at as uu
                    FROM sightings
                    JOIN users on users.id = sightings.user_id;"""
        sighting_data = connectToMySQL(DB).query_db(query)

        # Make a list to hold sighting objects to return
        sightings = []

        # Iterate through the list of sighting dictionaries
        for sighting in sighting_data:

            # convert data into a sighting object
            sighting_obj = cls(sighting)

            # convert joined user data into a user object
            sighting_obj.user = user.User(
                {
                    "id": sighting["user_id"],
                    "first_name": sighting["first_name"],
                    "last_name": sighting["last_name"],
                    "email": sighting["email"],
                    "created_at": sighting["uc"],
                    "updated_at": sighting["uu"]
                }
            )
            sightings.append(sighting_obj)


        return sightings

    @staticmethod
    def is_valid(sighting_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(sighting_dict["location"]) < 3:
            flash("location " + flash_string)
            valid = False
        if len(sighting_dict["what_happened"]) < 3:
            flash("what_happened " + flash_string)
            valid = False
        if len(sighting_dict["num_sasquatches"]) < 1:
            flash("num_sasquatches " + flash_string)
            valid = False

        if len(sighting_dict["date_made"]) <= 0:
            flash("Date is required.")
            valid = False
        

        return valid