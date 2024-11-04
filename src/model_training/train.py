import numpy as np # linear algebra
import os
import shutil
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
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
    def __init__(self, original_data_filename, new_data_filename=None, model_dir=None):
        self.original_data_filename = original_data_filename
        self.new_data_filename = new_data_filename
        self.model_dir = model_dir
        logger.info("Initializing Trainer with original data file: {} and new data file: {} and model dir: {}".format(
            self.original_data_filename,
            self.new_data_filename,
            self.model_dir
        ))
    
    def train_and_evaluate_model(self):

        logger.info("Invoking cleaning module to clean original data ..........")
        cleanObj_orig = clean(self.original_data_filename)
        original_train_df = cleanObj_orig.clean_data()

        if self.new_data_filename:
            logger.info("Invoking cleaning module to clean new data ..........")
            cleanObj_new = clean(self.new_data_filename)
            new_train_df = cleanObj_new.clean_data()
            train_df = pd.concat([original_train_df, new_train_df], axis=0, ignore_index=True)
        else:
            train_df = original_train_df

        # Splitting the data into train and test
        logger.info("Splitting the data into train and test")
        X = train_df.drop('readmitted', axis=1)
        y = train_df['readmitted']
        X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,random_state=1)

        train_algo_accuracy = {}
        test_algo_accuracy = {}

        # Standardizing the data
        logger.info("Standardizing the data")
        SC = StandardScaler()
        X_train_scaled = pd.DataFrame(SC.fit_transform(X_train),columns=X_train.columns)
        X_test_scaled = pd.DataFrame(SC.transform(X_test),columns=X_test.columns)
        scaler_dir = os.path.join(self.model_dir, 'scaler')
        if not os.path.exists(scaler_dir):
            os.makedirs(scaler_dir)
        joblib.dump(SC, os.path.join(scaler_dir, 'standard_scaler.joblib'), compress=('gzip', 3))

        # Linear Regression Model
        log_reg_dir = os.path.join(self.model_dir, 'logisic_regression')
        if not os.path.exists(log_reg_dir):
            os.makedirs(log_reg_dir)
        logger.info("Training Linear Regression Model")
        train_algo_accuracy['Logistic Regression'] = 0
        test_algo_accuracy['Logistic Regression'] = 0
        LR = LogisticRegression()
        LR.fit(X_train_scaled,y_train)
        train_algo_accuracy['Logistic Regression'] = LR.score(X_train_scaled,y_train)
        logger.info("Logistic Regression Train Accuracy: {}".format(
            train_algo_accuracy['Logistic Regression']
            ))
        joblib.dump(LR, os.path.join(log_reg_dir, 'logistic_model.joblib'), compress=('gzip', 3))

        y_test_pred = LR.predict(X_test_scaled)
        cm = confusion_matrix(y_test, y_test_pred)
        test_algo_accuracy['Logistic Regression'] = accuracy_score(y_test, y_test_pred)
        logger.info("Logistic Regression Test Accuracy: {}\n Test confusion matrix: {}".format(
            test_algo_accuracy['Logistic Regression'],
            cm
            ))

        # Random Forest Model
        random_forest_dir = os.path.join(self.model_dir, 'random_forest')
        if not os.path.exists(random_forest_dir):
            os.makedirs(random_forest_dir)
        logger.info("Training Random Forest Model")
        train_algo_accuracy['Random Forest'] = 0
        RF = RandomForestClassifier()
        RF.fit(X_train,y_train)
        train_algo_accuracy['Random Forest'] = RF.score(X_train,y_train)
        logger.info("Random Forest Train Accuracy: {}".format(
            train_algo_accuracy['Random Forest']
            ))
        joblib.dump(RF, os.path.join(random_forest_dir, 'random_forest.joblib'), compress=('gzip', 3))

        y_test_pred = RF.predict(X_test)
        cm = confusion_matrix(y_test, y_test_pred)
        test_algo_accuracy['Random Forest'] = accuracy_score(y_test, y_test_pred)
        logger.info("Random Forest Test Accuracy: {}\n Test confusion matrix: {}".format(
            test_algo_accuracy['Random Forest'],
            cm
            ))

        # # Lazy Classifier Models
        # X = train_df.drop('readmitted', axis=1)
        # y = train_df['readmitted']
        # X_sampled, _, y_sampled, _ = train_test_split(X, y, train_size=20000, stratify=y, random_state=42)
        # X_train, X_test, y_train, y_test = train_test_split(X_sampled, y_sampled, test_size=0.2, stratify=y_sampled, random_state=42)

        # # Standardizing the data
        # logger.info("Standardizing the data")
        # SC = StandardScaler()
        # X_train_scaled = pd.DataFrame(SC.fit_transform(X_train),columns=X_train.columns)
        # X_test_scaled = pd.DataFrame(SC.transform(X_test),columns=X_test.columns)
        # joblib.dump(SC, os.path.join(scaler_dir, 'lazy_standard_scaler.joblib'), compress=('gzip', 3))

        # lazy_classifier_dir = os.path.join(self.model_dir, 'lazy_classifier')
        # if not os.path.exists(lazy_classifier_dir):
        #     os.makedirs(lazy_classifier_dir)
        # logger.info("Training Lazy Classifier Models")
        # clf = LazyClassifier(verbose=0,ignore_warnings=True, custom_metric=None)
        # models, predictions = clf.fit(X_train_scaled, X_test_scaled, y_train, y_test)
        # model_dict = clf.provide_models(X_train_scaled, X_test_scaled, y_train, y_test)

        # # Select top 3 models based on test accuracy
        # top_3_models = models.head(3)
        # logger.info("Top 3 models:\n{}".format(top_3_models))

        # # Store top 3 models and their accuracies
        # for model_name in top_3_models.index:
        #     model = model_dict[model_name]
        #     joblib.dump(model, os.path.join(lazy_classifier_dir, f'{model_name}.joblib'), compress=('gzip', 3))
        #     train_algo_accuracy[model_name] = model.score(X_train_scaled, y_train)
        #     test_algo_accuracy[model_name] = models.loc[model_name, 'Accuracy']
        #     logger.info(f"{model_name} Train Accuracy: {train_algo_accuracy[model_name]} Test Accuracy: {test_algo_accuracy[model_name]}")

        # Choose the best model
        best_model_name = max(test_algo_accuracy, key=test_algo_accuracy.get)
        best_model_accuracy = test_algo_accuracy[best_model_name]

        logger.info(f"Best model: {best_model_name}")
        logger.info(f"Best model train accuracy: {train_algo_accuracy[best_model_name]}")
        logger.info(f"Best model test accuracy: {best_model_accuracy}")

        # Store the best model
        best_model_dir = os.path.join(self.model_dir, 'best_model')
        if not os.path.exists(best_model_dir):
            os.makedirs(best_model_dir)

        if best_model_name == 'Logistic Regression':
            best_model = LR
            source_path = os.path.join(log_reg_dir, 'logistic_model.joblib')
            scaler_path = os.path.join(scaler_dir, 'standard_scaler.joblib')
        elif best_model_name == 'Random Forest':
            best_model = RF
            source_path = os.path.join(random_forest_dir, 'random_forest.joblib')
            scaler_path = os.path.join(scaler_dir, 'standard_scaler.joblib')
        # else:
        #     best_model = model_dict[best_model_name]
        #     source_path = os.path.join(lazy_classifier_dir, f'{best_model_name}.joblib')
        #     scaler_path = os.path.join(scaler_dir, 'lazy_standard_scaler.joblib')

        # Move the best model to the best_model directory
        shutil.copy(source_path, os.path.join(best_model_dir, 'best_model.joblib'))

        # Store the best scaler
        shutil.copy(scaler_path, os.path.join(best_model_dir, 'best_scaler.joblib'))

        # Clean up directories
        # directories_to_remove = ['logistic_regression', 'random_forest', 'lazy_classifier', 'scaler']
        directories_to_remove = ['logistic_regression', 'random_forest', 'scaler']
        for dir_name in directories_to_remove:
            dir_path = os.path.join(self.model_dir, dir_name)
            if os.path.exists(dir_path):
                shutil.rmtree(dir_path)

        return {
            'best_model_name': best_model_name,
            'best_model_train_accuracy': train_algo_accuracy[best_model_name],
            'best_model_test_accuracy': best_model_accuracy
        }