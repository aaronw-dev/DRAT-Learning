from flask import Flask, render_template, request, redirect, Markup
import firebase_admin
from firebase_admin import credentials, auth, firestore, exceptions
import requests
import json
from time import sleep
import flagimportant
import searchalgorithm
import sendemail
from bs4 import BeautifulSoup as soup
from urllib.request import urlopen

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

def VerifyEmail(idToken):
    verificationlink = "https://drat-learning.aw-dev.repl.co/verify/" + idToken
    user = auth.get_user(idToken)
    emailbody = "Hello, " + user.display_name + ", \n" + "Please verify your email address for DRAT: \n" + str(
        verificationlink)
    sendemail.sendEmail(user.email, "Your verification link for DRAT", emailbody)


def AddUser(email, password, username):
  try:
    res = auth.create_user(
      email=email,
      password=password,
      display_name=username)
    userid = auth.get_user_by_email(email)
    VerifyEmail(userid.uid)
  except Exception as error:
    return str(error)

def DisplayByteCards(uid, name):
  return db.collection("users").document(uid).collection("research").document(name).get().to_dict()["List"]

# Import Flask Class, and render_template

app = Flask(__name__)  # Create an Instance
cred = credentials.Certificate("credentials.json")
firebase_admin.initialize_app(cred)
firebasekey = "AIzaSyBWKGsWsKhnGNjjOEcbXMMCE-lsjYhf83w"
db = firestore.client()


@app.route('/')
def homepage():
  return render_template('index.html')

@app.route('/getbyte', methods=['GET', 'POST'])
def getbyte():
  if request.method == "GET":
    return redirect("https://drat-learning.aw-dev.repl.co")
  uid = request.form['uid']
  name = request.form['name']
  return ",".join(DisplayByteCards(uid, name))

def getresults(query):
  return searchalgorithm.search(query)

@app.route('/addresearch', methods=['GET', 'POST'])
def addresearch():
  if request.method == "GET":
    return redirect("https://drat-learning.aw-dev.repl.co")
  collection = getresults(request.form['query'])
  uid = request.form['uid']
  name = request.form['name']
  returnlist = ""
  for item in collection["items"][0:1]:
    #open result item's associated link
    wikidata = urlopen(item["link"])
    #read data from DAT EPIC LINK
    wikihtml = wikidata.read()
    #close read stream
    wikidata.close()
    #get JUST text from website
    pagesoup = soup(wikihtml, "html.parser").get_text()
    returnlist += pagesoup
  flaggedlist = flagimportant.flag(returnlist[0:10000])["output"].split("\n")
  db.collection('users').document(uid).collection('research').document(name).set({"List":flaggedlist, "name":name})
  sleep(1000)
  return redirect("https://drat-learning.aw-dev.repl.co/dashboard")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html", message="")
    if request.method == 'POST':
      authem = request.form['email']
      authpw = request.form['password']
      payload={
        "email":authem,
        "password" : authpw,
      }
      res = requests.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=" + firebasekey, data=payload).json()
      if("error" in res):
        error = res["error"]["message"]
        if error == "INVALID_PASSWORD":
          return render_template("login.html", message="Password not valid. Try again.")
        if error == "EMAIL_NOT_FOUND":
          return render_template("login.html", message="Email not valid. Try again.")
      if auth.get_user_by_email(authem).email_verified == False:
        return render_template("login.html", message="Email not verified; Please check your email for a verification link.")
        #return "Email not verified!"
      data = {"uid": auth.get_user_by_email(authem).uid}
      return render_template("dashboard.html", data=data)

@app.route("/getdashboard", methods=['GET', 'POST'])
def getdash():
    if request.method == "GET":
        return redirect("https://drat-learning.aw-dev.repl.co")
    #get list of users
    userid = request.form["uid"]
    information = db.collection("users").document(userid).collection(
        "research").get()
    returninfo = []
    for info in information:
        returninfo.append(str(info.to_dict()["name"]))
    return str(returninfo)


@app.route("/resetpassword", methods=['GET', 'POST'])
def resetpassword():
    if request.method == "GET":
        return render_template("resetpassword.html")
    email = request.form["email"]
    verificationlink = auth.generate_password_reset_link(email)
    user = auth.get_user_by_email(email)
    emailbody = "Hello, " + user.display_name + ", \n" + "Your Passoword Reset has arrived: \n" + str(
        verificationlink)
    sendemail.sendEmail(user.email, "Your password reset link for DRAT",
                        emailbody)
    return redirect("https://drat-learning.aw-dev.repl.co/")


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'GET':
        return render_template("signup.html")
    if request.method == 'POST':
        inputemail = request.form['email']
        inputpassword = request.form['password']
        inputusername = request.form['username']
        addresult = AddUser(inputemail, inputpassword, inputusername)
        data = {
            "username": inputusername,
            "uid": auth.get_user_by_email(inputemail).uid
        }
        user = auth.get_user_by_email(inputemail)
        db.collection('users').document(user.uid).set(data)
        return redirect("https://drat-learning.aw-dev.repl.co/login")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route('/verify/<uid>')
def verify(uid):
    auth.update_user(uid, email_verified=True)
    return str(auth.get_user(uid).email_verified) + '''
  <script>
    window.open('','_self').close();
  </script>
  '''


@app.errorhandler(500)
def fivehundrederror(error):
  #return "Server Error: " + str(error)
  return render_template("errorpage.html", errorcode = error)


@app.errorhandler(404)
def invalid_route(error):
    #return "404 Error: Resource not found."
    return render_template("errorpage.html", errorcode=Markup("404 Error: <br> Resource not found."))

@app.errorhandler(403)
def forbidden(error):
    return redirect("https://drat-learning.aw-dev.repl.co/")
    #return render_template("errorpage.html")
  
app.run(host='0.0.0.0', port=5000, debug=False)
