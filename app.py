from flask import Flask, request, jsonify
from simple_forecaster import forecast  # or adjust this based on your file
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "CocoMerch Forecast API is running!"

@app.route('/forecast', methods=['POST'])
def get_forecast():
    data = request.get_json()
    # Example: expect {"sales": [100, 120, 130]} or your actual format
    result = forecast(data)
    return jsonify({"forecast_result": result})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
