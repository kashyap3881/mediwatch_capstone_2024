"""
Data cleaning module for the MediWatch project's medical dataset.

This module provides functionality for cleaning and preprocessing medical data,
particularly focused on hospital readmission data. It includes methods for
feature dropping, data transformation, and categorical variable processing.

The main class `clean` handles various preprocessing tasks such as:
- Converting readmission data to binary classification
- Transforming age groups to numerical values
- Mapping admission IDs to meaningful categories
- Handling missing values and data normalization

Example:
    cleaner = clean('path_to_data.csv')
    cleaner.collapse_readmitted()
    cleaner.collapse_age_groups()
"""
import pandas as pd
import numpy as np
from .common import get_rows_columns_dtypes, get_unique_values
from sklearn.preprocessing import LabelEncoder
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class clean:
    """
    A class for cleaning and preprocessing medical data.

    This class provides methods to clean and transform medical dataset features,
    particularly focusing on readmission prediction preprocessing tasks.

    Parameters:
        filename (str): Path to the CSV file containing the medical data to be processed.

    Attributes:
        filename (str): Path to the source data file.
        df (pandas.DataFrame): DataFrame containing the loaded and processed medical data.
            This is the main data structure that gets transformed by the cleaning methods.
    """
    def __init__(self, filename):
        self.filename = filename
        self.df = pd.read_csv(self.filename)
        logger.info(f"Initializing Data cleaner with the file: {self.filename}")
    
    def drop_feature(self, feature_arr=[]):
        self.df = self.df.drop(feature_arr, axis=1)
    

    def collapse_readmitted(self):
        """
        Collapse readmission variable into a binary target variable, where:
        - 0: Readmitted after 30 days
        - 1: Readmitted in less than 30 days
        """
        # New target variable mapping to collapse into a binary classification and plotting distribution
        self.df = self.df.replace({"NO":0,
                                   "<30":1,
                                   ">30":0})
        logger.info(self.df.readmitted.value_counts())
    
    def collapse_age_groups(self):

        self.df.age = self.df.age.replace({"[70-80)":75,
                                           "[60-70)":65,
                                           "[50-60)":55,
                                           "[80-90)":85,
                                           "[40-50)":45,
                                           "[30-40)":35,
                                           "[90-100)":95,
                                           "[20-30)":25,
                                           "[10-20)":15,
                                           "[0-10)":5})
    
    def collapse_admission_id(self):
        """
        Transform numerical admission type IDs into categorical string values.
        
        Transforms the numerical IDs in 'admission_type_id' column to descriptive strings:
            1.0, 2.0 -> "Emergency"     : Different types of emergency admissions
            3.0      -> "Elective"      : Planned/scheduled admissions
            4.0      -> "New Born"      : Birth/newborn admissions
            7.0      -> "Trauma Center" : Specialized trauma admissions
            5.0, 6.0, 8.0 -> np.nan     : Unknown or invalid admission types
        
        The method modifies the 'admission_type_id' column in the DataFrame directly.
        """

        mapped = {1.0:"Emergency",
                  2.0:"Emergency",
                  3.0:"Elective",
                  4.0:"New Born",
                  5.0:np.nan,
                  6.0:np.nan,
                  7.0:"Trauma Center",
                  8.0:np.nan}

        self.df.admission_type_id = self.df.admission_type_id.replace(mapped)
    
    def collapse_discharge_disposition_id(self):

        mapped_discharge = {1:"Discharged to Home",
                            6:"Discharged to Home",
                            8:"Discharged to Home",
                            13:"Discharged to Home",
                            19:"Discharged to Home",
                            18:np.nan,25:np.nan,26:np.nan,
                            2:"Other",3:"Other",4:"Other",
                            5:"Other",7:"Other",9:"Other",
                            10:"Other",11:"Other",12:"Other",
                            14:"Other",15:"Other",16:"Other",
                            17:"Other",20:"Other",21:"Other",
                            22:"Other",23:"Other",24:"Other",
                            27:"Other",28:"Other",29:"Other",30:"Other"}
        
        self.df["discharge_disposition_id"] = self.df["discharge_disposition_id"].replace(mapped_discharge)
    
    def collapse_admission_source_id(self):

        mapped_adm = {1:"Referral",2:"Referral",3:"Referral",
                      4:"Other",5:"Other",6:"Other",10:"Other",22:"Other",25:"Other",
                      9:"Other",8:"Other",14:"Other",13:"Other",11:"Other",
                      15:np.nan,17:np.nan,20:np.nan,21:np.nan,
                      7:"Emergency"}
        self.df.admission_source_id = self.df.admission_source_id.replace(mapped_adm)
    
    def label_encode(self):
        """
        Convert categorical string columns into numerical values using LabelEncoder.
        
        Process:
        1. Separates categorical (string) and numerical columns
        2. For each categorical column, converts unique string values into integers
           Example: ["Emergency", "Elective", "New Born"] → [0, 1, 2]
        3. Combines the encoded categorical columns with the original numerical columns
        
        Returns:
            pandas.DataFrame: DataFrame with all categorical columns converted to numbers
        """
        cat_data = self.df.select_dtypes('O')
        num_data = self.df.select_dtypes(np.number)

        LE = LabelEncoder()
        for i in cat_data:
            cat_data[i] = LE.fit_transform(cat_data[i])
        data = pd.concat([num_data,cat_data],axis=1)
        return data


    def clean_data(self):

        get_rows_columns_dtypes(self.df)

        get_unique_values(self.df)

        '''
        replace all occurrences of the string "?" in the DataFrame df with np.nan (Not a Number), 
        effectively converting unknown or missing values to NaN for further processing.
        '''
        self.df = self.df.replace("?",np.nan)

        # Drop weight, payer_code, and medical_speciality features
        logger.info("Dropping weight, payer_code, and medical_speciality features")
        self.drop_feature(['weight', 'payer_code', 'medical_specialty'])

        self.collapse_readmitted()

        # Drop Unknown/Invalid gender records
        self.df = self.df.drop(self.df.loc[self.df["gender"]=="Unknown/Invalid"].index, axis=0)

        # Collapsing ages groups to specific midpoint values of ages
        self.collapse_age_groups()

        # Collapsing ID to specific categories Emergency, Elective, New Born, and Trauma Center
        self.collapse_admission_id()

        # Collapsing Discharge disposition IDs to to mainly two categories Discharged to Home and Other
        self.collapse_discharge_disposition_id()

        # Collapsing Admission Source IDs to Referral,  Other, and Emergency
        self.collapse_admission_source_id()

        # Get list of columns with missing values
        missing_cols = self.df.columns[self.df.isnull().any()].tolist()

        if len(missing_cols) > 0:
            logger.info("Replace missing values with most common value")
            for feat in missing_cols:
                self.df[f'{feat}'] = self.df[f'{feat}'].fillna(self.df[f'{feat}'].mode()[0])
        
        # Perfom Label Encoding
        self.df = self.label_encode()

        # Drop encounter_id and patient_nbr
        self.drop_feature(['encounter_id','patient_nbr'])

        logger.info(f"Data cleaned successfully and ready for either training or prediction")

        get_rows_columns_dtypes(self.df)

        get_unique_values(self.df)

        return self.df