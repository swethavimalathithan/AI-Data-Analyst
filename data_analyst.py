import streamlit as st
import pandas as pd
from pandasai import Agent
from ydata_profiling import ProfileReport
import base64
import os

st.set_page_config(page_title="AI Data Analysis Assistant")
st.title("AI Data Analyst")

def sidebar_api_key_form():
    st.sidebar.header("API Key Setup")

    if 'api_key' not in st.session_state:
        st.session_state.api_key = None

    with st.sidebar.form(key='api_key_form'):
        st.session_state.api_key = st.text_input("Enter your BambooLLM API Key", type="password")
        submit_button = st.form_submit_button("Submit API Key")
        
        if submit_button:
            if st.session_state.api_key:
                os.environ["PANDASAI_API_KEY"] = st.session_state.api_key
                st.session_state.api_key = st.session_state.api_key  # Store the API key in session state
                st.sidebar.success("API Key set successfully!")
            else:
                st.sidebar.error("Please enter an API Key.")

sidebar_api_key_form()

if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None

if 'agent' not in st.session_state:
    st.session_state.agent = None

def handle_file_upload(uploaded_file):
    st.session_state.uploaded_file = uploaded_file
    st.session_state.df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    st.session_state.agent = Agent(st.session_state.df)
    st.session_state.file_uploaded = True
    st.success("File uploaded successfully! You can now generate a report or chat with the data.")

def generate_profiling_report():
    try:
        df = st.session_state.df
        profile = ProfileReport(df, title="EDA Report", explorative=True)
        report_file = "profiling_report.html"
        profile.to_file(report_file)

        st.markdown(get_download_link(report_file), unsafe_allow_html=True)

        with open(report_file, "r") as f:
            report_html = f.read()

        st.components.v1.html(report_html, height=800, scrolling=True)
        os.remove(report_file)

    except Exception as e:
        st.error(f"Error generating report: {e}")

def get_download_link(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode('UTF-8')
    href = f'''
    <a href="data:file/html;base64,{b64}" download="{file_path}" 
       style="display: inline-flex; align-items: center; text-decoration: none; padding: 8px 16px; background-color: #4CAF50; color: white; border-radius: 4px;">
       <img src="https://img.icons8.com/material-outlined/24/000000/download.png" alt="download icon" style="margin-right: 8px;"/>
       Download Report
    </a>
    '''
    return href

uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["xlsx", "csv"], key="file_uploader")

if st.button("Upload File", help="Click to upload the file"):
    if uploaded_file is not None:
        handle_file_upload(uploaded_file)
    else:
        st.write("Please upload a file.")

if st.session_state.get('file_uploaded', False):
    st.write("File successfully uploaded! You can now generate a report or chat with the data.")
    
    if st.button("Generate Report", help="Click to generate a report for the uploaded dataset.", use_container_width=True):
        with st.spinner("Generating report..."):
            generate_profiling_report()

    st.subheader("Ask your question:")
    user_input = st.text_input("Type your question here:")

    if st.button("Submit Question"):
        if user_input:
            with st.spinner("Generating response..."):
                response = st.session_state.agent.chat(user_input)
                st.write(f"**Question:** {user_input}")
                st.write(f"**Answer:** {response}")
        else:
            st.write("Please enter a question.")
