import streamlit as st
import numpy as np
import pandas as pd

def weight_product(criteria_weights, alternative_matrix, benefit_criteria):
    normalized_weights = criteria_weights / np.sum(criteria_weights)
    S = np.prod(alternative_matrix ** (normalized_weights * np.where(benefit_criteria, 1, -1)), axis=1)
    V = S / np.sum(S)
    return S, V

def wp_page(criteria_weights, alternative_matrix, benefit_criteria):
    # Calculate results
    S, V = weight_product(criteria_weights, alternative_matrix, benefit_criteria)

    # Prepare results
    results = {
        'S': S.tolist(),
        'V': V.tolist(),
        'best_alternative': np.argmax(V) + 1,
        'best_score': float(max(V))
    }

    # Display results
    st.subheader("Weight Product Method Results")
    
    # S vector table
    st.write("Vector S:")
    s_df = pd.DataFrame({'Alternative': [f'A{i+1}' for i in range(len(S))], 'S Value': S})
    st.table(s_df)

    # V vector table
    st.write("Vector V (Final Normalized Scores):")
    v_df = pd.DataFrame({'Alternative': [f'A{i+1}' for i in range(len(V))], 'V Value': V})
    st.table(v_df)

    # Best alternative
    st.success(f"The best alternative is A{results['best_alternative']} with a score of {results['best_score']:.4f}")

    return results