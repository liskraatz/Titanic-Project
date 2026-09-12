from flask import Flask, request, jsonify, render_template
import joblib
import pandas as pd

# Loade model into file
file = joblib.load('titanic_model.pkl') 
titanicModel = file

# pre load the training data once to compute the stats for the graphs
train = pd.read_csv('titanic-data-train.csv')
train['FamilySize'] = train['SibSp'] + train['Parch'] 

# normalizing the coloumn for sex if male/female text
if train['Sex'].dtype == 'object':
    train['Sex'] = train['Sex'].map({'male': 0, 'female': 1})

def get_age_group(age):
    if age < 13:
        return 'Child'
    elif age < 20:
        return 'Teenager'
    elif age < 60:
        return 'Adult'
    else:
        return 'Senior'
    
train['AgeGroup'] = train['Age'].apply(lambda a: get_age_group(a) if pd.notna(a) else None)

# Create application object (server)
app = Flask(__name__) # tells flask to search in current script

# Start flask and open in browser on port 5000
@app.route('/')
def home():
  return render_template('index.html') # Sends file to browser for display

# sends the survival rate stats for the graphs
@app.route('/stats', methods=['GET'])
def get_stats():
  class_stats = (train.groupby('Pclass')['Survived'].mean() * 100).round(1).to_dict()
  sex_stats = (train.groupby('Sex')['Survived'].mean() * 100).round(1).to_dict()

  age_order = ['Child', 'Teenager', 'Adult', 'Senior']
  age_stats_raw = (train.groupby('AgeGroup')['Survived'].mean() * 100).round(1).to_dict()
  age_stats = {}
  for group in age_order:
    age_stats[group] = age_stats_raw.get(group, 0)

  family_stats_raw = (train.groupby('FamilySize')['Survived'].mean() * 100).round(1).to_dict()
  family_stats = {}
  for size, rate in family_stats_raw.items():
    if size <= 6:
      family_stats[str(size)] = rate

  return jsonify({
    'class': {'1': class_stats.get(1, 0), '2': class_stats.get(2, 0), '3': class_stats.get(3, 0)},
    'sex': {'male': sex_stats.get(0, 0), 'female': sex_stats.get(1, 0)},
    'ageGroup': age_stats,
    'familySize': family_stats
  })

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

  # not expecting anyone under 18 with kids for demo
  if age < 18:
    children = 0

  SibSp = siblings + spouses
  ParCh = parents + children

  # sex = 2 means "other" was picked, this is just now taking into consideration that option
  # since the model cant predict the other, we will run it once as male and once as female and show both
  if sex == 2:
    male_features = [[travelComfort, 0, age, SibSp, ParCh, title]]
    female_features = [[travelComfort, 1, age, SibSp, ParCh, title]]

    male_outcome = int(file.predict(male_features)[0])
    female_outcome = int(file.predict(female_features)[0])

    male_word = 'survived' if male_outcome == 1 else 'died'
    female_word = 'survived' if female_outcome == 1 else 'died'

    predictionMsg = (name + ', explain why we chose to use both male and female here with better explanation below ' + female_word + '.')

    return jsonify({
      'isOther': True,
      'maleOutcome': male_outcome,
      'femaleOutcome': female_outcome,
      'message': predictionMsg,
      'userStats': {
        'pclass': travelComfort,
        'ageGroup': get_age_group(age),
        'familySize': min(SibSp + ParCh, 6)
      }
    })

  # normal case, sex is male or female
  passenger_features = [[travelComfort, sex, age, SibSp, ParCh, title]]
  prediction_array = file.predict(passenger_features)
  outcome = int(prediction_array[0])

  if outcome == 1:
     predictionMsg = 'Congratualtions, ' + name + ' you survived.'
  else:
     predictionMsg = 'Sorry, ' + name + ' you died.'

  return jsonify({
    'isOther': False,
    'outcome': outcome,
    'message': predictionMsg,
    'userStats': {
      'pclass': travelComfort,
      'sex': 'female' if sex == 1 else 'male',
      'ageGroup': get_age_group(age),
      'familySize': min(SibSp + ParCh, 6)
    }
  })


# Start web engine and listen to internet traffic
if __name__ == '__main__':
    app.run(debug=True)
