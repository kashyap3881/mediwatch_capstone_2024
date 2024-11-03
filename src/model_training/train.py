import numpy as np # linear algebra
import os
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler 
from sklearn import metrics
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score, classification_report
import lazypredict
from lazypredict.Supervised import LazyClassifier
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from src.data_cleaning.clean import clean
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class DiabetesReadmissionTrainer:
    def __init__(self, original_data_filename, new_data_filename):
        self.original_data_filename = original_data_filename
        self.new_data_filename = new_data_filename
        logger.info(f"Initializing Trainer with original data file: {self.original_data_filename} and new data file: {self.new_data_filename}")
    
    def train_and_evaluate_model(self):

        logger.info("Invoking cleaning module to clean original data ..........")
        cleanObj_orig = clean(self.original_data_filename)
        original_train_df = cleanObj_orig.clean_data()

        logger.info("Invoking cleaning module to clean new data ..........")
        cleanObj_new = clean(self.new_data_filename)
        new_train_df = cleanObj_new.clean_data()

        train_df = pd.concat([original_train_df, new_train_df], axis=0, ignore_index=True)

        logger.info("Loading the best model ..........")
        loaded_model = joblib.load(os.path.join(model_dir, 'best_model.joblib'))

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