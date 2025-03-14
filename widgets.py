import streamlit as st

st.title("Widget")

if st.button("Press"):
    st.write("it is working")


name=st.text_input('Enter ur Name: ')
st.write(name)

ads=st.text_area('Address')
st.write(ads)

st.date_input('Enter ur date :')
st.time_input('Enter ur time :')

if st.checkbox("Accecpt"):
    st.write("agree")