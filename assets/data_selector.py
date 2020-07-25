import pandas as pd
import requests
import streamlit as st
from requests.exceptions import HTTPError


class DataSelector:

	def __init__(self, API_URL, API_KEY):
		self.API_URL = API_URL
		self.API_KEY = API_KEY
		self.query = dict()

	@property
	def headers(self):
		return {'Content-Type': 'application/json',
				'Authorization': 'Token ' + self.API_KEY}

	@property
	def __occupation_type_choices(self):
		url = self.API_URL + '/applications/'
		response = requests.options(url, headers=self.headers)
		json_res = response.json()
		occupation_type = json_res['actions']['POST']['occupation_type']
		return [None] + [x['value'] for x in occupation_type['choices']]

	def __fetch(self, query):
		url = self.API_URL + f'/applications/'
		response = requests.get(url, headers=self.headers, params=query)
		if response.status_code != 200:
			raise HTTPError(response.status_code)
		return response.json()

	def form(self):
		age = st.slider('Age', min_value=18, 
				        max_value=100, value=(18, 100))
		self.query['min_days_birth'] = age[0]
		self.query['max_days_birth'] = age[1]
		occupation_type = st.selectbox('Occupation type', 
									   options=self.__occupation_type_choices)
		self.query['occupation_type'] = occupation_type
		res = self.__fetch(self.query)
		st.markdown(f"### Nombre de demandes correspondant à votre requête {res['count']}")
		st.write(pd.DataFrame(res['results']))
