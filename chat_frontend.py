import streamlit as st
import os
import json
from PIL import Image
import pandas as pd  # Import pandas for table creation
st.set_page_config(layout="wide")
data_folder = "Responses"
image_folder = "images"

# Get list of JSON files
json_files = [f for f in os.listdir(data_folder) if f.endswith(".json")]

# Sort files for consistent order
json_files.sort()

# Session state to track current file index
if 'file_index' not in st.session_state:
    st.session_state.file_index = 0

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8' ,errors='ignore') as f:
        return json.load(f)

def show_image(image_name):
    image_path = os.path.join(image_folder, image_name + ".jpg")
    if os.path.exists(image_path):
        image = Image.open(image_path)
        return image
    else:
        st.warning(f"Image {image_name}.jpg not found.")
        return None

def main():
    st.title("Medical Report Viewer")
    next_button = st.button("Next Image")
    if json_files:
        # Get current file
        current_json_file = json_files[st.session_state.file_index]
        json_path = os.path.join(data_folder, current_json_file)
        
        # Extract image name
        image_name = os.path.splitext(current_json_file)[0]  # Remove .json extension
        
        # Load JSON data
        json_data = load_json(json_path)
        
        # Display report title
        st.subheader("Report Title")
        st.text_input("Title", json_data["report_title"], key="report_title", disabled=True)
        
        # Prepare data for the table
        test_data = []
        for test in json_data["test_results"]:
            test_data.append({
                "Test Name": test["test_name"],
                "Value": test["value"],
                "Unit": test["unit"],
                "Reference": test["range"]
            })
        
        # Create a DataFrame for the test results
        test_df = pd.DataFrame(test_data)
        
        # Create two columns: larger image column and table column
        col1, col2 = st.columns([3, 6])  # Adjust the relative width of the columns (3 for image, 2 for table)

        with col1:
            # Show the corresponding image
            st.subheader("Associated Image")
            image = show_image(image_name)
            if image:
                st.image(image, caption=image_name, use_container_width=True)  # Image takes full width of the column

        with col2:
            # Display the test results in a table
            st.subheader("Test Results Table")
            st.table(test_df)  # Display the table
        
        # Navigation button
        if next_button:
            st.session_state.file_index = (st.session_state.file_index + 1) % len(json_files)
            st.rerun()
    else:
        st.error("No JSON files found in the Responses folder.")

if __name__ == "__main__":
    main()
