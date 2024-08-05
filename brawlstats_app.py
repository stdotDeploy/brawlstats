import streamlit as st 
import requests

st.title('BrawlStats')
st.write('A Brawl Stars Stats App')

params = st.text_input('Your Tag')

API_KEY = st.secrets(['api'])

def get_request(api_key, params):
    headers = 'Authentication : Bearer {API_KEY}'
    st.write('headers')
    url = 'https://api.brawlstars.com/v1/players/'
    response = requests.get(url, params=params, headers)
    return response

st.title('Brawl Stats')