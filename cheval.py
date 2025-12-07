import streamlit as st
import os

pg = st.navigation([st.Page("About.py"), st.Page("Gallery.py")])
pg.run()
