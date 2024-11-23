import streamlit as st
import requests

# Define FastAPI server URL
FASTAPI_URL = "http://127.0.0.1:8000"  # Update with your deployed server's URL if not running locally

st.title("Image Caption Generator")

uploaded_file = st.file_uploader("Upload an image (JPEG or PNG)", type=["jpeg", "jpg", "png"])
optional_text = st.text_input("Optional text to guide caption generation")

if st.button("Generate Caption"):
    if uploaded_file is not None:
        try:
            # Send the file to the FastAPI server
            files = {"image": uploaded_file.getvalue()}
            data = {"text": optional_text}
            response = requests.post(f"{FASTAPI_URL}/caption", files=files, data=data)

            if response.status_code == 200:
                caption = response.json().get("caption", "No caption returned.")
                st.success(f"Caption: {caption}")
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.warning("Please upload an image first.")
