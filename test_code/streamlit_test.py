import streamlit as st
import pandas as pd
import random


st.title("MediWatch Readmission Minder")

st.subheader("the way to anticipate readmissions")

# Function to determine readmission risk (placeholder logic)
def predict_readmission(row):
    return bool(random.getrandbits(1))

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    # Read the CSV file into a DataFrame
    data_all = pd.read_csv(uploaded_file)
    
    # Get 5 random samples from the DataFrame
    patient_sample = data_all.sample(n=5, random_state=42)
    
    # Display the sampled data
    st.write("Random sample of 5 rows:")
    st.write(patient_sample)

    
    
    # Add prediction column to the beginning of the DataFrame
    patient_sample.insert(0, 'Readmission_Risk', patient_sample.apply(predict_readmission, axis=1))
    
    # Display updated sample with prediction column
    st.write("Sample with readmission predictions:")
    st.write(patient_sample)
