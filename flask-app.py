from flask import Flask, request, jsonify, render_template
import joblib

# Loade model into file
file = joblib.load('titanic_model.pkl') 
titanicModel = file

# Create application object (server)
app = Flask(__name__) # tells flask to search in current script

# Start flask and open in browser on port 5000
@app.route('/')
def home():
  return render_template('index.html') # Re
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
  return jsonify({'Status':'Received'}) # Web Browser needs valid return statement - without it function would've returned 'None'

# Start web engine and listen to internet traffic
if __name__ == '__main__':
    app.run(debug=True)


















