from flask import Flask, redirect, url_for, render_template, request, jsonify
from flask_pymongo import PyMongo
import pickle
import numpy as np
import time

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://admin:Password1@flask-test.p39lo.mongodb.net/test_database?retryWrites=true&w=majority"
mongo = PyMongo(app)
model = pickle.load(open('model.pkl', 'rb'))

global loggedIn
global formFilled
global formdata
loggedIn = False
formFilled = False
formdata = {}

user_collection = mongo.db.test_collection


@app.route("/")
def home():
    if not loggedIn:
        return redirect(url_for("login"))
    elif not formFilled:
        return redirect(url_for("form"))
    else:
        formattedName = formdata['fname'] + " " + formdata['lname']
        fname = formdata['fname']
        lname = formdata['lname']
        age = formdata['age']
        city = formdata['city']
        state = formdata['state']
        score = formdata['score']
        return render_template("index.html", fname=fname, lname=lname, age=age, city=city, state=state, score=score)


@app.route("/login", methods=['GET', 'POST'])
def login():
    global loggedIn
    if request.method == 'POST':
        credentials = request.form.to_dict()
        if credentials['loginId'] == 'Nithin' and credentials['password'] == "pass":
            loggedIn = True
            if formFilled:
                return redirect(url_for("home"))
            else:
                return redirect(url_for("form"))
        else:
            return render_template("login.html", incorrect="Incorrect ID or password")
    else:
        if not loggedIn:
            return render_template("login.html")
        elif not formFilled:
            return redirect(url_for("form"))
        else:
            return redirect(url_for("home"))


@app.route("/form", methods=['GET', 'POST'])
def form():
    if request.method == 'GET':
        if not loggedIn:
            return redirect(url_for("login"))
        elif formFilled:
            return redirect(url_for("home"))
    return render_template("form.html")


@app.route("/predict", methods=['POST'])
def predict():
    global formFilled
    global formdata
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
        formdata['score'] = output
        formdata['time'] = timeNow
        user_collection.insert_one(formdata)
        formFilled = True
    return redirect(url_for("home"))


@app.route("/signout")
def signout():
    global loggedIn
    loggedIn = False
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
