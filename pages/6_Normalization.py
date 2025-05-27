import streamlit as st
import numpy as np
import pandas as pd

st.set_page_config(
    page_title="Normalization",
    page_icon="💯",
)

st.title('Weight Normalization Calculator')
st.markdown('Write the amount of criterias to be normalized')
critamt = st.number_input("Criteria", min_value=2, max_value=20, value=2)

criteria = []
weights = []

st.markdown("Define criteria name and weight")
for i in range (critamt):
    col1, col2 = st.columns([5, 5])
    with col1:
        critname = st.text_input(f"Criteria {i+1}", key=f"crit_name_{i}")
    with col2:
        critweight = st.number_input(f"Weight {i+1}", key=f"crit_weight_{i}")

    criteria.append(critname or f"Criterion {i+1}")
    weights.append(critweight)

if st.button("Compute"):
    try:
        weights = np.array(weights)
        total = weights.sum()

        if total == 0:
            st.error("Total weight is 0. Cannot normalize.")
        else:
            normalized = weights/total
            
            result = pd.DataFrame({
                "Criteria": criteria, 
                "Normalized Weight": normalized
            })

            st.dataframe(result.style.format({"Normalized Weight": "{:.3f}"}))

    except Exception as e:
        st.error(f"error: {e}")