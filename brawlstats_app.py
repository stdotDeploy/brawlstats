import streamlit as st 
import json
import pandas as pd 
from Brawlstats import APIrequests
import base64

@ st.cache_data
def get_img(file):
    with open (file, 'rb') as f:
        data=f.read()
    return base64.b64encode(data).decode()

img = get_img("/home/lrose/brawlstats/assets/wallpaper.jpg")
API_KEY = st.secrets['api']['api_key'] 
api =  APIrequests(api_key=API_KEY)


css = f"""
<style>
[data-testid="stApp"] {{
background-image: url("data:/home/lrose/brawlstats/assets/wallpaper.jpg;base64,{img}");
background-size: cover}}

[data-testid="stHeader"] {{
background-color: rgb(0 0 0 / 0%)
}}

[data-testid="stTextInput-RootElement"]{{    
height : 5em;
border-radius: 300px;
}}

[data-testid="stTextInput"] {{  
    width:300px;
    margin-left: auto;
    margin-right: auto;
}}

[data-baseweb="base-input"] {{    
    background-color:white;
}}

[data-baseweb="base-input"] > input{{    
font-weight:bolder;
font-size: 1.5em;
text-align: center;
}}


</style>
"""

# Apply custom CSS
st.markdown(css, unsafe_allow_html=True)

# Display logo in the center column
col1, col2, col3 = st.columns([1, 3, 1])
with col2:
    st.image('/home/lrose/brawlstats/assets/logo.png', use_column_width=True)

user_tag = st.text_input('.', placeholder='Enter your Player Tag')
if user_tag:
    st.write(user_tag)
    if user_tag not in st.session_state:
        st.session_state.user_tag = user_tag

    st.switch_page('pages/01_dashboard.py')