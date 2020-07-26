import os
import json
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import requests

from core.menu import MainMenu

API_KEY = os.environ.get('API_KEY')
URL_API = 'https://api.hc.cornet-grandjean.com'

if not API_KEY:
    API_KEY = st.text_input('API_KEY', type='password')
    os.environ['API_KEY'] = API_KEY
MainMenu(URL_API, API_KEY).form()
