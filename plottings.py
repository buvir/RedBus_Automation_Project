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


st.graphviz_chart("""

digraph{
status  ->  study
Learn  ->  implement   
                  
                  
                  
                  }

""")

st.map()

data = pd.DataFrame({
    'lat':[40.7128,51.5074,35.6895,33.8688],
    'lon':[74.0060,0.1278,139.6917,151.2093]
})

st.map(data)




