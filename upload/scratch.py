import streamlit as st
from description import describe_pptx, describe_pdf, allowed_paths
import streamlit as st
from pathlib import Path

# Step 1: Upload the PPTX file
st.write(f"hello")
uploaded_file = st.file_uploader("Upload  file")

if uploaded_file is not None and Path(uploaded_file.name).suffix in allowed_paths:
    if Path(uploaded_file.name).suffix == ".pptx":
        description = describe_pptx(uploaded_file, False, 3000, True)
    elif Path(uploaded_file.name).suffix == ".pdf":
        description = describe_pdf(uploaded_file, False, 3000, True)
    st.write(description)