import streamlit as st
import numpy as np
import pandas as pd

def calculate_consistency_ratio(matrix, n):
    eigenvalues = np.linalg.eigvals(matrix)
    lambda_max = max(eigenvalues.real)
    consistency_index = (lambda_max - n) / (n - 1)
    random_index = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    consistency_ratio = consistency_index / random_index[n]
    return consistency_ratio

def create_comparison_matrix(labels, prefix):
    n = len(labels)
    
    # Check if matrix already exists in session state, otherwise create a new one
    if f"{prefix}_matrix" not in st.session_state:
        st.session_state[f"{prefix}_matrix"] = np.ones((n, n))
    else:
        # Resize matrix if the number of labels has changed
        matrix = st.session_state[f"{prefix}_matrix"]
        if matrix.shape[0] != n or matrix.shape[1] != n:
            st.session_state[f"{prefix}_matrix"] = np.ones((n, n))  # Reinitialize to ones with new size
    
    matrix = st.session_state[f"{prefix}_matrix"]
    
    for i in range(n):
        for j in range(i+1, n):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"{labels[i]} vs {labels[j]}")
            with col2:
                key = f"{prefix}{labels[i]}{labels[j]}"
                value = st.number_input(
                    f"Importance",
                    min_value=1/9,
                    max_value=9.0,
                    value=matrix[i, j],
                    step=0.1,
                    key=key,
                    on_change=update_matrix,
                    args=(prefix, i, j, key)
                )
            matrix[i, j] = value
            matrix[j, i] = 1 / value
    
    return matrix

def update_matrix(prefix, i, j, key):
    value = st.session_state[key]
    st.session_state[f"{prefix}_matrix"][i, j] = value
    st.session_state[f"{prefix}_matrix"][j, i] = 1 / value

def initialize_session_state():
    if 'num_criteria' not in st.session_state:
        st.session_state.num_criteria = 5
    if 'num_alternatives' not in st.session_state:
        st.session_state.num_alternatives = 3
    if 'ahp_criteria' not in st.session_state:
        st.session_state.ahp_criteria = [f'C{i+1:02d}' for i in range(st.session_state.num_criteria)]
    if 'ahp_alternatives' not in st.session_state:
        st.session_state.ahp_alternatives = [f'A{i+1:02d}' for i in range(st.session_state.num_alternatives)]

def reset_session_state():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

def ahp_page():
    st.title("Analytical Hierarchy Process (AHP)")
    st.write("This application helps you perform AHP calculations.")

    initialize_session_state()

    # Input for criteria and alternatives
    st.sidebar.header("AHP Parameters")
    num_criteria = st.sidebar.number_input("Number of Criteria", min_value=2, max_value=10, value=st.session_state.num_criteria, key="ahp_num_criteria")
    num_alternatives = st.sidebar.number_input("Number of Alternatives", min_value=2, max_value=10, value=st.session_state.num_alternatives, key="ahp_num_alternatives")

    # Update criteria and alternatives lists dynamically based on user input
    if len(st.session_state.ahp_criteria) != num_criteria:
        st.session_state.ahp_criteria = [f'C{i+1:02d}' for i in range(num_criteria)]
        st.session_state.num_criteria = num_criteria
    if len(st.session_state.ahp_alternatives) != num_alternatives:
        st.session_state.ahp_alternatives = [f'A{i+1:02d}' for i in range(num_alternatives)]
        st.session_state.num_alternatives = num_alternatives

    # Input for criteria names
    st.sidebar.header("Criteria Names")
    for i in range(st.session_state.num_criteria):
        st.session_state.ahp_criteria[i] = st.sidebar.text_input(f"Criterion {i+1}", value=st.session_state.ahp_criteria[i], key=f"ahp_criterion_{i}")

    # Input for alternative names
    st.sidebar.header("Alternative Names")
    for i in range(st.session_state.num_alternatives):
        st.session_state.ahp_alternatives[i] = st.sidebar.text_input(f"Alternative {i+1}", value=st.session_state.ahp_alternatives[i], key=f"ahp_alternative_{i}")

    # Pairwise comparison for criteria
    st.header("Pairwise Comparison of Criteria")
    criteria_matrix = create_comparison_matrix(st.session_state.ahp_criteria, "criteria")

    # Display criteria matrix
    st.subheader("Criteria Comparison Matrix")
    criteria_df = pd.DataFrame(criteria_matrix, columns=st.session_state.ahp_criteria, index=st.session_state.ahp_criteria)
    st.write(criteria_df)

    # Pairwise comparison for alternatives with respect to each criterion
    alternative_matrices = []
    for k, criterion in enumerate(st.session_state.ahp_criteria):
        st.header(f"Pairwise Comparison of Alternatives with respect to {criterion}")
        alt_matrix = create_comparison_matrix(st.session_state.ahp_alternatives, f"alt_{k}")
        alternative_matrices.append(alt_matrix)

        # Display alternative matrix for each criterion
        st.subheader(f"Alternative Comparison Matrix for {criterion}")
        alt_df = pd.DataFrame(alt_matrix, columns=st.session_state.ahp_alternatives, index=st.session_state.ahp_alternatives)
        st.write(alt_df)

    if st.button("Calculate AHP"):
        # Calculate weights for criteria
        criteria_weights = np.mean(criteria_matrix / np.sum(criteria_matrix, axis=0), axis=1)

        # Calculate consistency ratio for criteria
        cr_criteria = calculate_consistency_ratio(criteria_matrix, num_criteria)

        # Calculate weights for alternatives with respect to each criterion
        alternative_weights = []
        cr_alternatives = []
        for alt_matrix in alternative_matrices:
            weights = np.mean(alt_matrix / np.sum(alt_matrix, axis=0), axis=1)
            alternative_weights.append(weights)
            cr_alternatives.append(calculate_consistency_ratio(alt_matrix, num_alternatives))

        # Calculate final scores
        final_scores = np.dot(np.array(alternative_weights).T, criteria_weights)

        # Display results
        st.header("Results")

        st.subheader("Criteria Weights")
        criteria_df = pd.DataFrame({
            'Criterion': st.session_state.ahp_criteria,
            'Weight': criteria_weights
        })
        st.write(criteria_df)
        st.write(f"Consistency Ratio for Criteria: {cr_criteria:.4f}")
        if cr_criteria > 0.1:
            st.warning("The consistency ratio for criteria is greater than 0.1. Consider revising your judgments.")

        st.subheader("Alternative Weights for each Criterion")
        for i, criterion in enumerate(st.session_state.ahp_criteria):
            st.write(f"For {criterion}:")
            alt_df = pd.DataFrame({
                'Alternative': st.session_state.ahp_alternatives,
                'Weight': alternative_weights[i]
            })
            st.write(alt_df)
            st.write(f"Consistency Ratio: {cr_alternatives[i]:.4f}")
            if cr_alternatives[i] > 0.1:
                st.warning(f"The consistency ratio for {criterion} is greater than 0.1. Consider revising your judgments.")

        st.subheader("Final Scores")
        final_df = pd.DataFrame({
            'Alternative': st.session_state.ahp_alternatives,
            'Score': final_scores
        })
        final_df = final_df.sort_values('Score', ascending=False)
        final_df['Rank'] = final_df['Score'].rank(ascending=False, method='min')
        st.write(final_df)

        st.success(f"The best alternative is {final_df.iloc[0]['Alternative']} with a score of {final_df.iloc[0]['Score']:.4f}")

if _name_ == "_main_":
    ahp_page()