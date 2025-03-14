import streamlit as st
import pandas as pd
import numpy as np

l=[1,2,3,4,5,6,7,8]

n=np.array(l)

lp=n.reshape(2,4)

dic={'Name': 'Hickson',
     'Age':56,
     'Place':'Australia'}

# df=pd.read_csv("path")

st.dataframe(l)

st.dataframe(n)

st.dataframe(lp)

st.dataframe(dic)

st.json(dic)