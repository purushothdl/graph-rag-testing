import streamlit as st
from components import upload_section, query_section

def main():
    st.set_page_config(page_title="RAG & GraphRAG UI", layout="wide")
    st.title("RAG & GraphRAG Document Processing")
    st.write("Welcome! Use the tools below to upload documents and query them using either RAG or GraphRAG methods.")

    # Upload Section Container
    st.header("Upload Documents")
    upload_section()

    st.markdown("---")
    
    # Query Section Container
    st.header("Query Documents")
    query_mode = st.radio("Select Query Mode", options=["RAG", "GraphRAG"], index=0)
    query_section(query_mode)

if __name__ == "__main__":
    main() 