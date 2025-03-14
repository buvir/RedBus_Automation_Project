import streamlit as st
import  pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt


data =pd.DataFrame(np.random.randn(100,3),columns=['a','b','c'])

st.line_chart(data)


st.area_chart(data)

st.bar_chart(data)

fig,ax=plt.subplots()
ax.scatter(data['a'],data['b'])
ax.set_title('Scatter')
st.pyplot(fig)

chart=alt.Chart(data).mark_circle().encode(x='a',y='b')
st.altair_chart(chart)

chart=alt.Chart(data).mark_circle().encode(x='a',y='b')
st.altair_chart(chart, use_container_width=True)




