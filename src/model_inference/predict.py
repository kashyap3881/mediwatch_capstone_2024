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
        """
        Predict diabetes patient readmission using the trained model.

        Process:
        1. Loads and cleans the input data using the clean module
        2. Loads the trained model and scaler
        3. Scales the features using the saved scaler
        4. Makes predictions using the model
        5. Returns results with patient IDs and predictions

        Returns:
            list: A list containing a dictionary with predictions in the format:
                [{'Hospital Readmission Prediction': [
                    {'patient_id': id, 'readmitted': actual, 'predicted_readmitted': pred},
                    ...
                ]}]
        """
        logger.info("Loading the original data ..........")
        original_df = pd.read_csv(self.filename)
        patient_id = original_df['patient_nbr']
        
        logger.info("Invoking cleaning module to clean new data ..........")
        cleanObj = clean(self.filename)
        clean_df = cleanObj.clean_data()

        # This is non-scaled data so we need to apply scaler here before we do predictions
        
        logger.info("Loading the best model ..........")
        loaded_model = joblib.load(os.path.join(self.model_dir, 'best_model.joblib'))
        loaded_scaler = joblib.load(os.path.join(self.model_dir, 'best_scaler.joblib'))

        y_actual = clean_df['readmitted']
        X_new = clean_df.drop('readmitted', axis=1)
        X_new_scaled = loaded_scaler.transform(X_new)

        # Predicting the patient readmission
        y_pred = loaded_model.predict(X_new_scaled)

        # Creating the result DataFrame
        result_df = pd.DataFrame({
            'patient_id': patient_id,
            'readmitted': y_actual,
            'predicted_readmitted': y_pred
        })

        # Convert the DataFrame to a dictionary
        result_dict = result_df.to_dict(orient='records')

        return [{"Hospital Readmission Prediction": result_dict}]