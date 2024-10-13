import streamlit as st
import numpy as np
import pandas as pd
from pages.wp import wp_page  # Sesuaikan sesuai path


st.set_page_config(page_title="Decision Support System", layout="wide")

st.title("Decision Support System")

# Input untuk jumlah alternatif dan kriteria
num_alternatives = st.number_input("Number of Alternatives", min_value=2, value=3, step=1)
num_criteria = st.number_input("Number of Criteria", min_value=2, value=5, step=1)

# Buat dataframe kosong untuk input
df = pd.DataFrame(np.zeros((num_alternatives, num_criteria)), 
                  columns=[f'C{i+1}' for i in range(num_criteria)],
                  index=[f'A{i+1}' for i in range(num_alternatives)])

# Tampilkan dataframe sebagai tabel yang dapat diedit
st.write("Enter values for each alternative and criterion:")
edited_df = st.data_editor(df)

# Input untuk bobot kriteria
st.subheader("Criteria Weights")
weights = st.text_input("Enter criteria weights (comma-separated)", value="5,3,4,4,2")
weights = [float(w.strip()) for w in weights.split(',') if w.strip()]

# Input untuk tipe kriteria
st.subheader("Criteria Types")
criteria_types = st.text_input("Enter criteria types (benefit/cost, comma-separated)", value="cost,benefit,cost,benefit,cost")
criteria_types = [t.strip().lower() for t in criteria_types.split(',') if t.strip()]

# Pilihan metode perhitungan
method = st.selectbox("Select calculation method", ["Weight Product (WP)"])

if st.button("Calculate"):
    if len(weights) != num_criteria or len(criteria_types) != num_criteria:
        st.error("Number of weights and criteria types must match the number of criteria.")
    else:
        # Convert dataframe to numpy array
        alternative_matrix = edited_df.to_numpy()
        criteria_weights = np.array(weights)
        benefit_criteria = np.array([t == 'benefit' for t in criteria_types])

        # Lakukan perhitungan jika metode yang dipilih adalah WP
        if method == "Weight Product (WP)":
            wp_page(criteria_weights, alternative_matrix, benefit_criteria)