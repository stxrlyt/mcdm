import streamlit as st
import numpy as np
import pandas as pd

# Define algorithm
def saw(matrix, weights, bencos):
    matrix = np.array(matrix, dtype=float) # Define matrix from input
    normalized = np.zeros_like(matrix) # Matrix for normalized values

    # Criteria normalization loop
    for j in range(matrix.shape[1]):
        if bencos[j] == 'Benefit':
            normalized[:, j] = matrix[:, j]/matrix[:, j].max()
        else:
            normalized[:, j] = matrix[:, j]/matrix[:, j].min()

    # Obtaining scores
    finalscore = np.dot(normalized, weights) # Multiply normalized values with each weight
    return finalscore.tolist() # Listing final scores

# Page metadata
st.set_page_config(
    page_title="SAW",
    page_icon="📊",
)

# Main user interface
st.title('Simple Additive Weighing (SAW)')

input_mode = st.radio("Please select input mode", ["Input", "Upload File"])

if input_mode == "Input":
    # Define number of criteria and alternative
    altamt = st.number_input("Alternatives", min_value=2, max_value=99, value=2)
    critamt = st.number_input("Criteria", min_value=2, max_value=99, value=2)

    # Enable/disable sub criterias
    use_subcriteria = st.checkbox("Do you need sub-criterias?", value=False)

    # Input alternatives
    alternatives=[]
    st.markdown("Define alternatives")
    for i in range (altamt):
        altname = st.text_input(f"Alternative {i+1}", key=f"alt_name_{i}")
        alternatives.append(altname)

    criteria = []
    column_weights = []
    column_types = []
    column_names = []

    altersdata = []

    # If we need sub-criterias
    if use_subcriteria:
        # Input criterias
        st.markdown("Define criterias and sub-criterias")
        for i in range(critamt):
            st.markdown(f"Criterion {i+1}")
            col1, col2, col3 = st.columns([4, 3, 3])
            with col1:
                critname = st.text_input(f"Main criteria name {i+1}", key=f"crit_name_{i}")
            with col2:
                critweight = st.number_input(f"Weight for {critname}", min_value=0.0, max_value=1.0, step=0.01, key=f"crit_weight_{i}")
            with col3:
                subcritsamt = st.number_input(f"Number of sub-criterias for {critname}", min_value=0, max_value=10, value=1, key=f"subcritamt_{i}")

            subcrits = []
            for j in range(subcritsamt):
                st.markdown(f"Sub-criteria {j+1}")
                cols1, cols2, cols3 = st.columns([4, 3, 3])
                with cols1:
                    subname = st.text_input(f"Sub-criteria name {j+1} for {critname}", key=f"subname_{i}_{j}")
                with cols2:
                    subweight = st.number_input(f"{subname}'s weight", min_value=0.0, max_value=1.0, step=0.01, key=f"subweight_{i}_{j}")
                with cols3:
                    subtype = st.selectbox(f"Type {j+1}", ["Benefit", "Cost"], key=f"subtype_{i}_{j}")
                subcrits.append((subname, subweight, subtype))

            totalsubw = sum([w for _, w, _ in subcrits])
            for subname, subweight, subtype in subcrits:
                effectivew = critweight * (subweight / totalsubw if totalsubw != 0 else 0)
                column_weights.append(effectivew)
                column_types.append(subtype)
                column_names.append(f"{critname} - {subname}")

            row = []
            altersdata.append(row)

        altersdata = np.array(altersdata).T

    else:
        # Input criterias
        st.markdown("Define criterias")
        for i in range(critamt):
            col1, col2, col3 = st.columns([4, 3, 3])
            with col1:
                critname = st.text_input(f"Criterion {i+1}", key=f"crit_name_{i}")
            with col2:
                bencos = st.selectbox(f"Type {i+1}", ["Benefit", "Cost"], key=f"crit_type_{i}")
            with col3:
                weights = st.number_input(f"Weight {i+1}", min_value=0.00, max_value=1.0, key=f"crit_weight_{i}")
            criteria.append((critname, bencos, weights)) 

        # Create matrix by inputting alternatives' data
        st.markdown("Input alternatives' data")
        for alt_idx, alt in enumerate(alternatives):
            st.markdown(f"{alt}")

            cols = st.columns(len(criteria))
            row = []

            for crit_idx, (name, _, _) in enumerate(criteria):
                with cols[crit_idx]:
                    val = st.number_input(f"{alt} - {name}", key=f"val_{alt_idx}_{crit_idx}")
                    row.append(val)
            altersdata.append(row)

    # Computing time!
    if st.button("Compute"):
        try:
            matrix = np.array(altersdata)
            weights = np.array([w for _, _, w in criteria])
            bencos = [t for _, t, _ in criteria]

            # If criteria weights don't add up to 1
            if not np.isclose(weights.sum(), 1.0):
                st.warning("Weights do not add up to 1. Please normalize at the normalization page prior.")

            if 'weights' in st.session_state:
                weights = st.session_state.weights

            # Run SAW function
            scores = saw(matrix, weights, bencos)

            # Showcase results
            results = pd.DataFrame({"alternatives": alternatives, "score": scores})
            results = results.sort_values(by="score", ascending = False)
            results['Rank'] = range(1, len(results) + 1)
            results = results[['Rank', 'alternatives', 'score']]
            st.write("Results")
            st.dataframe(results)
    
        except Exception as e:
            st.error(f"error: {e}")

else: 
    criteria_file = st.file_uploader("Upload Criteria CSV (Criteria, Weight, Type)", type=["csv"])
    alternatives_file = st.file_uploader("Upload Alternatives CSV (Alternative, Criterias' Columns...)", type=["csv"])

    try:
        # Read criteria file
        criteria_df = pd.read_csv(criteria_file)
        st.write("Criterias")
        st.dataframe(criteria_df)

        # Validate criteria file structure
        required_cols = {'Criteria', 'Weight', 'Type'}
        if not required_cols.issubset(set(criteria_df.columns)):
            st.error(f"Criteria CSV must contain columns: {required_cols}")
        else:
            weights = criteria_df['Weight'].values.astype(float)
            bencos = criteria_df['Type'].values.astype(str)

            # Normalize weights if not sum to 1
            if not np.isclose(weights.sum(), 1.0):
                weights = weights / weights.sum()
                st.info("Weights normalized")

            # Read alternatives file
            alt_df = pd.read_csv(alternatives_file)
            st.write("Alternatives Data")
            st.dataframe(alt_df)

            alternatives = alt_df.iloc[:, 0].astype(str).tolist()
            matrix = alt_df.iloc[:, 1:].values.astype(float)

            # Check if columns in alternatives match criteria names
            crit_names_alt = alt_df.columns[1:].tolist()
            crit_names_criteria = criteria_df['Criteria'].tolist()

            if crit_names_alt != crit_names_criteria:
                st.warning("Warning: Criteria columns in alternatives CSV do not match the criteria names CSV order.")

            if st.button("Compute"):
                scores = saw(matrix, weights, bencos)
                results = pd.DataFrame({
                    "Alternative": alternatives,
                    "Score": scores
                }).sort_values(by="Score", ascending=False)
                results["Rank"] = range(1, len(results)+1)
                st.dataframe(results[["Rank", "Alternative", "Score"]])

    except Exception as e:
        st.error(f"Error processing files: {e}")
