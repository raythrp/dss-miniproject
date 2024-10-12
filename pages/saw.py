import streamlit as st
import pandas as pd

# Initialize session state if it doesn't exist
if 'alternativesCount' not in st.session_state:
    st.session_state.alternativesCount = 1
if 'criteriaCount' not in st.session_state:
    st.session_state.criteriaCount = 1
if 'criteria_names' not in st.session_state:
    st.session_state.criteria_names = ['Criteria 1']
if 'criteria_types' not in st.session_state:
    st.session_state.criteria_types = ['Benefit']
if 'weights' not in st.session_state:
    st.session_state.weights = [0.00]
if 'alternatives' not in st.session_state:
    st.session_state.alternatives = ['Alternative 1']
if 'scores' not in st.session_state:
    st.session_state.scores = {}

# Count inputs
num_alternatives = st.session_state.alternativesCount = st.sidebar.number_input("Number of Alternatives", min_value=1, max_value=10, value=st.session_state.alternativesCount)
num_criteria = st.session_state.criteriaCount = st.sidebar.number_input("Number of Criteria", min_value=1, max_value=10, value=st.session_state.criteriaCount)

# Session state extends based on count inputs
if len(st.session_state.criteria_names) < num_criteria:
    st.session_state.criteria_names.extend([f"Criteria {i+1}" for i in range(len(st.session_state.criteria_names), num_criteria)])
if len(st.session_state.criteria_types) < num_criteria:
    st.session_state.criteria_types.extend(["Benefit"] * (num_criteria - len(st.session_state.criteria_types)))
if len(st.session_state.weights) < num_criteria:
    st.session_state.weights.extend([0.00] * (num_criteria - len(st.session_state.weights)))
if len(st.session_state.alternatives) < num_alternatives:
    st.session_state.alternatives.extend([f"Alternative {i+1}" for i in range(len(st.session_state.alternatives), num_alternatives)])

# Input criteria names and types (cost/benefit)
criteria_names = []
criteria_types = []
for i in range(num_criteria):
    st.sidebar.title(f"Criteria {i+1}")
    criteria_name = st.session_state.criteria_names[i] = st.sidebar.text_input(f"Criteria {i+1} Name", value=st.session_state.criteria_names[i])
    criteria_names.append(st.session_state.criteria_names[i])
    
    criteria_type = st.session_state.criteria_types[i] = st.sidebar.selectbox(
        f"Type for {criteria_name}",
        options=["Benefit", "Cost"],
        index=0 if st.session_state.criteria_types[i] == "Benefit" else 1,
    )
    criteria_types.append(st.session_state.criteria_types[i])

# Input criteria weights
st.sidebar.title("Criteria Weights")
weights = []
total_weight = 0.0
for i in range(num_criteria):
    weight = st.session_state.weights[i] = st.sidebar.number_input(f"Weight for {criteria_names[i]}", min_value=0.0, max_value=1.0, value=st.session_state.weights[i])
    weights.append(weight)
    total_weight += weight

st.sidebar.warning("Please adjust weights until equals 1.")

# Input alternatives and their scores
alternatives = []
for i in range(num_alternatives):
    st.sidebar.title(f"Alternative {i+1}")
    alt_name = st.session_state.alternatives[i] = st.sidebar.text_input(f"Alternative {i+1} Name", value=st.session_state.alternatives[i])
    alternatives.append(alt_name)
    
    # Specific alternative score storing in session state
    if alt_name not in st.session_state.scores:
        st.session_state.scores[alt_name] = [50.0] * num_criteria

    # Score session state adjustments based on count inputs
    if len(st.session_state.scores[alt_name]) < num_criteria:
        st.session_state.scores[alt_name].extend([50.0] * (num_criteria - len(st.session_state.scores[alt_name])))
    elif len(st.session_state.scores[alt_name]) > num_criteria:
        st.session_state.scores[alt_name] = st.session_state.scores[alt_name][:num_criteria]

    for j in range(num_criteria):
        score = st.session_state.scores[alt_name][j] = st.sidebar.number_input(f"Score for {alt_name} in {criteria_names[j]}", min_value=0.0, max_value=100.0, value=st.session_state.scores[alt_name][j])

# Normalise
def saw_method(criteria, weights, scores, criteria_types):
    # Convert session scores from dict to table
    scores_dict = {alt: st.session_state.scores[alt] for alt in alternatives}
    df = pd.DataFrame.from_dict(scores_dict, orient='index', columns=criteria)
    
    # Display scores
    st.write("Scores", df)
    
    # Normalising based on criteria types
    normalized_df = pd.DataFrame(index=df.index, columns=df.columns)
    for i, crit_type in enumerate(criteria_types):
        if crit_type == "Benefit":
            normalized_df.iloc[:, i] = df.iloc[:, i] / df.iloc[:, i].max()
        else:    # Cost
            normalized_df.iloc[:, i] = df.iloc[:, i].min() / df.iloc[:, i]
    
    # Display normalised table
    st.write("Normalised", normalized_df)
    
    saw_scores = normalized_df.dot(weights)  # Weighted sum
    
    # Rank the alternatives based on the final scores
    final_scores = pd.DataFrame(saw_scores, columns=["Final Score"])
    final_scores['Rank'] = final_scores['Final Score'].rank(ascending=False)
    final_scores = final_scores.sort_values(by='Final Score', ascending=False)
    
    # Display chosen alternative
    chosen = final_scores.index[0]
    
    return final_scores, chosen


st.title("Simple Additive Weighting")
st.write("Thank you for choosing this method!")
st.markdown('Please fill in all of the input blocks and pay attention to the :orange[warnings!]')

# Display results
if st.sidebar.button("Calculate") and total_weight == 1:
    st.header("Result")
    result, chosen = saw_method(criteria_names, weights, st.session_state.scores, criteria_types)
    
    st.write("Rankings")
    st.write(result)
    
    st.success(f"The chosen alternative is {chosen}")
elif total_weight != 1:
    st.subheader(':orange[Warnings]')
    st.warning(f"Cannot calculate SAW results because the total weight is not 1, it's :orange[{total_weight}]")