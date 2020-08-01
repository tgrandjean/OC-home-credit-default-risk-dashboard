import json
import requests
import streamlit as st
import numpy as np
import pandas as pd
from matplotlib import colors

from .base import Component


class ModelExplainer(Component):

    @st.cache
    def _min_max_ids(self):
        first = requests.get(self.API_URL + '/applications/first_record/',
                             headers=self.headers)
        last = requests.get(self.API_URL + '/applications/last_record/',
                            headers=self.headers)
        first = first.json()['sk_id_curr']
        last = last.json()['sk_id_curr']
        return {'min_value': first, 'max_value': last}

    def __get_explaination(self, data):
        res = requests.post(self.API_URL + '/explainer/',
                            data=json.dumps(data),
                            headers=self.headers)
        return res.json()

    @property
    def cmap(self):
        cdict = {'red':  ((0.0, 0.0, 0.0),
             (1/6., 0.0, 0.0),
             (1/2., 0.8, 1.0),
             (5/6., 1.0, 1.0),
             (1.0, 0.4, 1.0)),

         'green':  ((0.0, 0.0, 0.4),
             (1/6., 1.0, 1.0),
             (1/2., 1.0, 0.8),
             (5/6., 0.0, 0.0),
             (1.0, 0.0, 0.0)),

         'blue': ((0.0, 0.0, 0.0),
             (1/6., 0.0, 0.0),
             (1/2., 0.9, 0.9),
             (5/6., 0.0, 0.0),
             (1.0, 0.0, 0.0))}

        return colors.LinearSegmentedColormap('rg', cdict, N=256)

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
        explains = self.__get_explaination(data)

        contribs = explains['contribs']
        results = pd.DataFrame(contribs, index=['contrib']).T

        input_data = pd.DataFrame(explains['input data'])
        results = results.join(input_data.T)
        results.rename(columns={0: "entrée du modèle"}, inplace=True)
        occupation_type_keys = [x for x in contribs.keys()
                                 if x not in explains['input data'].keys()]
        occup_contrib = results.loc[occupation_type_keys].sum(axis=0)[0]
        results = results.drop(occupation_type_keys, axis=0)
        occup_contrib = pd.DataFrame({'contrib': occup_contrib},
                                      index=['OCCUPATION_TYPE'])
        results = pd.concat([occup_contrib, results])
        base_val = {'contrib': explains['base_value']}
        base_val = pd.DataFrame(base_val, index=['base_value'])
        results = pd.concat([base_val, results], axis=0)
        results['contrib'] = results['contrib'] * 100

        results.loc['OCCUPATION_TYPE', 'entrée du modèle'] \
            = app['occupation_type']
        results.replace(np.nan, '', inplace=True)
        results = results[['entrée du modèle', 'contrib']]
        results.rename(index={"DAYS_BIRTH": 'AGE'}, inplace=True)
        st.markdown("Dans la table ci-dessous, la somme des contributions"
                    " correspond à la probabilité de non remboursement, "
                    "la *base value* est la moyenne pour un échantillon de 100"
                    " demandes de crédit."
                    " Chaque variable augmente ou diminue alors cette valeur.")
        st.table(results.style.background_gradient(cmap=self.cmap)\
                 .apply(lambda x: ['background-color: cyan'],
                    subset=pd.IndexSlice['base_value', ['contrib']]))
        st.info('Prédiction du modèle (Probabilité de non-remboursement) : %f %%'\
            % (results['contrib'].sum()))
        st.info('Probabilité de remboursement (100 - Prédiction du modèle) : %f %%' %
                        ((100 - results['contrib'].sum())))
        st.markdown(":warning: Ces résultats sont obtenus sur un échantillon"
                    " de 100 demandes. Ces derniers peuvent donc varier entre"
                    " deux exécutions.")
