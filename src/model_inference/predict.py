import os
import joblib
import pandas as pd
from src.data_cleaning.clean import clean
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DiabetesReadmissionPredictor:
    def __init__(self, filename, model_dir):
        self.filename = filename
        self.model_dir = model_dir
        logger.info(f"Initializing Diabetes Readmission Predictor with file: {self.filename} and best model at {self.model_dir}")
    
    def prediction_diabetes_readmission(self):
        logger.info("Loading the original data ..........")
        original_df = pd.read_csv(self.filename)
        patient_id = original_df['patient_nbr']
        
        logger.info("Invoking cleaning module to clean new data ..........")
        cleanObj = clean(self.filename)
        clean_df = cleanObj.clean_data()
        
        logger.info("Loading the best model ..........")
        loaded_model = joblib.load(os.path.join(self.model_dir, 'best_model.joblib'))

        y_actual = clean_df['readmitted']
        X_new = clean_df.drop('readmitted', axis=1)

        # Predicting the patient readmission
        y_pred = loaded_model.predict(X_new)

        # Creating the result DataFrame
        result_df = pd.DataFrame({
            'patient_id': patient_id,
            'readmitted': y_actual,
            'predicted_readmitted': y_pred
        })

        # Convert the DataFrame to a dictionary
        result_dict = result_df.to_dict(orient='records')

        return [{"Hospital Readmission Prediction": result_dict}]