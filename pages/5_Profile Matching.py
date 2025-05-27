import streamlit as st
import numpy as np
import pandas as pd

gap_weight_table = {
    0: 5.0,
    -1: 4.5, 1: 4.5,
    -2: 4.0, 2: 4.0,
    -3: 3.5, 3: 3.5,
    -4: 3.0, 4: 3.0
}

def profile_matching(actual_scores, ideal_scores, gap_weight_table, factor_weights):
    gap_scores = []
    for actual, ideal in zip(actual_scores, ideal_scores):
        gap = int(actual - ideal)
        if gap not in gap_weight_table:
            if gap > max(gap_weight_table.keys()):
                gap = max(gap_weight_table.keys())
            elif gap < min(gap_weight_table.keys()):
                gap = min(gap_weight_table.keys())
        gap_scores.append(gap_weight_table[gap])
    weighted_scores = [score * weight for score, weight in zip(gap_scores, factor_weights)]
    return sum(weighted_scores)

st.set_page_config(
    page_title="Profile Matching", 
    page_icon="🆚"
)

st.title('Profile Matching')

altno = st.number_input("Number of alternatives", min_value=2, max_value=20, value=3)
criteriano = st.number_input("Number of criteria", min_value=2, max_value=20, value=3)

st.markdown("Define criteria")
criteria = []
for i in range(criteriano):
    col1, col2 = st.columns([4,3])
    with col1:
        critname = st.text_input(f"Criterion {i+1}", key=f"crit_name_{i}")
    with col2:
        grouping = st.selectbox(f"Grouping Factor {i+1}", ["Core", "Secondary"], key=f"crit_type_{i}")
    criteria.append((critname, grouping))

st.markdown("Set Core factor/Secondary factor weight")
core_weight = st.slider("Core factor weight", 0.0, 1.0, 0.6, 0.01)
sec_weight = 1 - core_weight
st.write(f"Secondary factor weight: {sec_weight:.2f}")

st.markdown("Define alternatives")
alternatives = []
for i in range(altno):
    altname = st.text_input(f"Alternative {i+1}", key=f"alt_name_{i}")
    alternatives.append(altname)

st.markdown("Input ideal profile values")
ideal_profile = []
cols = st.columns(criteriano)
for i in range(criteriano):
    with cols[i]:
        val = st.number_input(f"Ideal for {criteria[i][0]}", key=f"ideal_{i}")
        ideal_profile.append(val)

st.markdown("Input alternatives' data")
altersdata = []
for alt_idx, alt in enumerate(alternatives):
    st.markdown(f"**{alt}**")
    cols = st.columns(criteriano)
    row = []
    for crit_idx, (name, _) in enumerate(criteria):
        with cols[crit_idx]:
            val = st.number_input(f"{alt} - {name}", key=f"val_{alt_idx}_{crit_idx}")
            row.append(val)
    altersdata.append(row)

if st.button("Compute"):
    try:
        core_indices = [i for i, (_, g) in enumerate(criteria) if g == "Core"]
        sec_indices = [i for i, (_, g) in enumerate(criteria) if g == "Secondary"]

        # Equal weights inside each group
        core_weights = [1 / len(core_indices)] * len(core_indices) if core_indices else []
        sec_weights = [1 / len(sec_indices)] * len(sec_indices) if sec_indices else []

        results = []
        for alt_idx, alt in enumerate(alternatives):
            row = altersdata[alt_idx]

            core_actual = [row[i] for i in core_indices]
            core_ideal = [ideal_profile[i] for i in core_indices]

            sec_actual = [row[i] for i in sec_indices]
            sec_ideal = [ideal_profile[i] for i in sec_indices]

            core_score = profile_matching(core_actual, core_ideal, gap_weight_table, core_weights) if core_weights else 0
            sec_score = profile_matching(sec_actual, sec_ideal, gap_weight_table, sec_weights) if sec_weights else 0

            final_score = core_score * core_weight + sec_score * sec_weight
            results.append((alt, final_score))

        results.sort(key=lambda x: x[1], reverse=True)
        df = pd.DataFrame(results, columns=["Alternative", "Final Score"])
        df["Rank"] = range(1, len(df) + 1)
        st.dataframe(df[["Rank", "Alternative", "Final Score"]])

    except Exception as e:
        st.error(f"❌ Error: {e}")
