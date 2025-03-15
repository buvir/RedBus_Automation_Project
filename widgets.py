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

v1=st.radio("colors",['R','Y','B'],index=1)
st.write(v1)

v1=st.selectbox("colors",['R','Y','B','G'],index=1)
st.write(v1)

v1=st.multiselect("colors",['R','Y','B','G'])
st.write(v1)

c=st.slider("age",min_value=0,max_value=100,step=2)
st.write(c)
