import streamlit as st

st.title("MediWatch")

st.write("Welcome to MediWatch!")
x = st.text_input("Enter your name:")

st.write(f"Hello, {x}!")