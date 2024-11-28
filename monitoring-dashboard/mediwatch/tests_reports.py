import os
import sys
# Add the root directory of your project to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
from continuous_training.airflow_local.src.model_inference.predict import DiabetesReadmissionPredictor
from continuous_training.airflow_local.src.data_cleaning.clean import clean
from continuous_training.airflow_local.src.lib.utils import get_reference_data, get_report, compare_dataframe_features
from continuous_training.airflow_local.src.lib.utils import get_test_suite
from evidently.ui.workspace import Workspace
from evidently import ColumnMapping
from continuous_training.airflow_local.src.data_cleaning.common import get_numeric_features, get_categorical_features
import dagconfig as cfg

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def trigger_dag(original_data_filename, new_data_filename, model_dir):

    parameters = {
        "conf": {
            "original_data_filename": original_data_filename,
            "new_data_filename": new_data_filename,
            "model_dir": model_dir
            # "bucket_name": cfg.BUCKET_NAME
        }
    }   

    # Send an authenticated HTTP POST request to trigger the DAG
    response = requests.post(cfg.AIRFLOW_API_URL, json=parameters, auth=HTTPBasicAuth(cfg.AIRFLOW_USERNAME, cfg.AIRFLOW_PASSWORD))

    # Check the response to see if the DAG was triggered successfully
    if response.status_code == 200:
        print("DAG has been triggered successfully.")
    else:
        print(f"Error: Failed to trigger the DAG. Status code: {response.status_code}")
        print(f"Errror: \n {response.text}")

def create_column_mapping(data, target_column, prediction_column):
    numeric_features = get_numeric_features(data, col_exclude = [target_column, prediction_column])
    categorical_features = get_categorical_features(data, col_exclude = [target_column, prediction_column])
    
    column_mapping = ColumnMapping(
        target=target_column,
        prediction=prediction_column,
        numerical_features=numeric_features,
        categorical_features=categorical_features
    )
    
    return column_mapping

def get_test_summary(tests_results):

    # False for failed and True for passed
    test_summary = []
    logger.info("Getting test summary: False for failed and True for passed")
    for result in tests_results:
        if result['status'] == 'SUCCESS':
            test_summary.append(True)
        else:
            test_summary.append(False)

    return test_summary

def main():
    # Intialize the predictor for new data
    print("Create Diabetes Readmission Predictor Object ........")
    predictor = DiabetesReadmissionPredictor(cfg.NEW_DATA_PATH, cfg.MODEL_PATH)

    # Make predictions on new data
    print("Run prediction ...........")
    result = predictor.prediction_diabetes_readmission()

    # Load the CSV file you want to make predictions on
    print(f"Loading new data from: {cfg.NEW_DATA_PATH}")
    new_data = pd.read_csv(cfg.NEW_DATA_PATH)

    # Check if the prediction was successful
    if "Hospital Readmission Prediction" in result[0]:
        predictions = result[0]["Hospital Readmission Prediction"]
        
        # Create a dictionary mapping patient_id to predicted_readmitted
        prediction_dict = {item['patient_id']: item['predicted_readmitted'] for item in predictions}
        
        # Add the predictions as a new column
        new_data['Predicted_readmitted'] = new_data['patient_nbr'].map(prediction_dict)
        
        print("Predictions added to new_data DataFrame.")
    else:
        print("Error: Prediction failed. Unable to add predictions to new_data. Cannot proceed ahead...")
        sys.exit(1)
    
    # Save the new data with predictions
    new_data_with_pred_filename = os.path.join(os.getcwd(), 'new_data_with_predictions.csv')
    new_data.to_csv(new_data_with_pred_filename, index=False)
    print(f"New data with predictions saved to: {new_data_with_pred_filename}")
    

    # Clean new data to include features we used for training and inference
    # Mapping of readmitted is also achieved
    print("Invoking cleaning module to clean new data and leave only features used for training and inference ..........")
    cleanObj = clean(new_data_with_pred_filename)
    new_data_with_pred = cleanObj.clean_data()

    # Create the column mapping for Evidently, this depends on what exactly was used for training and prediction
    target_column = "readmitted"
    prediction_column = "Predicted_readmitted"

    # Create the column mapping
    column_mapping = create_column_mapping(new_data_with_pred, target_column, prediction_column)
    
    # Print the column mapping to verify
    print("Column Mapping: Target:", column_mapping.target)
    print("Column Mapping: Prediction:", column_mapping.prediction)
    print("Column Mapping: Numerical Features:", column_mapping.numerical_features)
    print("Column Mapping: Categorical Features:", column_mapping.categorical_features)


    # Returns the original created workspace if it exists already
    ws = Workspace.create(cfg.WORKSACE_PATH)

    existing_projects = ws.search_project(project_name=cfg.PROJECT_NAME)
    project = existing_projects[0]
    
    # Reference data is the original training data training data with predicted_readmitted
    reference_data = get_reference_data(cfg.TRAINING_DATA_PATH)

    if reference_data is None:
        print("Error: Reference data not found. Please provide a valid reference data path.")
        sys.exit(1)

    # Both reference data and new data are cleaned and have the same features
    print("Comparing reference data and new data features to ensure they are the same.")
    result = compare_dataframe_features(reference_data, new_data_with_pred)
    
    if result:
        print("The original and new data could be used to generate Evidently reports ... Proceeding ...")
    else:
        print("Error: Please address the differences in the datasets before proceeding.....")
        sys.exit(1)

    report = get_report(reference_data, new_data_with_pred, column_mapping=column_mapping)
    ws.add_report(project.id, report)

    test_suite = get_test_suite(reference_data, new_data_with_pred, column_mapping)
    ws.add_test_suite(project.id, test_suite)


    test_summary = get_test_summary(test_suite.as_dict()['tests'])

    print(f"Test summary:--------------\n {test_summary}")
    print(f"Tests: {test_suite.as_dict()['tests']}")

    if not all(test_summary):
        print("Error: One or more tests failed. Triggering model retraining...")
        trigger_dag(cfg.TRAINING_DATA_PATH, cfg.NEW_DATA_PATH, cfg.MODEL_PATH)

    else:
        print("All tests have passed. Not retraining the model.")

if __name__ == '__main__':
    main()