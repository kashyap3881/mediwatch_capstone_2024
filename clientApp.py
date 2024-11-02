from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
from src.lib.utils import decodeCSV
from src.model_inference.predict import DiabetesReadmissionPredictor
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)


#@cross_origin()
class ClientApp:
    def __init__(self):
        self.filename = "test_prod__hlrLogLocationUpdateOTA__.csv"
        self.qpredictor = DiabetesReadmissionPredictor(self.filename, os.path.join(os.getcwd(), "src/models/best_model"))

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')


@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    csv_data = request.json['csv']
    client_app = ClientApp()
    decodeCSV(csv_data, client_app.filename)
    result = client_app.qpredictor.prediction_diabetes_readmission()
    # Ensure the result is in the correct format
    formatted_result = {
        "Hospital Readmission Prediction": result[0]["Hospital Readmission Prediction"]
    }
    return jsonify(formatted_result)


#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    clApp = ClientApp()
    #app.run(host='0.0.0.0', port=port)
    app.run(host='0.0.0.0', port=9003, debug=True)
