from flask import Flask, request, jsonify, render_template
import joblib
# added: builds the passenger table in the same shape the model was trained on
import pandas as pd
# added: lets us save each submission into a small local database
import sqlite3
# added: matches typed self-describe gender text against a safe list, allows for typos
import difflib
# added: timestamps every submission we log
from datetime import datetime

# Loade model into file
file = joblib.load('titanic_model.pkl')
titanicModel = file
print("Number of features the model wants:", file.n_features_in_)

# Create application object (server)
app = Flask(__name__)  # tells flask to search in current script

# NEW: terms we'll accept in the self-describe gender box, keeps out junk like "chicken"
VALID_GENDER_TERMS = [
  "non-binary", "nonbinary", "genderfluid", "genderqueer", "agender",
  "trans man", "trans woman", "transgender", "two-spirit", "bigender",
  "demiboy", "demigirl", "androgynous", "questioning",
]

# NEW: matches typed text against the list above, allows for small typos
def checkSelfDescribedGender(typedText):
  if not typedText:
    return None
  typedText = typedText.strip().lower()
  matches = difflib.get_close_matches(typedText, VALID_GENDER_TERMS, n=1, cutoff=0.75)
  return matches[0] if matches else None

# NEW: works out the label to save and the number the model should see
# the model only ever saw 0/1 so non-binary and self-describe fall back to 0
def getGenderInfo(sexChoice, selfDescribedText):
  if sexChoice == 1:
    return "Female", 1
  elif sexChoice == 2:
    return "Non-binary", 0
  elif sexChoice == 3:
    matched = checkSelfDescribedGender(selfDescribedText)
    return (matched if matched else "Prefer not to say"), 0
  else:
    return "Male", 0

# NEW: same age buckets used in the notebook
def getAgeGroup(age):
  if age <= 4:
    return 1
  elif age <= 12:
    return 2
  elif age <= 15:
    return 3
  elif age <= 19:
    return 4
  elif age <= 39:
    return 5
  elif age <= 49:
    return 6
  else:
    return 7

# NEW/FIXED: travel comfort -> Pclass was backwards before
# "rough it to save money" was sending Pclass 1 (first class), the opposite of what it means
def getPclass(travelComfort):
  return 4 - travelComfort

# NEW: reverse lookup so age group numbers turn into readable chart labels
AGE_GROUP_LABELS = {
  0: "Unknown", 1: "Infant", 2: "Child", 3: "Young",
  4: "Teenager", 5: "Adult", 6: "Middle Aged", 7: "Senior",
}

# NEW: survival rates from the real historical Titanic data, grouped a few ways
# this never changes since titanic-data-train.csv never changes
def computeRealDataStats():
  train = pd.read_csv('titanic-data-train.csv')
  byClass = (train.groupby('Pclass')['Survived'].mean() * 100).round(1)
  bySex = (train.groupby('Sex')['Survived'].mean() * 100).round(1)
  train['AgeGroup'] = train['Age'].fillna(-1).apply(getAgeGroup)
  byAge = (train.groupby('AgeGroup')['Survived'].mean() * 100).round(1)
  return {
    'byClass': {f'Class {k}': v for k, v in byClass.items()},
    'bySex': {k.capitalize(): v for k, v in bySex.items()},
    'byAge': {AGE_GROUP_LABELS.get(k, 'Unknown'): v for k, v in byAge.items()},
  }

# NEW: same three groupings, but from everyone who has used the site so far
# uses predicted survival since we don't know a real outcome for these
def computeNewDataStats():
  conn = sqlite3.connect('submissions.db')
  submissions = pd.read_sql('SELECT * FROM submissions', conn)
  conn.close()
  if submissions.empty:
    return None
  byClass = (submissions.groupby('pclass')['prediction'].mean() * 100).round(1)
  byGender = (submissions.groupby('gender_label')['prediction'].mean() * 100).round(1)
  submissions['ageGroup'] = submissions['age'].apply(getAgeGroup)
  byAge = (submissions.groupby('ageGroup')['prediction'].mean() * 100).round(1)
  return {
    'byClass': {f'Class {k}': v for k, v in byClass.items()},
    'bySex': {k: v for k, v in byGender.items()},
    'byAge': {AGE_GROUP_LABELS.get(k, 'Unknown'): v for k, v in byAge.items()},
    'totalSubmissions': len(submissions),
  }

