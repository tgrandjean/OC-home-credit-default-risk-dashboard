import streamlit as st

from .data_selector import DataSelector
from .predict import Scorer
from .home import Home
from .explainer import ModelExplainer


class MainMenu:

	def __init__(self, API_URL, API_KEY):
		self.API_KEY = API_KEY
		self.API_URL = API_URL

	@property
	def pages(self):
		choices = ['Accueil',
				   'Exploratateur des demandes',
				   'Simulateur de crédit',
				   'Explication de score'
				   ]
		return choices

	def form(self):
		page = st.sidebar.selectbox('Veuillez choisir une option',
									options=self.pages)
		if page == self.pages[0]:
			return Home()
		elif page == self.pages[1]:
			return DataSelector(self.API_URL, self.API_KEY).form()
		elif page == self.pages[2]:
			return Scorer(self.API_URL, self.API_KEY).form()
		elif page == self.pages[3]:
			return ModelExplainer(self.API_URL, self.API_KEY).form()
