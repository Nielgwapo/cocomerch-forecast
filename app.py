from flask import Flask, request, jsonify
from flask_cors import CORS
from simple_forecaster import SimpleForecastController  # Import the correct class
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/')
def home():
    return "CocoMerch Forecast API is running!"

@app.route('/forecast', methods=['POST'])
def get_forecast():
    try:
        data = request.get_json()
        product_name = data.get("product_name")
        product_id = data.get("product_id")
        months = data.get("months", 3)

        controller = SimpleForecastController()
        result = controller.generate_forecast(product_name, months, product_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    # Render requires the app to listen on all interfaces, port 10000
    app.run(host='0.0.0.0', port=10000)