# NEW: sets up submissions.db if it doesn't exist yet, separate from our training data
def initDb():
  conn = sqlite3.connect('submissions.db')
  conn.execute('''
    CREATE TABLE IF NOT EXISTS submissions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT,
      gender_label TEXT,
      age INTEGER,
      pclass INTEGER,
      sibsp INTEGER,
      parch INTEGER,
      title INTEGER,
      prediction INTEGER,
      timestamp TEXT
    )
  ''')
  conn.commit()
  conn.close()

# NEW: saves one submission
def logSubmission(name, genderLabel, age, pclass, sibsp, parch, title, prediction):
  conn = sqlite3.connect('submissions.db')
  conn.execute('''
    INSERT INTO submissions
      (name, gender_label, age, pclass, sibsp, parch, title, prediction, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  ''', (name, genderLabel, age, pclass, sibsp, parch, title, prediction, datetime.now().isoformat()))
  conn.commit()
  conn.close()

initDb()  # NEW: run once on startup

# Start flask and open in browser on port 5000
@app.route('/')
def home():
  return render_template('index.html')  # Sends file to browser for display

# Catching JSON data sent by JS
@app.route('/predict', methods=['POST'])  # Function only triggers if data packet is actively being sent
def predict_survival():
  data = request.get_json()  # Parses raw JS into python dictionary
  name = data.get('name')

  # ORIGINAL:
  # sex = data.get('sex')
  # CHANGED: added genderSelf so self describe answers actually get read,
  # and int()/defaults everywhere below since form data was coming in unconverted
  sexChoice = data.get('sex')
  selfDescribedText = data.get('genderSelf', '')
  age = int(data.get('age', 0))
  title = int(data.get('title', 1))
  travelComfort = int(data.get('travel-comfort', 2))
  siblings = int(data.get('sib', 0))
  parents = int(data.get('pa', 0))
  spouses = int(data.get('sp', 0))
  children = int(data.get('ch', 0))
  SibSp = siblings + spouses
  ParCh = parents + children

  # NEW: figure out gender label + model input, age group, and pclass (fixed direction)
  genderLabel, modelSex = getGenderInfo(sexChoice, selfDescribedText)
  ageGroup = getAgeGroup(age)
  pclass = getPclass(travelComfort)

  fareMap = {1: 100, 2: 35, 3: 12}  # NEW: rough fare estimate based on class
  fare = fareMap.get(pclass, 30)

  # NEW: builds the passenger row in the same shape/order the model was trained on
  passenger = pd.DataFrame({
    'Pclass': [pclass], 'Sex': [modelSex], 'Age': [ageGroup],
    'SibSp': [SibSp], 'Parch': [ParCh], 'Fare': [fare],
    'Embarked': [1], 'Title': [title],
  })

  # ORIGINAL:
  # prediction_array = file.predict([[]])
  # CHANGED: this was predicting on an empty list, which is why it never
  # actually worked - now it predicts on the real passenger row above
  prediction_array = file.predict(passenger)
  prediction = int(prediction_array[0])

  # NEW: saves this submission so our dataset grows over time
  logSubmission(name, genderLabel, age, pclass, SibSp, ParCh, title, prediction)

  # ORIGINAL:
  # return jsonify({'Status':'Received'}) # Web Browser needs valid return statement - without it function would've returned 'None'
  # CHANGED: now sends back the actual prediction instead of a placeholder
  return jsonify({
    'prediction': prediction,
    'outcome': 'SURVIVED' if prediction == 1 else 'DID NOT SURVIVE',
    'gender_label': genderLabel,
  })

# NEW: sends both sets of survival stats to the front end for the charts
@app.route('/stats')
def get_stats():
  return jsonify({
    'realData': computeRealDataStats(),
    'newData': computeNewDataStats(),
  })

# Start web engine and listen to internet traffic
if __name__ == '__main__':
    app.run(debug=True)