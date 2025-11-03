from flask import Flask, request, jsonify
from flask_cors import CORS
from simple_forecaster import SimpleForecastController

app = Flask(__name__)
CORS(app)  # Allow all origins (InfinityFree can access it)

@app.route('/')
def home():
    return "CocoMerch Forecast API is running!"

@app.route('/forecast', methods=['POST'])
def get_forecast():
    try:
        data = request.get_json()
        if not data or "sales" not in data:
            return jsonify({"error": "Invalid data format. Expected key 'sales'."}), 400

        controller = SimpleForecastController()
        result = controller.generate_forecast_from_data(data["sales"])
        return jsonify({"forecast_result": result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
