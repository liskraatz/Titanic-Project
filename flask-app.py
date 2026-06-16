from flask import Flask, request, jsonify
import joblib

# Loading model into file
file = joblib.load('titanic_model.pkl') 
titanicModel = file

# Creating application object (server)
app = Flask(__name__) # tells flask to search in current script


















