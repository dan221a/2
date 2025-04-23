# app.py
# Streamlit application to fetch and update Recall entities from Base44 API

import os
import requests
import streamlit as st
import pandas as pd

# Configuration
API_BASE_URL = "https://app.base44.com/api/apps/6809148e298bbd9cf45ed5fa/entities/Recall"
# Load your API key securely: set in Streamlit Secrets or environment variable
API_KEY = st.secrets.get("BASE44_API_KEY") or os.getenv("BASE44_API_KEY")

HEADERS = {
    'api_key': API_KEY,
    'Content-Type': 'application/json'
}

@st.cache_data
def fetch_recall_entities():
    """
    Fetch Recall entities from Base44
    """
    response = requests.get(API_BASE_URL, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return pd.DataFrame(data)

@st.cache_data
def fetch_single_entity(entity_id: str):
    """
    Fetch a single Recall entity by ID
    """
    url = f"{API_BASE_URL}/{entity_id}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def update_recall_entity(entity_id: str, update_data: dict):
    """
    Update a Recall entity in Base44
    """
    url = f"{API_BASE_URL}/{entity_id}"
    response = requests.put(url, json=update_data, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Streamlit UI
st.set_page_config(page_title="Contamio Recall Manager", layout="wide")
st.title("🛑 Contamio Recall Entities Dashboard")

# Fetch data
with st.spinner("Loading recall data..."):
    df = fetch_recall_entities()

# Sidebar filters
st.sidebar.header("🔍 Filters")
filter_region = st.sidebar.multiselect("Region", options=df["region"].unique(), default=None)
filter_severity = st.sidebar.multiselect("Severity", options=df["severity"].unique(), default=None)

# Apply filters
if filter_region:
    df = df[df["region"].isin(filter_region)]
if filter_severity:
    df = df[df["severity"].isin(filter_severity)]

# Display table
st.subheader("📋 Recall Entities")
st.dataframe(df)

# Entity update section
st.sidebar.header("✏️ Update Recall")
selected_id = st.sidebar.selectbox("Select Entity ID to Edit", options=df["id"].astype(str))
if selected_id:
    entity = fetch_single_entity(selected_id)
    st.sidebar.markdown("---")
    st.sidebar.write(f"**Title:** {entity.get('title')} ")

    # Editable fields
    new_status = st.sidebar.selectbox("Status", options=["open", "in_progress", "closed", "resolved"], index=["open","in_progress","closed","resolved"].index(entity.get('status', 'open')))
    new_corrective = st.sidebar.text_area("Corrective Action", value=entity.get('corrective_action', ''))
    if st.sidebar.button("Update Entity"):
        update_data = {
            "status": new_status,
            "corrective_action": new_corrective
        }
        result = update_recall_entity(selected_id, update_data)
        st.sidebar.success("Entity updated successfully!")
        st.experimental_rerun()

# Footer
st.markdown("---")
st.caption("Built with Streamlit & Base44 API | Contamio")
