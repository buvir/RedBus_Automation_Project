import streamlit as st

# choice = st.sidebar.radio(label='Choose an option', options=('IMAGE', 'VIDEO'))
# if choice=='IMAGE':
#     st.title('IMAGE')
#     st.image("C:/Users/USER/Desktop/RedBus_Automation_Project/download (6).jpeg")
# if choice=='VIDEO':
#     st.title('VIDEO')
#     st.video("C:/Users/USER/Desktop/RedBus_Automation_Project/3144446-hd_1920_1080_25fps.mp4")


# col1,col2 = st.columns([1,3],gap="small")
# col1.image("C:/Users/USER/Desktop/RedBus_Automation_Project/download (6).jpeg")
# col2.video("C:/Users/USER/Desktop/RedBus_Automation_Project/3144446-hd_1920_1080_25fps.mp4")

tab1,tab2=st.tabs(['Image','Video'])
tab1.image("C:/Users/USER/Desktop/RedBus_Automation_Project/download (6).jpeg")
tab2.video("C:/Users/USER/Desktop/RedBus_Automation_Project/3144446-hd_1920_1080_25fps.mp4")