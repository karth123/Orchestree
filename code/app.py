import json
from pathlib import Path
import sys
import re
import uuid
from datetime import datetime, timedelta
import os
import streamlit as st
import time
import shutil
from streamlit.components.v1 import html
from backend import YAMLTransformer, SVGTransformer, generate_svg_from_yaml, remove_all_dot_files

# Set directory path
dir = Path(__file__).resolve().parent
sys.path.append(dir.parent.parent)

# App state initialization
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = True
if "email" not in st.session_state:
    st.session_state["email"] = None
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "output" not in st.session_state:
    st.session_state["output"] = None
if "last_interaction" not in st.session_state:
    st.session_state["last_interaction"] = time.time()
if "input_data" not in st.session_state:
    st.session_state["input_data"] = None

# Update last interaction time
def update_interaction():
    st.session_state["last_interaction"] = time.time()

# Inject JavaScript to handle page unload
st.markdown("""
<script>
window.addEventListener('beforeunload', function (event) {
    fetch('/clean-up', { method: 'POST' });
});
</script>
""", unsafe_allow_html=True)

# Title
st.title("Orchestree")

# Supported cloud providers
cloud_providers = ["AWS", "Azure", "Google Cloud", "IBM Cloud", "Oracle Cloud"]

# Load icon keys
with open(r"icon_descriptor.json", "r") as f:
    icon_keys = json.load(f)

# Load default prompt JSON
with open("default_prompt.json", "r") as f:
    default_prompt = json.load(f)

# Button to load default values from prompt JSON
if st.button("Default Prompt", on_click=update_interaction):
    st.session_state["file_name"] = "events_processing_architecture_AWS"
    st.session_state["title"] = default_prompt["title"]
    st.session_state["selected_providers"] = default_prompt["cloudProviders"]
    st.session_state["resources"] = default_prompt["icons"]
    st.session_state["clustering"] = default_prompt["clusteringDetails"]
    st.session_state["relationships"] = default_prompt["relationships"]
    st.experimental_rerun()

# User inputs
with st.form("architecture_form"):
    file_name = st.text_input("Provide a file name for the project. Warning: File name will be used as provided", st.session_state.get("file_name", ""))
    title = st.text_input("Provide a title of your cloud system architecture and a brief description", st.session_state.get("title", ""))
    selected_providers = st.multiselect("Select cloud providers", cloud_providers, st.session_state.get("selected_providers", []))
    resources = st.multiselect("Select resources used in this cloud system architecture", icon_keys, default=st.session_state.get("resources", []))
    clustering = st.text_area("How are these cloud provider resources clustered or grouped? Describe in detail.", st.session_state.get("clustering", ""), height=150)
    relationships = st.text_area("Describe the relationships between these resources and clusters/groups", st.session_state.get("relationships", ""), height=150)
    submitted = st.form_submit_button("Submit", on_click=update_interaction)

# Handle form submission
user_id = st.session_state["session_id"]
if submitted:
    input_data = {
        "title": title,
        "cloud_providers": selected_providers,
        "relationships_description": relationships,
        "resources": resources,
        "cluster_description": clustering
    }
    st.session_state["input_data"] = str(input_data)

    # Start backend process logic
    with open(r"base_prompt.txt", 'r') as base_prompt_file:
        first_pass = base_prompt_file.read()
    with open(r"yaml_transformer.txt", 'r') as base_prompt_file:
        second_pass = base_prompt_file.read()
    icon_descriptor_path = r"icon_descriptor.json"
    exception_icon_path = r"blank-cloud-svgrepo-com.svg"

    first_yaml = YAMLTransformer().generate_yaml_from_prompt(input_data=str(input_data), system_prompt=first_pass)
    second_yaml = YAMLTransformer().transform_yaml_with_icons(input_yaml=first_yaml, cloud_icons=str(resources), system_prompt=second_pass)
    third_yaml = YAMLTransformer().transform_yaml_with_icon_paths(yaml_string=second_yaml, icon_descriptor_path=icon_descriptor_path, exception_icon_path=exception_icon_path)
    local_svg = generate_svg_from_yaml(yaml_content=third_yaml)
    new_svg = SVGTransformer().get_svg_code(main_svg_code=local_svg)
    remove_all_dot_files()

    # End backend process logic
    st.session_state["output"] = new_svg
    st.session_state["submitted"] = True

if st.session_state["submitted"]:

# Replace width and height attributes inside the <svg> tag
    scaled_svg = st.session_state["output"]

    st.write(
        f'''
        <div style="display: flex; justify-content: center; margin-bottom: -800px;">
            <div style="transform: scale(0.3); transform-origin: top center;">
                {scaled_svg}
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )
    st.download_button(
            label="Download SVG",
            data=st.session_state["output"],
            file_name=f"{file_name or 'cloud_architecture'}.svg",
            mime="image/svg+xml"
        )
    update_interaction()

    if st.button("Regenerate", on_click=update_interaction):
        first_yaml = YAMLTransformer().generate_yaml_from_prompt(input_data=str(input_data), system_prompt=first_pass)
        second_yaml = YAMLTransformer().transform_yaml_with_icons(input_yaml=first_yaml, cloud_icons=str(resources), system_prompt=second_pass)
        third_yaml = YAMLTransformer().transform_yaml_with_icon_paths(yaml_string=second_yaml, icon_descriptor_path=icon_descriptor_path, exception_icon_path=exception_icon_path)
        local_svg = generate_svg_from_yaml(yaml_content=third_yaml)
        new_svg = SVGTransformer().get_svg_code(main_svg_code=local_svg)
        st.session_state["output"] = new_svg

            # Resize the raw SVG before embedding it
        raw_svg = st.session_state["output"]

# Replace width and height attributes inside the <svg> tag
        scaled_svg = st.session_state["output"]

        st.write(
            f'''
            <div style="display: flex; justify-content: center; margin-bottom: -800px;">
                <div style="transform: scale(0.3); transform-origin: top center;">
                    {scaled_svg}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )    
        st.download_button(
            label="Download SVG",
            data=st.session_state["output"],
            file_name=f"{file_name or 'cloud_architecture'}.svg",
            mime="image/svg+xml"
        )
        st.experimental_rerun()

    if st.button("Restart", on_click=update_interaction):
        st.session_state["submitted"] = False
        st.session_state["output"] = None
        st.session_state["input_data"] = None
        st.experimental_rerun()
