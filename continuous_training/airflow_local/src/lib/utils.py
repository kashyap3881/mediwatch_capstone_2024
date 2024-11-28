import base64
import pickle
import pandas as pd
from ..data_cleaning.clean import clean
from evidently.report import Report
from evidently.metrics import DatasetSummaryMetric, ColumnDistributionMetric
from evidently.metric_preset import ClassificationPreset
from evidently.test_suite import TestSuite
from evidently.tests import TestAccuracyScore, TestPrecisionByClass, TestColumnDrift
from ..data_cleaning.common import get_numeric_features, get_categorical_features

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def decodeCSV(csvstring, fileName):
    """
    Decode a base64-encoded CSV string and save it to a file.

    Args:
        csvstring (str): Base64-encoded CSV data
        fileName (str): Path where the decoded CSV should be saved

    The function decodes the base64 string to UTF-8 CSV format and saves it.
    Useful when receiving CSV data that has been encoded for transmission.
    """
    csvdata = base64.b64decode(csvstring).decode('utf-8')
    with open(fileName, 'w') as f:
        f.write(csvdata)
        f.close()
    logger.info(f"CSV file saved as: {fileName}")

def get_reference_data(training_data_path=None):

    """
    Returns the reference data to find drift against. In this case, we are using the training data as reference.
    """
    if training_data_path:
        #logger.info(f"Loading original reference data: {training_data_path}")
        #df = pd.read_csv(cfg.TRAINING_DATA_PATH)
        logger.info("Invoking cleaning module to clean original data and leave only features used for training and inference ..........")
        cleanObj = clean(training_data_path)
        df = cleanObj.clean_data()
        df['Predicted_readmitted'] = df['readmitted']
        return df
    else:
        logger.error("Training data path is not provided.")
        return None

def get_report(reference_data, new_data, column_mapping):

    """
    Creates a report with DatasetSummaryMetric, ColumnDistributionMetric, ColumnDriftMetric, ClassificationPreset, ColumnMissingValuesMetric
    """

    # Exit if no new predictions were made since the last reported batch
    total_new_records = new_data.shape[0]

    if total_new_records == 0:
        logger.info("No new predictions made by the model. Exiting...")
        exit()

    logger.info(f"{total_new_records} new predictions done by the model. Reporting the same.")

    data_drift_report = Report(
        metrics=[
            # Generates a table of Summary of the Dataset (similar to how pandas generates one)
            DatasetSummaryMetric(),

            # Generates how many predictions were made for each class
            ColumnDistributionMetric(column_name="Predicted_readmitted"),

            # Generates a range of classification metrics such as Precision, Recall etc.
            ClassificationPreset(),
        ]
    )

    data_drift_report.run(reference_data=reference_data, current_data=new_data, column_mapping=column_mapping)

    logger.info("Report generation complete.... ")

    return data_drift_report

def compare_dataframe_features(reference_data, new_data):
    # Get all features
    ref_features = set(reference_data.columns)
    new_features = set(new_data.columns)

    # Get numeric features
    ref_numeric = set(get_numeric_features(reference_data))
    new_numeric = set(get_numeric_features(new_data))

    # Get categorical features
    ref_categorical = set(get_categorical_features(reference_data))
    new_categorical = set(get_categorical_features(new_data))

    # Compare total features
    if ref_features != new_features:
        logger.warning("Warning:The datasets have different features.")
        logger.warning("Features in reference data but not in new data:", ref_features - new_features)
        logger.warning("Features in new data but not in reference data:", new_features - ref_features)
    else:
        logger.info("Both datasets have the same features.")

    # Compare numeric features
    if ref_numeric != new_numeric:
        logger.warning("Warning: The datasets have different numeric features.")
        logger.warning("Numeric features in reference data but not in new data:", ref_numeric - new_numeric)
        logger.warning("Numeric features in new data but not in reference data:", new_numeric - ref_numeric)
    else:
        logger.info("Both datasets have the same numeric features.")

    # Compare categorical features
    if ref_categorical != new_categorical:
        logger.warning("Warning: The datasets have different categorical features.")
        logger.warning("Categorical features in reference data but not in new data:", ref_categorical - new_categorical)
        logger.warning("Categorical features in new data but not in reference data:", new_categorical - ref_categorical)
    else:
        logger.info("Both datasets have the same categorical features.")

    # Check if all comparisons pass
    if ref_features == new_features and ref_numeric == new_numeric and ref_categorical == new_categorical:
        logger.info("All checks passed. The datasets have identical feature structures.")
        return True
    else:
        logger.error("The datasets have different feature structures.")
        return False

def get_test_suite(reference_data, new_data, column_mapping):

    """
    Creates a test suite with TestAccuracyScore, TestPrecisionByClass for class '1' (churn), TestColumnDrift
    """

    data_test_suite = TestSuite(
        tests = [
                 TestAccuracyScore(gte=0.5),
                 TestPrecisionByClass(gte=0.5, label=1),
                 #TestColumnDrift(column_name='time_in_hospital ', stattest='psi', stattest_threshold=0.1),
                 TestColumnDrift(column_name='time_in_hospital', stattest='psi', stattest_threshold=0.1),
                 TestColumnDrift(column_name='num_medications', stattest='ks', stattest_threshold=0.05),
                 TestColumnDrift(column_name='number_diagnoses', stattest='ks', stattest_threshold=0.05)
                ],
        tags = ["patient-readmission-tests"]
    )

    data_test_suite.run(reference_data=reference_data, current_data=new_data, column_mapping=column_mapping)

    logger.info("Test Suite generation complete.... ")

    return data_test_suite

# def trigger_dag(trainer):
#     # Serialize the trainer object
#     serialized_trainer = pickle.dumps(trainer)
#     # Encode the serialized object as base64
#     encoded_trainer = base64.b64encode(serialized_trainer).decode('utf-8')

#     parameters = {
#         "conf": {
#             "trainer": encoded_trainer
#         }
#     }

#     # Send an authenticated HTTP POST request to trigger the DAG
#     response = requests.post(cfg.AIRFLOW_API_URL, json=parameters, auth=HTTPBasicAuth(cfg.AIRFLOW_USERNAME, cfg.AIRFLOW_PASSWORD))

#     # Check the response to see if the DAG was triggered successfully
#     if response.status_code == 200:
#         logger.info("DAG has been triggered successfully.")
#         return response.json()
#     else:
#         logger.error(f"Failed to trigger the DAG. Status code: {response.status_code}")
#         logger.error(response.text)
#         return None