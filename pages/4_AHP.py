import streamlit as st
import numpy as np
import pandas as pd

def calculate_ahp(matrix):
    matrix = np.array(matrix, dtype=float)
    normalized = matrix / matrix.sum(axis=0)
    weights = normalized.mean(axis=1)

    lambdamax = np.sum((matrix @ weights) / weights) / len(weights)
    conin = (lambdamax - len(weights)) / (len(weights) - 1)

    ridict = {1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
              6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49}
    randin = ridict.get(len(weights), 1.49)
    conrat = conin / randin if randin != 0 else 0

    return weights.tolist(), conrat

def ahp(criteria_matrix, alternative_matrices):
    criteria_weights, criteria_conrat = calculate_ahp(criteria_matrix)

    alt_weights_all = []
    alt_conrats = []

    for alt_matrix in alternative_matrices:
        weights, conrat = calculate_ahp(alt_matrix)
        alt_weights_all.append(weights)
        alt_conrats.append(conrat)

    alt_weights_all = np.array(alt_weights_all)
    final_scores = np.dot(criteria_weights, alt_weights_all)

    return final_scores.tolist(), criteria_weights, criteria_conrat, alt_conrats

st.set_page_config(
    page_title="AHP",
    page_icon="🆚",
)

st.title('Analytic Hierarchy Process (AHP)')
altno = st.number_input("Number of alternatives", min_value=2, max_value=99, value=3)
criteriano = st.number_input("Number of criteria", min_value=2, max_value=99, value=3)

alternatives = []
st.markdown("Define alternatives")
for i in range(altno):
    altname = st.text_input(f"Alternative {i+1}", key=f"alt_name_{i}")
    alternatives.append(altname)

criteria = []
st.markdown("Define criteria")
for i in range(criteriano):
    criterianame = st.text_input(f"Criterion {i+1}", key=f"crit_name_{i}")
    criteria.append(criterianame)

criteria_matrix = []
st.markdown("### Criteria Pairwise Comparison Matrix")
for i in range(criteriano):
    cols = st.columns(criteriano)
    row = []
    for j in range(criteriano):
        if i == j:
            val = 1.0
            cols[j].number_input(f"{criteria[i]} vs {criteria[j]}", value=1.0, disabled=True, key=f"crit_{i}_{j}")
        elif i < j:
            val = cols[j].number_input(f"{criteria[i]} vs {criteria[j]}", min_value=0.01, max_value=9.0, step=1.0, key=f"crit_{i}_{j}")
        else:
            val = 1 / criteria_matrix[j][i]
            cols[j].number_input(f"{criteria[i]} vs {criteria[j]}", value=round(val, 3), disabled=True, key=f"crit_{i}_{j}")
        row.append(val)
    criteria_matrix.append(row)

alternative_matrices = []
for c_idx, crit_name in enumerate(criteria):
    st.markdown(f"### Alternative Comparisons for Criterion: {crit_name}")
    matrix = []
    for i in range(altno):
        cols = st.columns(altno)
        row = []
        for j in range(altno):
            if i == j:
                val = 1.0
                cols[j].number_input(f"{alternatives[i]} vs {alternatives[j]} ({crit_name})", value=1.0, disabled=True, key=f"alt_{c_idx}_{i}_{j}")
            elif i < j:
                val = cols[j].number_input(
                    f"{alternatives[i]} vs {alternatives[j]} ({crit_name})",
                    min_value=0.01, max_value=9.0, step=1.0,
                    key=f"alt_{c_idx}_{i}_{j}"
                )
            else:
                val = 1 / matrix[j][i]
                cols[j].number_input(
                    f"{alternatives[i]} vs {alternatives[j]} ({crit_name})",
                    value=round(val, 3), disabled=True,
                    key=f"alt_{c_idx}_{i}_{j}"
                )
            row.append(val)
        matrix.append(row)
    alternative_matrices.append(matrix)

if st.button("Compute"):
    try:
        final_scores, crit_weights, crit_conrat, alt_conrats = ahp(criteria_matrix, alternative_matrices)

        st.subheader("Final Scores")
        results = pd.DataFrame({
            "Alternative": alternatives,
            "Score": final_scores
        }).sort_values(by="Score", ascending=False).reset_index(drop=True)
        results.index += 1
        st.dataframe(results)

        st.write(f"**Criteria Consistency Ratio:** {crit_conrat:.4f}")
        for i, conrat in enumerate(alt_conrats):
            st.write(f"{criteria[i]} Alternative Matrix Consistency Ratio: {conrat:.4f}")
            if conrat > 0.1:
                st.warning(f"Consistency ratio for {criteria[i]} > 0.1. Consider revising your comparisons.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
