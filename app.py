import os
import json
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import requests

from assets.sidebar import Sidebar

API_KEY = os.environ.get('API_KEY')
URL_API = 'https://api.hc.cornet-grandjean.com'

Sidebar(URL_API, API_KEY).form()
