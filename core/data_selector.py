import pandas as pd
import requests
import streamlit as st
from requests.exceptions import HTTPError

class DataSelector:

	def __init__(self, API_URL, API_KEY):
		self.API_URL = API_URL
		self.API_KEY = API_KEY
		self.url_app = API_URL + '/applications/'
		self.query = dict(limit=10, offset=0)

	@property
	def headers(self):
		return {'Content-Type': 'application/json',
				'Authorization': 'Token ' + self.API_KEY}

	@property
	def __occupation_type_choices(self):
		json_res = self.__fetch(None, method='OPTIONS')
		occupation_type = json_res['actions']['POST']['occupation_type']
		return [None] + [x['value'] for x in occupation_type['choices']]

	@property
	def __credit_type_choices(self):
		json_res = self.__fetch(None, method='OPTIONS')
		credit_type = json_res['actions']['POST']['name_contract_type']
		return [None] + [x['value'] for x in credit_type['choices']]

	def __fetch(self, query, url=None, method='GET'):
		if method == 'GET':
			response = requests.get(url if url else self.url_app,
								    headers=self.headers,
									params=query)
		elif method == 'OPTIONS':
			response = requests.options(self.url_app, headers=self.headers)
		if response.status_code != 200:
			raise HTTPError(response.status_code)
		return response.json()

	def form(self):
		first = self.__fetch(None,
							 url=self.url_app+ 'first_record')['sk_id_curr']
		last = self.__fetch(None,
							url=self.url_app + 'last_record')['sk_id_curr']
		id = st.slider('Numéro de dossier',
					   min_value=first,
					   max_value=last,
					   value=(first, last))
		self.query['min_sk_id_curr'], self.query['max_sk_id_curr'] = id

		age = st.slider('Age', min_value=18,
				        max_value=100, value=(18, 100))
		self.query['min_days_birth'], self.query['max_days_birth'] = age
		occupation_type = st.selectbox('Profession',
									   options=self.__occupation_type_choices)
		self.query['occupation_type'] = occupation_type
		name_contract_type = st.selectbox('Type de contrat',
										  options=self.__credit_type_choices)
		self.query['name_contract_type'] = name_contract_type
		res = self.__fetch(self.query)
		st.markdown(f"### Nombre de demandes correspondant à votre requête {res['count']}")

		page_slot = st.empty()
		page = page_slot.number_input('page', min_value=0,
						 	    	  max_value=res['count'] // 10,
									  value=0)
		if page:
			self.query['offset'] = page * 10
			res = self.__fetch(self.query)
		slot = st.empty()
		slot.dataframe(pd.DataFrame(res['results']))
		for elt in res['results']:
			if st.button('predict ' + str(elt['sk_id_curr'])):
				st.sidebar.number_input('id application', value=elt['sk_id_curr'])
