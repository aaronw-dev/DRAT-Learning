from flask import Flask, render_template, request, jsonify
import firebase_admin
import requests

def AddUser(email,password):
    details={
        'email':email,
        'password':password,
        'returnSecureToken': True
    }
    # send post request
    r=requests.post('https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={}'.format(firebasekey),data=details)
    #check for errors in result
    if 'error' in r.json().keys():
      return {'status':'error','message':r.json()['error']['message']}
    #if the registration succeeded
    if 'idToken' in r.json().keys() :
      return {'status':'success'}
      
# Import Flask Class, and render_template
app = Flask(__name__) # Create an Instance

firebasekey = "AIzaSyBWKGsWsKhnGNjjOEcbXMMCE-lsjYhf83w"

@app.route('/')
def homepage():
  return render_template('index.html')

@app.route("/signup", methods=['GET', 'POST'])
def join():
  if request.method == 'GET':
    return render_template("signup.html")
  if request.method == 'POST':
    inputemail = request.form['email'] 
    inputpassword = request.form['password']
    print(AddUser(inputemail, inputpassword))
    return render_template('signed-up.html')

@app.errorhandler(500)
def fivehundrederror(error):
  return "Server Error!"
  #return render_template("error.html", errorcode = error)
  
@app.errorhandler(404)
def invalid_route(error):
  return "404 Error"
  #return render_template("error.html")
app.run(host='0.0.0.0', port=5000, debug=False)