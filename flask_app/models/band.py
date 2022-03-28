from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app import app
bcrypt = Bcrypt(app)
from flask_app.models import user

class Band:
    db = "py_exam_2_schema"
    def __init__(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.genre = data["genre"]
        self.city = data["city"]

        self.user = {}

    @staticmethod
    def validate_band(raw_form_data):
        is_valid = True

        if not raw_form_data["name"]:
            flash("No input detected in Name field")
            is_valid = False

        elif len(raw_form_data["name"]) < 2:
            flash("Name must be at least 2 characters long")
            is_valid = False

        if not raw_form_data["genre"]:
            flash("No input detected in Genre field")
            is_valid = False

        elif len(raw_form_data["genre"]) < 2:
            flash("Genre must be at least 2 characters long")
            is_valid = False

        if not raw_form_data["city"]:
            flash("No input detected in City field")
            is_valid = False

        return is_valid

    @classmethod
    def get_all_bands(cls):
        query = "SELECT * FROM bands"
        query_result = connectToMySQL(cls.db).query_db(query)
        return query_result

    @classmethod
    def get_bands_and_users(cls):
        query = """SELECT bands.id, bands.name, bands.genre, bands.city, bands.users_id, bands.created_at, bands.updated_at, users.id AS "user_id", users.first_name AS user_fname, users.last_name AS user_lname, users.email FROM bands
                JOIN users ON bands.users_id = users.id
                ORDER BY bands.id"""
        query_result = connectToMySQL(cls.db).query_db(query)
        all_bands_with_users = []
        for band in query_result:
            all_bands_with_users.append( cls(band))
        return query_result

    @classmethod
    def get_bands_createdby_user(cls,data):
        query = "SELECT * FROM bands WHERE users_id = %(id)s"
        query_result = connectToMySQL(cls.db).query_db(query,data)
        return query_result

    @classmethod
    def get_bands_joinedby_user(cls,data):
        check_query = """SELECT users.id, bands.id AS band_id, bands.name
                        FROM users
                        join users_in_bands ON users.id = users_in_bands.users_id AND users_in_bands.bands_id
                        join bands ON users_in_bands.bands_id = bands.id
                        Where (users.id = %(id)s)"""
        query_result = connectToMySQL(cls.db).query_db(check_query,data)
        return query_result

    @classmethod
    def get_band_by_ID(cls,data):

        query = """SELECT * FROM bands
        LEFT JOIN users ON bands.users_id = users.id
        WHERE bands.id = %(id)s;"""

        query_result = connectToMySQL(cls.db).query_db(query,data)
        if len(query_result) < 1:
            return False

        newband = ( cls(query_result[0]))
        userData = {
        "id" : query_result[0]["users.id"],
        "first_name" : query_result[0]["first_name"],
        "last_name" : query_result[0]["last_name"],
        "email" : query_result[0]["email"],
        "password" : query_result[0]["password"],
        "created_at" : query_result[0]["users.created_at"],
        "updated_at" : query_result[0]["users.updated_at"],
        }

        userInstance = user.User(userData)
        newband.user = userInstance

        return newband

    @classmethod
    def create_band(cls,data):
        query = """INSERT INTO bands (name, genre, city, created_at, updated_at, users_id) VALUES (%(name)s, %(genre)s, %(city)s, NOW(), NOW(), %(user_id)s);"""
        query_result = connectToMySQL(cls.db).query_db(query,data)
        return query_result

    @classmethod
    def edit_band(cls,data):
        query = """UPDATE bands SET name = %(name)s,genre = %(genre)s,city = %(city)s WHERE id = %(id)s ; """
        query_result = connectToMySQL(cls.db).query_db(query,data)
        return query_result

    @classmethod
    def delete_band(cls,id):
        query = "DELETE FROM users_in_bands WHERE bands_id = %(id)s;"
        query_result = connectToMySQL(cls.db).query_db(query,id)

        query = "DELETE FROM bands WHERE `id` = %(id)s"
        query_result = connectToMySQL(cls.db).query_db(query,id)
        return query_result

    @classmethod
    def date_check(cls,raw_form_data):
        current_year_query = "SELECT YEAR(NOW()) AS 'year';"
        date_check = "SELECT YEAR(%(city)s) AS 'year';"
        date_check_data= {
            "city" : raw_form_data["city"]
        }
        check_result = connectToMySQL(cls.db).query_db(date_check,date_check_data)
        current_year_result = connectToMySQL(cls.db).query_db(current_year_query)
        if check_result[0]['year'] > current_year_result[0]['year'] or check_result[0]['year'] < 1900:
            return False
        return True
