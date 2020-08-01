import pandas as pd
import requests
import streamlit as st
from requests.exceptions import HTTPError

from .base import Component


class DataSelector(Component):

	def __init__(self, *args):
		super(DataSelector, self).__init__(*args)
		self.url_app = self.API_URL + '/applications/'
		self.query = dict(limit=10, offset=0)

	@property
	def __occupation_type_choices(self):
		"""Get available options for choice field occupation_type."""
		json_res = self.__fetch(None, method='OPTIONS')
		occupation_type = json_res['actions']['POST']['occupation_type']
		return [None] + [x['value'] for x in occupation_type['choices']]

	@property
	def __credit_type_choices(self):
		"""Get available options for choice field name_contract_type."""
		json_res = self.__fetch(None, method='OPTIONS')
		credit_type = json_res['actions']['POST']['name_contract_type']
		return [None] + [x['value'] for x in credit_type['choices']]

	def __fetch(self, query, url=None, method='GET'):
		"""Fetch data from API.

		args::
			* query (dict) : params that be passed as query in url.

		kwargs::
		 	* url (str) : url that you want to fetch. default is None make
				a request to self.url_app.
			* method (str): Http that you want to use. default is GET.
				should be one of GET or OPTIONS
		"""
		if method == 'GET':
			response = requests.get(url if url else self.url_app,
								    headers=self.headers,
									params=query)
		# get available options for an entry point
		elif method == 'OPTIONS':
			response = requests.options(self.url_app, headers=self.headers)
		if response.status_code != 200:
			raise HTTPError(response.status_code)
		return response.json()

	def form(self):
		# Fetch fist record and last record for making slider's boundaries
		first = self.__fetch(None,
							 url=self.url_app+ 'first_record')['sk_id_curr']
		last = self.__fetch(None,
							url=self.url_app + 'last_record')['sk_id_curr']
		id = st.slider('Numéro de dossier',
					   min_value=first,
					   max_value=last,
					   value=(first, last))
		# use returned tuple by slider to filter applications
		self.query['min_sk_id_curr'], self.query['max_sk_id_curr'] = id

		age = st.slider('Age', min_value=18,
				        max_value=100, value=(18, 100))
		# Use returned tuple by age slider to filer applications
		self.query['min_days_birth'], self.query['max_days_birth'] = age

		occupation_type = st.selectbox('Profession',
									   options=self.__occupation_type_choices)
		# Filter applications by occupation_type
		self.query['occupation_type'] = occupation_type
		# Filter application by contract name
		name_contract_type = st.selectbox('Type de contrat',
										  options=self.__credit_type_choices)
		self.query['name_contract_type'] = name_contract_type
		# finally fetch corresponding applications
		res = self.__fetch(self.query)
		# Display the number of applications that match to filters
		st.markdown(f"### Nombre de demandes correspondant à votre requête {res['count']}")

		# add a number input that allow us to reload applications for next
		# or previous page. The API return paginated applications for
		# performance reasons
		page_slot = st.empty()
		page = page_slot.number_input('page', min_value=0,
						 	    	  max_value=res['count'] // 10,
									  value=0)
		# if page is not null, increase the offset to get the right page
		if page:
			self.query['offset'] = page * 10
			res = self.__fetch(self.query)
		slot = st.empty()
		results = pd.DataFrame(res['results'])
		# HACK: normally this field should be renamed directly in API
		results.rename(columns={"days_birth": "age"}, inplace=True)
		# finally display the corresponding dataframe
		slot.dataframe(results)
