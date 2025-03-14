import streamlit as st

# Try accessing a custom secret
custom_value = st.secrets.get("HF_TOKEN", None)

if custom_value:
    st.write(f"Custom Secret Value: {custom_value}")
else:
    st.error("Custom Secret Value not found!")
