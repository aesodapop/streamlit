import streamlit as st

about = st.Page("pages/about.py", title="About", icon=":material/about:", default=True)
gallery = st.Page("pages/gallery.py", title="Gallery", icon=":material/gallery:", default=False)

pg = st.navigation({"Cheval": [about, gallery]})

pg.run()
