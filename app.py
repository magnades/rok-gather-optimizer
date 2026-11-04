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
    google_sheet_url = "TU_URL_DE_GOOGLE_SHEETS_AQUI"
    active_sheet = gspread_client.open_by_url(google_sheet_url).sheet1
except Exception as connection_error:
    st.error("Error connecting to Google Sheets. Check your credentials.")
    st.stop()

# Build the Streamlit UI
st.title("Guardar Recurso")

# Dictionary mapping the UI display (with emojis) to the clean database string
resources_options = {
    "🌽 Corn": "Corn",
    "🪵 Wood": "Wood",
    "🪨 Rock": "Rock",
    "🪙 Gold": "Gold",
    "💎 Cristal": "Cristal"
}

# Create a form to group inputs
with st.form("resource_form"):
    x_coord = st.number_input("Coordenada X (Columna B):", format="%f", step=0.01)
    y_coord = st.number_input("Coordenada Y (Columna C):", format="%f", step=0.01)
    
    # Dropdown using the keys of the dictionary (the ones with emojis)
    selected_resource_ui = st.selectbox("Recurso (Columna D):", options=list(resources_options.keys()))
    
    optional_text = st.text_input("Texto opcional (Columna E):", placeholder="Añade una nota...")
    
    submit_button = st.form_submit_button("Guardar Datos")
    
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
            st.error("Error: Estas coordenadas ya están registradas en la hoja.")
        else:
            # Extract the clean string value (without emoji) to save in the sheet
            clean_resource_value = resources_options[selected_resource_ui]
            
            # Append new data. Empty string for Col A, x_coord for Col B, y_coord for Col C...
            new_row_data = ["", x_coord, y_coord, clean_resource_value, optional_text]
            active_sheet.append_row(new_row_data)
            
            st.success("Éxito: Datos guardados correctamente.")