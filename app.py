import pandas as pd
import streamlit as st
from io import BytesIO

# Set up the app title and introductory text
st.title("Prepare Your CSV for LinkedIn Ads Custom Audience")

st.markdown("""
### Hey there! 👋
Welcome to your CSV processing tool! This app helps you prep either a Contact List or a Company List in the perfect format for LinkedIn Ads.
""")

# Define mappings for Contact List
contact_friendly_name_map = {
    "email": "Email",
    "firstname": "First Name",
    "lastname": "Last Name",
    "jobtitle": "Job Title",
    "employeecompany": "Company",
    "country": "Country",
    "googleaid": "Google Ad ID"
}

contact_keyword_map = {
    "firstname": ["first"],
    "lastname": ["last"],
    "employeecompany": ["company"],
    "jobtitle": ["title", "position"],
    "email": ["email"],
    "country": ["country"],
    "googleaid": ["google", "ad id", "gaid"]
}

# Define mappings for Company List
company_friendly_name_map = {
    "companyname": "Company Name",
    "companywebsite": "Company Website",
    "companyemaildomain": "Email Domain",
    "linkedincompanypageurl": "LinkedIn Page URL",
    "stocksymbol": "Stock Symbol",
    "industry": "Industry",
    "city": "City",
    "state": "State",
    "companycountry": "Country",
    "zipcode": "Zip Code"
}

company_keyword_map = {
    "companyname": ["company"],
    "companywebsite": ["website", "web"],
    "companyemaildomain": ["domain"],
    "linkedincompanypageurl": ["linkedin", "page"],
    "stocksymbol": ["stock", "symbol"],
    "industry": ["industry"],
    "city": ["city"],
    "state": ["state"],
    "companycountry": ["country"],
    "zipcode": ["zip", "postal"]
}

# Main screen with options
st.write("Please choose the type of list you'd like to process:")
list_type = st.radio("Choose List Type:", ["Contact List", "Company List"])

# Set mappings based on chosen list type
if list_type == "Contact List":
    final_columns = list(contact_friendly_name_map.keys())
    friendly_name_map = contact_friendly_name_map
    keyword_map = contact_keyword_map
elif list_type == "Company List":
    final_columns = list(company_friendly_name_map.keys())
    friendly_name_map = company_friendly_name_map
    keyword_map = company_keyword_map

# Upload CSV file
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)
    st.write("Uploaded CSV Preview:", df.head())

    # Attempt automatic column matching based on keywords
    column_map = {}
    auto_mapped = {}

    for col in final_columns:
        # Try to find a matching column based on keywords
        matched_column = next(
            (
                df_col for df_col in df.columns
                if any(keyword.lower() in df_col.lower() for keyword in keyword_map[col])
            ),
            None
        )
        column_map[col] = matched_column
        if matched_column:
            auto_mapped[col] = matched_column

    # Show automatic matches to user for confirmation or adjustment
    st.write("**Map Columns**")
    st.write("The app has automatically mapped columns where possible. Please confirm or adjust as needed:")

    # Display mapping options, with automatic matches as default selections
    for col in final_columns:
        default_selection = column_map[col]
        column_map[col] = st.selectbox(
            f"Map '{friendly_name_map[col]}' to:",
            [None] + list(df.columns),
            index=(list(df.columns).index(default_selection) + 1) if default_selection else 0
        )

    # Process the CSV based on mappings
    if st.button("Process CSV"):
        # Create a new DataFrame based on the final mapping
        new_df = pd.DataFrame()
        for col in final_columns:
            selected_column = column_map[col]
            if selected_column:
                new_df[col] = df[selected_column]
            else:
                new_df[col] = ""  # Fill missing columns with empty strings

        # Prepare the processed file for download with internal column names
        output = BytesIO()
        new_df.columns = final_columns  # Keep internal column names
        new_df.to_csv(output, index=False)
        output.seek(0)

        # Set the file name based on list type
        file_name = "anny-lenny-contact.csv" if list_type == "Contact List" else "anny-lenny-company.csv"

        st.download_button(
            label="Download Processed CSV",
            data=output,
            file_name=file_name,
            mime="text/csv"
        )

# Instructions at the bottom
st.markdown("""
---

### Instructions:

1. Choose the type of list you want to process: **Contact List** or **Company List**.
2. Upload your CSV file.
3. The app will automatically map columns where possible. You can review and adjust the mappings as needed.
4. Download your formatted CSV file, ready for LinkedIn Ads!

*Note: If you have any questions or need assistance, feel free to reach out to me at [anyjulia@anylenny.com](mailto:anyjulia@anylenny.com).*
""")
