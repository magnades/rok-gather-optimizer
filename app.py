import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# Define the scopes required for Google Sheets and Drive access
api_scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Load credentials. In production, this should come from st.secrets
# For local testing, you can use Credentials.from_service_account_file("path/to/your/credentials.json", scopes=api_scopes)
try:
    gcp_credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], 
        scopes=api_scopes
    )
    gspread_client = gspread.authorize(gcp_credentials)
    
    # Open the Google Sheet by its exact URL
    google_sheet_url = "https://docs.google.com/spreadsheets/d/1Po9b2HoB9DYWeFoUEd1gR83NI0nanNuhwqM5a47Fmgg/edit?gid=0#gid=0"
    active_sheet = gspread_client.open_by_url(google_sheet_url).sheet1
except Exception as connection_error:
    st.error(f"Error connecting to Google Sheets. Technical details: {connection_error}")
    st.stop()

# Build the Streamlit UI
st.title("Save Resource")

# Dictionary mapping the UI display (with emojis) to the clean database string
resources_options = {
    "🌽 Corn": "Corn",
    "🪵 Wood": "Wood",
    "🪨 Rock": "Rock",
    "🪙 Gold": "Gold",
    "💎 Cristal": "Cristal",
    "⛩️ Pass": "Pass",               # Pasos
    "🗿 Altar": "Altar"
}

# Create a form to group inputs
with st.form("resource_form"):
    x_coord = st.number_input("X Coordinate (Column B):", format="%f", step=0.01)
    y_coord = st.number_input("Y Coordinate (Column C):", format="%f", step=0.01)
    
    # Dropdown using the keys of the dictionary (the ones with emojis)
    selected_resource_ui = st.selectbox("Resource (Column D):", options=list(resources_options.keys()))
    
    optional_text = st.text_input("Optional text (Column E):", placeholder="Add a note...")
    
    submit_button = st.form_submit_button("Save Data")
    
    # Handle the save logic when the button is clicked
    if submit_button:
        # Fetch all existing records from the sheet to check for duplicates
        existing_data = active_sheet.get_all_values()
        
        is_duplicate = False
        
        # Loop through existing rows, starting at index 1 to skip headers
        for row_index in range(1, len(existing_data)):
            current_row = existing_data[row_index]
            
            # Ensure the row has enough columns before accessing index 1 and 2
            if len(current_row) > 2:
                try:
                    # Convert string values from Google Sheets to float for comparison
                    sheet_x_val = float(current_row[1])
                    sheet_y_val = float(current_row[2])
                    
                    if sheet_x_val == x_coord and sheet_y_val == y_coord:
                        is_duplicate = True
                        break
                except ValueError:
                    # Skip rows that contain non-numeric data in coordinates columns
                    pass 
        
        if is_duplicate:
            st.error("Error: These coordinates are already registered in the sheet.")
        else:
            # Extract the clean string value (without emoji) to save in the sheet
            clean_resource_value = resources_options[selected_resource_ui]
            
            # Append new data. Empty string for Col A, x_coord for Col B, y_coord for Col C...
            new_row_data = ["", x_coord, y_coord, clean_resource_value, optional_text]
            active_sheet.append_row(new_row_data)
            
            st.success("Success: Data saved successfully.")