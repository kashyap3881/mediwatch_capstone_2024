import os
import joblib
import pandas as pd
from ..data_cleaning.clean import clean
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class DiabetesReadmissionPredictor:
    def __init__(self, filename, model_dir):
        self.filename = filename
        self.model_dir = model_dir
        logger.info(f"Initializing Diabetes Readmission Predictor with file: {self.filename} and best model at {self.model_dir}")

    def merge_or_save_new_data(self):
        # Define the path to the new_data directory and new_data.csv file
        new_data_dir = os.path.join(os.path.dirname(os.path.dirname(self.model_dir)), 'new_data')
        new_data_path = os.path.join(new_data_dir, "new_data.csv")
        
        # Ensure the new_data directory exists
        os.makedirs(new_data_dir, exist_ok=True)

        # Load the new data from self.filename
        new_data_df = pd.read_csv(self.filename)

        if os.path.exists(new_data_path):
            # If new_data.csv exists, load and concatenate with the new data
            existing_data_df = pd.read_csv(new_data_path)
            combined_df = pd.concat([existing_data_df, new_data_df], axis=0, ignore_index=True)
            logger.info("Merged new data with existing new_data.csv")
        else:
            # If new_data.csv doesn't exist, use new_data_df directly
            combined_df = new_data_df
            logger.info("Saving new data as new_data.csv")
        
        # Remove exact duplicate rows
        combined_df = combined_df.drop_duplicates()

        # Save the combined data back to new_data.csv
        combined_df.to_csv(new_data_path, index=False)
        logger.info("Data merged, duplicates removed, and saved to new_data.csv")
    
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

        # Merge or save the cleaned data
        self.merge_or_save_new_data()

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