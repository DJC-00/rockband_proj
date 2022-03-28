from flask_app import app
from flask import render_template,redirect,request,session,flash
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

#------------------- view --------------------

@app.route('/band/info/<int:band_id>')
@login_required
def view_band(band_id):
    query_data = {
        'id' : band_id
    }
    one_band = Band.get_band_by_ID(query_data)
    return render_template("bandPage.html", one_band = one_band)

#------------------- create --------------------

@app.route('/band/create/')
@login_required
def create_band():
    return render_template("bandForm.html")
    
@app.route('/band/create/confirm', methods = ['POST'])
@login_required
def create_band_confirm():
    if not Band.validate_band(request.form):
        return redirect(request.referrer)

    query_data = {
        'name' : request.form['name'],
        'genre' : request.form['genre'],
        'city' : request.form['city'],
        'user_id' : session['user_id']
    }
    Band.create_band(query_data)
    return redirect('/dashboard')
    

#------------------- edit --------------------

@app.route('/band/edit/<int:band_id>')
@login_required
def edit_band(band_id):
    query_data = {
        "id" : band_id
    }
    one_band = Band.get_band_by_ID(query_data)
    if session["user_id"] != one_band.user.id:
        flash("Posts can only be edited by their creators")
        return redirect("/dashboard")
    return render_template("bandForm.html", one_band = one_band, edit = True)

@app.route('/band/edit/confirm/<int:band_id>', methods = ['POST'])
@login_required
def edit_band_confirm(band_id):
    if not Band.validate_band(request.form):
        return redirect(request.referrer)
    query_data = {
        'id' : band_id,
        'name' : request.form['name'],
        'genre' : request.form['genre'],
        'city' : request.form['city']
    }
    one_band = Band.get_band_by_ID(query_data)
    if session["user_id"] != one_band.user.id:
        flash("This is not your band!")
        return redirect("/dashboard")
    Band.edit_band(query_data)
    return redirect('/dashboard')

#------------------- delete --------------------

@app.route('/band/delete/confirm/<int:band_id>')
@login_required
def delete_band_confirm(band_id):
    query_data = {
        'id' : band_id
    }
    one_band = Band.get_band_by_ID(query_data)
    if session["user_id"] != one_band.user.id:
        flash("This is not your band!")
        return redirect("/dashboard")
    Band.delete_band(query_data)
    return redirect(request.referrer)

