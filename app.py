from flask import Flask, redirect, url_for, render_template, request, session, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
import pickle
import numpy as np
import time

app = Flask(__name__)
app.secret_key = "abc"
app.config["MONGO_URI"] = "mongodb+srv://admin:Password1@flask-test.p39lo.mongodb.net/test_database?retryWrites=true&w=majority"
mongo = PyMongo(app)
model = pickle.load(open('model.pkl', 'rb'))


user_collection = mongo.db.test_collection


@app.route("/")
def home():
    if not 'loggedIn' in session:
        return redirect(url_for("login"))
    elif session['privileges'] == 'user':
        if session["formFilled"] == False:
            return redirect(url_for("form"))
        else:
            user = user_collection.find_one(
                ({'aadhar_number': session['aadhar_number']}))
            return render_template("index.html", user=user)
    elif session['privileges'] == 'admin':
        users = user_collection.find().sort([("score", -1)])
        numUsers = user_collection.count_documents({})
        return render_template("admin.html", users=users, numUsers=numUsers)


@app.route("/passport")
def passport():
    if not 'loggedIn' in session:
        return redirect(url_for("login"))
    elif session['privileges'] == 'admin':
        return redirect(url_for("home"))
    elif session['formFilled'] == False:
        return redirect(url_for("form"))
    else:
        user = user_collection.find_one(
            ({'aadhar_number': session['aadhar_number']}))
        if user['status'] == True:
            return render_template("passport.html", user=user)
        else:
            return redirect(url_for("home"))


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        credentials = request.form.to_dict()
        aadhar_number = credentials["aadhar_number"]
        phone_number = credentials["phone_number"]
        password = credentials["password"]
        existing_user = user_collection.find_one(
            ({"aadhar_number": aadhar_number}))
        if existing_user is None:
            user_collection.insert_one({"fname": None,
                                        "lname": None,
                                        "aadhar_number": aadhar_number,
                                        "phone_number": phone_number,
                                        "password": password,
                                        "form_filled": False,
                                        'age': None,
                                        'gender': None,
                                        "state": None,
                                        'city': None,
                                        'address': None,
                                        'job': None,
                                        "diabetes": None,
                                        'BP': None,
                                        "heart": None,
                                        "pregnant": None,
                                        "score": None,
                                        "status": False,
                                        "time": None})
            return redirect(url_for("login"))
        else:
            return render_template("signup.html", incorrect="User already exists")
    else:
        if not 'loggedIn' in session:
            return render_template("signup.html")
        elif session['formFilled'] == False:
            return redirect(url_for("form"))
        else:
            return redirect(url_for("home"))


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        credentials = request.form.to_dict()
        existing_user = user_collection.find_one(
            ({"aadhar_number": credentials['loginId']}))
        if credentials['loginId'] == 'admin' and credentials['password'] == "pass":
            session['loggedIn'] = True
            session['privileges'] = 'admin'
            return redirect(url_for("home"))
        else:
            if existing_user is None:
                return render_template("login.html", incorrect="Incorrect ID or password")
            else:
                if credentials['loginId'] == existing_user["aadhar_number"] and credentials['password'] == existing_user['password']:
                    session['loggedIn'] = True
                    session['privileges'] = 'user'
                    session['aadhar_number'] = existing_user['aadhar_number']
                    session['formFilled'] = existing_user['form_filled']
                    if session['formFilled'] == True:
                        return redirect(url_for("home"))
                    else:
                        return redirect(url_for("form"))
                else:
                    return render_template("login.html", incorrect="Incorrect ID or password")
    else:
        if not 'loggedIn' in session:
            return render_template("login.html")
        elif session['formFilled'] == False:
            return redirect(url_for("form"))
        else:
            return redirect(url_for("home"))


@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        if not 'loggedIn' in session:
            return redirect(url_for("login"))
        elif session['privileges'] == 'admin' or session['formFilled'] == True:
            return redirect(url_for("home"))
    return render_template("form.html")


@app.route("/predict", methods=['POST'])
def predict():
    if request.method == 'POST':
        req = request.form
        formdata = req.to_dict()
        diabete = float(req.get("diabetes"))
        blood_pressure = float(req.get("BP"))
        heart_disease = float(req.get("heart"))
        pregnants = float(req.get("pregnant"))

        int_features = (diabete, blood_pressure, heart_disease, pregnants)
        final_features = np.array(int_features, dtype=np.float32)
        final_features = [np.array(int_features)]

        prediction = model.predict(final_features)

        output = round(prediction[0], 2)
        timeNow = time.asctime(time.localtime(time.time()))
        user_collection.update_one({'aadhar_number': session['aadhar_number']},
                                   {'$set': {'fname': req.get("fname"),
                                             'lname': req.get("lname"),
                                             'age': req.get("age"),
                                             'gender': req.get("gender"),
                                             'state': req.get("state"),
                                             'city': req.get("city"),
                                             'address': req.get("address"),
                                             'job': req.get("job"),
                                             'diabetes': req.get("diabetes"),
                                             'BP': req.get("BP"),
                                             'heart': req.get("heart"),
                                             'pregnant': req.get("pregnant"),
                                             'score': output,
                                             'time': timeNow,
                                             'form_filled': True}})
        session['formFilled'] = True
    return redirect(url_for("home"))


@app.route("/update", methods=['POST'])
def update():
    user = user_collection.find_one({"_id": ObjectId(str(request.form['id']))})
    user['status'] = True
    user_collection.update_one({"_id": ObjectId(str(request.form['id']))}, {
                               '$set': {'status': True}})
    return jsonify({'result': 'success'})


@app.route("/signout")
def signout():
    session.pop('loggedIn', None)
    session.pop('privileges', None)
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
