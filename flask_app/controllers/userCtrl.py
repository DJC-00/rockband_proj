from flask_app import app
from flask import render_template,redirect,request,session,flash
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)
from flask_app.models.band import Band
from flask_app.models.user import User
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not "user_id" in session:
            flash("Access Denied: Login Required")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def login_registration_page():
    return render_template('log_and_reg.html')

@app.route('/login', methods=['POST'])
def user_login():
    if not User.validate_login(request.form):
        return redirect('/')
    
    query_data = {
        "email" : request.form["email"],
    }

    current_user = User.get_user_by_email(query_data)
    session["user_id"] = current_user.id
    session["user_name"] = current_user.first_name
    return redirect ('/dashboard')

@app.route('/register', methods=['POST'])
def user_register():
    if not User.validate_registration(request.form):
        return redirect('/')
    
    pass_hash = bcrypt.generate_password_hash(request.form["password"])

    query_data = {
        "first_name" : request.form["first_name"],
        "last_name" : request.form["last_name"],
        "email" : request.form["email"],
        "first_name" : request.form["first_name"],
        "password" : pass_hash
    }

    new_user = User.create_user(query_data)
    current_user = User.get_user_by_email(query_data)
    session["user_id"] = current_user.id
    session["user_name"] = current_user.first_name
    return redirect ('/dashboard')

@app.route('/dashboard')   
@login_required
def home():
    query_data = {
        'id' : session["user_id"]
    }
    current_user = User.get_user_by_ID(query_data)
    user_bands_joined = User.get_user_bands_joined(query_data)
    all_bands = Band.get_all_bands()
    all_bands_with_users = Band.get_bands_and_users()
    return render_template('/dashboard.html', current_user = current_user, all_bands_with_users = all_bands_with_users, user_bands_joined = user_bands_joined )


@app.route("/logout")
@login_required
def logout():
    session.clear();
    return redirect("/")

@app.route("/user/band/join/<int:user_id>/<int:band_id>")
@login_required
def join_band(user_id, band_id):
    query_data =  {
        "id" : band_id
    }
    creator_id = Band.get_band_by_ID(query_data)
    if session['user_id'] == creator_id.user.id:
        flash("Cannot join or quit band you created")
        return redirect('/dashboard')
    query_data =  {
        "users_id" : user_id,
        "bands_id" : band_id
    }
    User.user_join_band(query_data)
    return redirect(request.referrer)

@app.route("/user/bands_info")
@login_required
def show_profile():
    query_data = {
        'id' : session["user_id"]
    }
    my_bands = Band.get_bands_createdby_user(query_data)
    joined_bands = Band.get_bands_joinedby_user(query_data)
    return render_template('/bandsPage.html', my_bands = my_bands, joined_bands = joined_bands, current_user_id = session["user_id"])