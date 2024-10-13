import streamlit as st

if 'show_flash' not in st.session_state:
    st.session_state.show_flash = False

st.title("Decision Support System Mini Project")
st.markdown("""
### Welcome to the App

This application provides several decision-making methods to help you with multi-criteria decision problems.""")

st.subheader("Available Methods")

if st.button("Analytic Hierarchy Process (AHP)"):
    st.session_state.show_flash = True

if st.button("Simple Additive Weighting (SAW)"):
    st.session_state.show_flash = True

if st.button("TOPSIS"):
    st.session_state.show_flash = True

if st.button("Weighted Product (WP)"):
    st.session_state.show_flash = True

if st.session_state.show_flash:
    st.info("Please select the method from the sidebar")
st.markdown("---")
st.markdown("Built for Ujian Tengah Semester Decision Support System")
