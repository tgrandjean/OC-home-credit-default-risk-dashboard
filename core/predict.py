import matplotlib.pyplot as plt
import requests
import streamlit as st
import json


class Scorer:

	def __init__(self, API_URL, API_KEY):
		self.API_URL = API_URL
		self.API_KEY = API_KEY
	
	@property
	def headers(self):
		return {'Content-Type': 'application/json',
				'Authorization': 'Token ' + self.API_KEY}

	def _fetch_application(self, id):
		res = requests.get(self.API_URL + f'/applications/{id}', 
						   headers=self.headers)
		return res.json()

	def _make_inference(self, data):
		res = requests.post(self.API_URL + '/predict/', 
							data=json.dumps(data), 
							headers=self.headers)
		return res.json()

	@st.cache
	def _min_max_ids(self):
		first = requests.get(self.API_URL + '/applications/first_record/', 
							 headers=self.headers)
		last = requests.get(self.API_URL + '/applications/last_record/', 
							headers=self.headers)
		first = first.json()['sk_id_curr']
		last = last.json()['sk_id_curr']
		return {'min_value': first, 'max_value': last}		

	def form(self):
		st.title('Prêt à dépenser')
		sk_id_curr = st.number_input('ID de la demande', 
									 **self._min_max_ids(),
									 value=self._min_max_ids()['min_value'],
									 step=1)
		app = self._fetch_application(sk_id_curr)
		app['amt_credit'] = st.slider('Montant du crédit',
									  value=app['amt_credit'] ,
									  min_value=app['amt_credit'] / 10, 
									  max_value=app['amt_credit'] * 5)

		app['amt_annuity'] = st.slider('Montant des mensualités',
									  value=app['amt_annuity'] ,
									  min_value=app['amt_annuity'] / 10, 
									  max_value=app['amt_annuity'] * 5)
		data = {'sk_id_curr': sk_id_curr,
			    'amt_credit': app['amt_credit'],
		        'amt_annuity': app['amt_annuity']}
		prob = self._make_inference(data)
		st.info(f"Probabilité de remboursement du prêt : {round(prob['Model response'], 2)} %")
		for key, val in app.items():
			if key != 'sk_id_curr':
				st.markdown(f'**{key}**: {val}')
		st.markdown('**Nombre de mensualités: %.1f **' % (app['amt_credit'] / app['amt_annuity']))
		# Income proportion
		f, ax = plt.subplots(1, figsize=(4, 4))
		amt_annuity = app['amt_annuity']
		amt_income = app['amt_income_total']
		labels = ['Remboursement', 'Revenus']
		ax.pie([amt_annuity, amt_income - amt_annuity], 
			   labels=labels, 
			   autopct='%1.1f%%',
			   startangle=90)
		ax.axis('equal')
		st.pyplot()