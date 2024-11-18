import numpy as np
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



def get_rows_columns_dtypes(data):
    # Print the shape
    # Overview of dataframe
    rows = data.shape[0]
    cols = data.shape[1]
    logger.info('#samples  (rows)    =  {}'.format(rows))
    logger.info('#features (columns) =  {}'.format(cols))
    
    # Print the data types dtypes
    logger.info(f"\nData types:\n {data.dtypes}")

#Checking for missing values in dataset
#In the dataset missing values are represented as '?' sign
def check_missing_values(data):
  missing_features = False
  for col in data.columns:
    num_missing = data[col][data[col] == '?'].count()
    percent_missing = (data[col] == '?').mean() * 100
    logger.info(f'{col},\t {num_missing},\t {percent_missing:.2f}%')


# get list of only numeric features
# def get_numeric_features(data, forecast_column=None):
#     if forecast_column:
#         return(list(set(list(data._get_numeric_data().columns))- {forecast_column}))
#     return(list(set(list(data._get_numeric_data().columns))))



# # get list of only categorical features
# def get_categorical_features(data, col_exclude=None):
#     cat_col = data.select_dtypes(include=['object', 'category', 'bool']).columns.tolist()
#     if col_exclude:
#         cat_col = [col for col in cat_col if col != col_exclude]
#     return(cat_col)

def get_numeric_features(data, col_exclude=None):
    numeric_columns = data.select_dtypes(np.number).columns.tolist()
    if col_exclude:
        numeric_columns = [col for col in numeric_columns if col not in col_exclude]
    return numeric_columns

def get_categorical_features(data, col_exclude=None):
    categorical_columns = data.select_dtypes('O').columns.tolist()
    if col_exclude:
        categorical_columns = [col for col in categorical_columns if col not in col_exclude]
    return categorical_columns


#Checking the unique values of the columns
def get_unique_values(data):
  for col in data.columns:
    logger.info(f"Unique values of {col}: {data[col].unique()}")

