from flask import Flask, request, jsonify, render_template
import joblib

# Loade model into file
file = joblib.load('titanic_model.pkl') 
titanicModel = file
print("Number of features the model wants:", file.n_features_in_)

# Create application object (server)
app = Flask(__name__) # tells flask to search in current script

# Start flask and open in browser on port 5000
@app.route('/')
def home():
  return render_template('index.html') # Sends file to browser for display

# Catching JSON data sent by JS
@app.route('/predict', methods=['POST']) # Function only triggers if data packet is actively being sent
def predict_survival():
  data = request.get_json() # Parses raw JS into python dictionary 
  name = data.get('name')
  sex = data.get('sex')
  age = data.get('age')
  title = data.get('title')
  travelComfort = data.get('travel-comfort')
  siblings = data.get('sib')
  parents = data.get('pa')
  spouses = data.get('sp')
  children = data.get('ch')
  SibSp = siblings + spouses
  ParCh = parents + children

  prediction_array = file.predict([[]])
  return jsonify({'Status':'Received'}) # Web Browser needs valid return statement - without it function would've returned 'None'

# Start web engine and listen to internet traffic
if __name__ == '__main__':
    app.run(debug=True)


















