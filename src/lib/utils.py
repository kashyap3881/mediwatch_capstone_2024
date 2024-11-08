import base64
import pickle
import requests
from requests.auth import HTTPBasicAuth
import src.lib.dagconfig as cfg

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def decodeCSV(csvstring, fileName):
    csvdata = base64.b64decode(csvstring).decode('utf-8')
    with open(fileName, 'w') as f:
        f.write(csvdata)
        f.close()
    logger.info(f"CSV file saved as: {fileName}")

def trigger_dag(trainer):
    # Serialize the trainer object
    serialized_trainer = pickle.dumps(trainer)
    # Encode the serialized object as base64
    encoded_trainer = base64.b64encode(serialized_trainer).decode('utf-8')

    parameters = {
        "conf": {
            "trainer": encoded_trainer
        }
    }   

    # Send an authenticated HTTP POST request to trigger the DAG
    response = requests.post(cfg.AIRFLOW_API_URL, json=parameters, auth=HTTPBasicAuth(cfg.AIRFLOW_USERNAME, cfg.AIRFLOW_PASSWORD))

    # Check the response to see if the DAG was triggered successfully
    if response.status_code == 200:
        logger.info("DAG has been triggered successfully.")
        return response.json()
    else:
        logger.error(f"Failed to trigger the DAG. Status code: {response.status_code}")
        logger.error(response.text)
        return None
