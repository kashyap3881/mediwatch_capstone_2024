from flask import Flask, request, jsonify, render_template
import os
from flask_cors import CORS, cross_origin
from continuous_training.airflow_local.src.lib.utils import decodeCSV
from continuous_training.airflow_local.src.model_inference.predict import DiabetesReadmissionPredictor
# from continuous_training.airflow_local.src.model_training.train import DiabetesReadmissionTrainer
# from continuous_training.airflow_local.src.lib.utils import trigger_dag
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
        self.filename = "test_data.csv"
        self.predictor = DiabetesReadmissionPredictor(self.filename, os.path.join(os.getcwd(), "continuous_training/airflow_local/src/models/best_model"))
        # self.trainer = DiabetesReadmissionTrainer(os.path.join(os.getcwd(), "src/input_data/dataset_diabetes/diabetic_data.csv"), 
        #                                           self.filename, 
        #                                           os.path.join(os.getcwd(), "src/models"))

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
    result = client_app.predictor.prediction_diabetes_readmission()
    # Ensure the result is in the correct format
    formatted_result = {
        "Hospital Readmission Prediction": result[0]["Hospital Readmission Prediction"]
    }
    return jsonify(formatted_result)


# @app.route("/train", methods=['POST'])
# @cross_origin()
# def trainRoute():
#     csv_data = request.json['csv']
#     client_app = ClientApp()
#     decodeCSV(csv_data, client_app.filename)
#     result = client_app.trainer.train_and_evaluate_model()
#     # Ensure the result is in the correct format
#     # Format the result
#     formatted_result = {
#         "Hospital Readmission Training": {
#             "Best Model": result['best_model_name'],
#             "Train Accuracy": result['best_model_train_accuracy'],
#             "Test Accuracy": result['best_model_test_accuracy']
#         }
#     }
#     return jsonify(formatted_result)

# @app.route("/dag", methods=['POST'])
# @cross_origin()
# def dagRoute():
#     csv_data = request.json['csv']
#     client_app = ClientApp()
#     decodeCSV(csv_data, client_app.filename)
    
#     # Trigger the DAG with the trainer object
#     dag_result = trigger_dag(client_app.trainer)
    
#     if dag_result:
#         return jsonify(dag_result), 200
#     else:
#         return jsonify({"error": "Failed to trigger DAG or retrieve results"}), 500


#port = int(os.getenv("PORT"))
if __name__ == "__main__":
    clApp = ClientApp()
    #app.run(host='0.0.0.0', port=port)
    app.run(host='0.0.0.0', port=9003, debug=True)
