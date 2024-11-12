import streamlit as st
from powerpoint import describe_pptx
import streamlit as st
import tempfile
from pathlib import Path

# Step 1: Upload the PPTX file
st.write(f"hello")
uploaded_file = st.file_uploader("Upload a PPTX file", type="pptx")

if uploaded_file is not None:
    st.write(Path(uploaded_file.name).suffix)
    # Step 2: Save the uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pptx") as temp_file:
        temp_file.write(uploaded_file.read())
        temp_file_path = temp_file.name  # Get the path of the temporary file
    description = describe_pptx(temp_file_path)
    st.write(description)