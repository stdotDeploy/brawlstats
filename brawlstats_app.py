import streamlit as st 
import requests

def get_request():
    API_KEY = st.secrets['api']['API_KEY']
    headers = {'Authorization': f'Bearer {API_KEY}'}
    st.write(headers)
    url = 'https://api.brawlstars.com/v1/players/'
    response = requests.get(url, params=params, headers=headers)
    st.write(response.url)
    return response

st.title('BrawlStats')
st.write('A Brawl Stars Stats App')
params = st.text_input('Your Tag')
if params:
    st.write(get_request())
    

