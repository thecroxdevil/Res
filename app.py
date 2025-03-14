import streamlit as st

# Test if the secret is available
custom_value = st.secrets.get("CUSTOM_SECRET_KEY", None)

if custom_value:
    st.write(f"Custom Secret Value: {custom_value}")
else:
    st.error("Custom Secret Value not found!")
