import streamlit as st
import requests
from api import upload_document_api, query_rag_api, query_graphrag_api

def upload_section():
    st.info("Upload a PDF or Image file")
    uploaded_file = st.file_uploader("Select a file", type=["pdf", "jpeg", "jpg", "png"])

    if uploaded_file is not None:
        if uploaded_file.type.startswith("image"):
            st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        else:
            st.write("PDF file uploaded.")

        if st.button("Upload Document"):
            with st.spinner("Uploading..."):
                response = upload_document_api(uploaded_file)
                if response.get("status") == "success":
                    st.success("Upload successful!")
                    st.info(f"Document ID: {response.get('document_id')}")
                else:
                    st.error("Upload failed. Please try again.")

def query_section(query_mode: str):
    query_text = st.text_input("Enter your query", "")

    if st.button("Submit Query"):
        if not query_text:
            st.warning("Please enter a query.")
            return
        with st.spinner("Querying..."):
            if query_mode == "RAG":
                result = query_rag_api(query_text)
            else:
                result = query_graphrag_api(query_text)
            if result:
                st.subheader("Response")
                st.write(result.get("answer", "No answer returned."))
                st.subheader("Sources")
                st.write(result.get("sources", []))
            else:
                st.error("Failed to retrieve a response.") 