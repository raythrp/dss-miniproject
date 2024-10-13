import streamlit as st
import numpy as np
import pandas as pd

# Initialize WP-specific session state if it doesn't exist
if 'wp_alternativesCount' not in st.session_state:
    st.session_state.wp_alternativesCount = 1
if 'wp_criteriaCount' not in st.session_state:
    st.session_state.wp_criteriaCount = 1
if 'wp_criteria_names' not in st.session_state:
    st.session_state.wp_criteria_names = ['Criteria 1', 'Criteria 2', 'Criteria 3', 'Criteria 4', 'Criteria 5']
if 'wp_criteria_types' not in st.session_state:
    st.session_state.wp_criteria_types = ['Cost', 'Benefit', 'Cost', 'Benefit', 'Cost']
if 'wp_weights' not in st.session_state:
    st.session_state.wp_weights = [5.0, 3.0, 4.0, 4.0, 2.0]
if 'wp_alternatives' not in st.session_state:
    st.session_state.wp_alternatives = ['Alternative 1', 'Alternative 2', 'Alternative 3']
if 'wp_scores' not in st.session_state:
    st.session_state.wp_scores = {}

def weight_product(criteria_weights, alternative_matrix, benefit_criteria):
    normalized_weights = criteria_weights / np.sum(criteria_weights)
    S = np.prod(alternative_matrix ** (normalized_weights * np.where(benefit_criteria, 1, -1)), axis=1)
    V = S / np.sum(S)
    return S, V

def wp_page():
    st.title("Weight Product Method")
    st.write("Thank you for choosing this method!")
    st.markdown('Please fill in all of the input blocks in the sidebar.')

    # Count inputs
    num_alternatives = st.session_state.wp_alternativesCount = st.sidebar.number_input("Number of Alternatives", min_value=2, max_value=10, value=st.session_state.wp_alternativesCount, key="wp_alt_count")
    num_criteria = st.session_state.wp_criteriaCount = st.sidebar.number_input("Number of Criteria", min_value=2, max_value=10, value=st.session_state.wp_criteriaCount, key="wp_crit_count")

    # Session state extends based on count inputs
    if len(st.session_state.wp_criteria_names) < num_criteria:
        st.session_state.wp_criteria_names.extend([f"Criteria {i+1}" for i in range(len(st.session_state.wp_criteria_names), num_criteria)])
    if len(st.session_state.wp_criteria_types) < num_criteria:
        st.session_state.wp_criteria_types.extend(["Cost"] * (num_criteria - len(st.session_state.wp_criteria_types)))
    if len(st.session_state.wp_weights) < num_criteria:
        st.session_state.wp_weights.extend([1.0] * (num_criteria - len(st.session_state.wp_weights)))
    if len(st.session_state.wp_alternatives) < num_alternatives:
        st.session_state.wp_alternatives.extend([f"Alternative {i+1}" for i in range(len(st.session_state.wp_alternatives), num_alternatives)])

    # Input criteria names and types (cost/benefit)
    criteria_names = []
    criteria_types = []
    for i in range(num_criteria):
        st.sidebar.title(f"Criteria {i+1}")
        criteria_name = st.session_state.wp_criteria_names[i] = st.sidebar.text_input(f"Criteria {i+1} Name", value=st.session_state.wp_criteria_names[i], key=f"wp_crit_name_{i}")
        criteria_names.append(st.session_state.wp_criteria_names[i])
        
        criteria_type = st.session_state.wp_criteria_types[i] = st.sidebar.selectbox(
            f"Type for {criteria_name}",
            options=["Benefit", "Cost"],
            index=0 if st.session_state.wp_criteria_types[i] == "Benefit" else 1,
            key=f"wp_crit_type_{i}"
        )
        criteria_types.append(st.session_state.wp_criteria_types[i])

    # Input criteria weights
    st.sidebar.title("Criteria Weights")
    weights = []
    for i in range(num_criteria):
        weight = st.session_state.wp_weights[i] = st.sidebar.number_input(f"Weight for {criteria_names[i]}", min_value=0.0, value=st.session_state.wp_weights[i], key=f"wp_weight_{i}")
        weights.append(weight)

    # Input alternatives and their scores
    alternatives = []
    for i in range(num_alternatives):
        st.sidebar.title(f"Alternative {i+1}")
        alt_name = st.session_state.wp_alternatives[i] = st.sidebar.text_input(f"Alternative {i+1} Name", value=st.session_state.wp_alternatives[i], key=f"wp_alt_name_{i}")
        alternatives.append(alt_name)
        
        # Specific alternative score storing in session state
        if alt_name not in st.session_state.wp_scores:
            st.session_state.wp_scores[alt_name] = [50.0] * num_criteria

        # Score session state adjustments based on count inputs
        if len(st.session_state.wp_scores[alt_name]) < num_criteria:
            st.session_state.wp_scores[alt_name].extend([50.0] * (num_criteria - len(st.session_state.wp_scores[alt_name])))
        elif len(st.session_state.wp_scores[alt_name]) > num_criteria:
            st.session_state.wp_scores[alt_name] = st.session_state.wp_scores[alt_name][:num_criteria]

        for j in range(num_criteria):
            score = st.session_state.wp_scores[alt_name][j] = st.sidebar.number_input(f"Score for {alt_name} in {criteria_names[j]}", min_value=0.0, max_value=100.0, value=st.session_state.wp_scores[alt_name][j], key=f"wp_score_{i}_{j}")

    if st.sidebar.button("Calculate", key="wp_calculate"):
        # Prepare data for calculation
        alternative_matrix = np.array([st.session_state.wp_scores[alt] for alt in alternatives])
        criteria_weights = np.array(weights)
        benefit_criteria = np.array([t == 'Benefit' for t in criteria_types])

        # Calculate results
        S, V = weight_product(criteria_weights, alternative_matrix, benefit_criteria)

        # Display results
        st.header("Weight Product Method Results")
        
        # Display input data
        st.subheader("Input Data")
        input_df = pd.DataFrame(alternative_matrix, columns=criteria_names, index=alternatives)
        st.write("Alternative Scores:")
        st.write(input_df)
        
        st.write("Criteria Weights:")
        weight_df = pd.DataFrame({'Criteria': criteria_names, 'Weight': weights, 'Type': criteria_types})
        st.write(weight_df)

        # S vector table
        st.subheader("Vector S")
        s_df = pd.DataFrame({'Alternative': alternatives, 'S Value': S})
        st.write(s_df)

        # V vector table
        st.subheader("Vector V (Final Normalized Scores)")
        v_df = pd.DataFrame({'Alternative': alternatives, 'V Value': V})
        v_df['Rank'] = v_df['V Value'].rank(ascending=False)
        v_df = v_df.sort_values('V Value', ascending=False)
        st.write(v_df)

        # Best alternative
        best_alternative = alternatives[np.argmax(V)]
        best_score = np.max(V)
        st.success(f"The best alternative is {best_alternative} with a score of {best_score:.4f}")

if _name_ == "_main_":
    wp_page()