import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("ggplot")

data={
    'num':[x for x in range(1,11)],
    'square':[x**2 for x in range(1,11)],
    'double':[x*2 for x in range(1,11)] ,
    'triple':[x*3 for x in range(1,11) ]
}

# df=pd.DataFrame(data=data)
# st.write(data)

# st.dataframe(df)

df=pd.DataFrame(data=data)
#col=st.sidebar.selectbox (" select a column ",df.columns)
#st.write(col)

# col=st.sidebar.selectbox (" select a column ",[1,2,3,4])


#st.sidebar.selectbox (" select a column ",[1,2,3,4])

col=st.sidebar.selectbox (" select a column ",df.columns)
st.write(col)

fig,ax=plt.subplots()
ax.plot(df['num'],df[col])

ax.set_title(f'plot of {col} vs Num')
ax.set_xlabel('num')
ax.set_ylabel('col')

st.pyplot(fig)
