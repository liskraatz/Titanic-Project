from flask import Flask, request, jsonify
import joblib

# Loading model into file
file = joblib.load('titanic_model.pkl') 
titanicModel = file

# Creating application object (server)
app = Flask(__name__) # tells flask to search in current script

# Catching JSON data sent by JS
@app.route('/predict', methods=['POST']) # 
def predict_survival():
  data = request.get_json()
  name = data.get('name')
  sex = data.get('sex')
  age = data.get('age')
  print(age)
  title = data.get('title')
  travelComfort = data.get('travel-comfort')
  siblings = data.get('sib')
  parents = data.get('pa')
  spouses = data.get('sp')
  children = data.get('ch')
  jsonify({'Status':'Received'}) # Web Browser needs valid return statement - without it function would've returned 'None'
  




















