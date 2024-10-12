import streamlit as st
import pandas as pd

# Initialize session state if it doesn't exist
if 'alternatives' not in st.session_state:
    st.session_state.alternatives = []
if 'criteria' not in st.session_state:
    st.session_state.criteria = []
if 'weights' not in st.session_state:
    st.session_state.weights = []
if 'scores' not in st.session_state:
    st.session_state.scores = {}

# Sidebar input
num_criteria = st.sidebar.number_input("Number of Criteria", min_value=1, max_value=10, value=3)
num_alternatives = st.sidebar.number_input("Number of Alternatives", min_value=1, max_value=10, value=3)

# Input criteria names and types (cost/benefit)
st.sidebar.title("Criteria Names and Types:")
criteria_names = []
criteria_types = []
for i in range(num_criteria):
    criteria_name = st.sidebar.text_input(f"Criteria {i+1} Name", value=f"Criteria {i+1}")
    criteria_names.append(criteria_name)
    
    # Cost or Benefit selection
    criteria_type = st.sidebar.selectbox(
        f"Type for {criteria_name}",
        options=["Benefit", "Cost"],
        index=0
    )
    criteria_types.append(criteria_type)

# Input criteria weights
st.sidebar.title("Criteria Weights (sum must not exceed 1):")
weights = []
total_weight = 0.0
for i in range(num_criteria):
    weight = st.sidebar.number_input(f"Weight for {criteria_names[i]}", min_value=0.0, max_value=1.0, value=0.33)
    weights.append(weight)
    total_weight += weight

# Flash error if the total weight exceeds 1
if total_weight > 1:
    st.sidebar.error("The total weight exceeds 1. Please adjust the weights.")

# Input alternatives and their scores for each criterion
st.sidebar.title("Alternatives and Scores:")
alternatives = []
for i in range(num_alternatives):
    alt_name = st.sidebar.text_input(f"Alternative {i+1} Name", value=f"Alternative {i+1}")
    alternatives.append(alt_name)
    st.session_state.scores[alt_name] = []
    for j in range(num_criteria):
        score = st.sidebar.number_input(f"Score for {alt_name} in {criteria_names[j]}", min_value=0.0, max_value=100.0, value=50.0)
        st.session_state.scores[alt_name].append(score)

# Normalize and calculate SAW scores
def saw_method(criteria, weights, scores, criteria_types):
    # Convert session scores from dict to dataframe
    scores_dict = {alt: st.session_state.scores[alt] for alt in alternatives}
    df = pd.DataFrame.from_dict(scores_dict, orient='index', columns=criteria)
    
    # Debug: Check dataframe
    st.write("Score DataFrame", df)
    
    # Normalize scores based on whether they are costs or benefits
    normalized_df = pd.DataFrame(index=df.index, columns=df.columns)
    for i, crit_type in enumerate(criteria_types):
        if crit_type == "Benefit":
            normalized_df.iloc[:, i] = df.iloc[:, i] / df.iloc[:, i].max()  # Benefit normalization
        else:  # Cost
            normalized_df.iloc[:, i] = df.iloc[:, i].min() / df.iloc[:, i]  # Cost normalization
    
    # Debug: Check normalized dataframe
    st.write("Normalized DataFrame", normalized_df)
    
    saw_scores = normalized_df.dot(weights)  # Calculate weighted sum
    
    # Create a DataFrame with the final scores
    final_scores = pd.DataFrame(saw_scores, columns=["Final Score"])
    
    # Rank the alternatives based on the final scores
    final_scores['Rank'] = final_scores['Final Score'].rank(ascending=False)
    
    # Sort by the rank (highest score first)
    final_scores = final_scores.sort_values(by='Final Score', ascending=False)
    
    # Determine the winner
    winner = final_scores.index[0]
    
    return final_scores, winner

# Display results
if st.sidebar.button("Calculate") and total_weight <= 1:
    result, winner = saw_method(criteria_names, weights, st.session_state.scores, criteria_types)
    
    st.write("Rankings")
    st.write(result)
    
    st.success(f"The chosen alternative is {winner}")
elif total_weight > 1:
    st.error("Cannot calculate SAW results because the total weight exceeds 1.")
