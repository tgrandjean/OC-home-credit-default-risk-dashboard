import os
import streamlit as st


LOCAL_PATH = os.path.dirname(os.path.abspath(__file__))


class Home:

    def __init__(self):
        st.markdown(self.content)

    @property
    def content(self):
        return self.__get_content()

    @st.cache
    def __get_content(self):
        with open(os.path.join(LOCAL_PATH, 'assets', 'home.txt'), 'rb') as f:
            return f.read().decode('utf8')
