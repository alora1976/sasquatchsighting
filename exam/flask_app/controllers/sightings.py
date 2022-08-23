from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models.user import User
from flask_app.models.sighting import Sighting
from flask import flash

######## RENDERING GET METHODS ########

@app.route("/sightings/home")
def sightings_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    sightings = Sighting.get_all()

    return render_template("home.html", user=user, sightings=sightings)

@app.route("/sightings/<int:sighting_id>")
def sighting_detail(sighting_id):
    user = User.get_by_id(session["user_id"])
    sighting = Sighting.get_by_id(sighting_id)
    return render_template("sighting_detail.html", user=user, sighting=sighting)

@app.route("/sightings/create")
def recipe_create_page():
    return render_template("create_sighting.html")

@app.route("/sightings/edit/<int:sighting_id>")
def recipe_edit_page(sighting_id):
    sighting = Sighting.get_by_id(sighting_id)
    return render_template("edit_sighting.html", sighting=sighting)

######## POST and ACTION METHODS ########

@app.route("/sightings", methods=["POST"])
def create_sighting():
    valid_sighting = Sighting.create_valid_sighting(request.form)
    if valid_sighting:
        return redirect(f'/sightings/{valid_sighting.id}')
    return redirect('/sightings/create')

@app.route("/sightings/<int:sighting_id>", methods=["POST"])
def update_sighting(sighting_id):

    valid_sighting = Sighting.update_sighting(request.form, session["user_id"])

    if not valid_sighting:
        return redirect(f"/sightings/edit/{sighting_id}")
        
    return redirect(f"/sightings/{sighting_id}")

@app.route("/sightings/delete/<int:sighting_id>")
def delete_by_id(sighting_id):
    Sighting.delete_sighting_by_id(sighting_id)
    return redirect("/sightings/home")