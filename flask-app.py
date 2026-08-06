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
  return render_template('index.html') # Sends file to browser for display

# Catching JSON data sent by JS


@app.route('/predict', methods=['POST']) # Function only triggers if data packet is actively being sent
def predict_survival():
  data = request.get_json() # Parses raw JS into python dictionary 
  name = data.get('name')
  sex = int(data.get('sex'))
  age = int(data.get('age'))
  title = int(data.get('title', 1)) # Add default to prevent crashing
  if age < 13:
      if sex == 0:
        title = 4
      elif sex == 1:
        title = 2
  
  travelComfort = int(data.get('travel-comfort'))
  siblings = int(data.get('sib'))
  parents = int(data.get('pa'))
  spouses = int(data.get('sp'))
  children = int(data.get('ch'))
  SibSp = siblings + spouses
  ParCh = parents + children


  passenger_features = [[travelComfort, sex, age, SibSp, ParCh, title]] # 2 dimensional -> expects outer [] for table, inner [] for rows

  print("Incoming array to model:", passenger_features)
  prediction_array = file.predict(passenger_features)
  # Result array
  prediction_array = file.predict(passenger_features)

  # Prediction result
  outcome = prediction_array[0] # result is 0 or 1
  if int(outcome) == 1:
     predictionMsg = 'Congratualtions, ' + name + ' you survived.'
  elif int(outcome) == 0:
     predictionMsg = 'Sorry, ' + name + ' you died.'

  # Return data to JS
  return jsonify({'outcome':int(outcome), 'message':predictionMsg}) # Web Browser needs valid return statement - without it function would've returned 'None'

# Start web engine and listen to internet traffic
if __name__ == '__main__':
    app.run(debug=True)


















