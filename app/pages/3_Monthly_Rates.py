import streamlit as st
import pandas as pd

st.title("📊 Exchange Rate Merger App")

# --- Function to load data with optional sheet selection ---
def load_data(file, file_label):
    if file is None:
        return None

    if file.name.endswith('.csv'):
        data = pd.read_csv(file)
    elif file.name.endswith(('.xls', '.xlsx')):
        xls = pd.ExcelFile(file)
        sheet_name = st.selectbox(f"Select a sheet from {file_label}", xls.sheet_names, key=file_label)
        data = pd.read_excel(file, sheet_name=sheet_name)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None

    # Convert all column names to lowercase
    data.columns = data.columns.str.lower()

    return data

# --- Function to process and merge datasets ---
def process_data(exchange_rate_data, export_data):
    # Ensure 'date' columns are datetime and strip time
    exchange_rate_data['date'] = pd.to_datetime(exchange_rate_data['date'], errors='coerce').dt.date
    export_data['date'] = pd.to_datetime(export_data['date'], errors='coerce').dt.date

    # Extract Month-Year string
    exchange_rate_data['month_year'] = pd.to_datetime(exchange_rate_data['date']).dt.strftime('%b %Y')
    export_data['month_year'] = pd.to_datetime(export_data['date']).dt.strftime('%b %Y')

    # Keep only needed columns for merge
    exchange_rate_data_clean = exchange_rate_data[['month_year', 'currency code', 'rate']]

    # Merge based on Month-Year and currency code, bringing only 'rate'
    merged_data = pd.merge(export_data, exchange_rate_data_clean,
                           left_on=['month_year', 'currency code'],
                           right_on=['month_year', 'currency code'],
                           how='left')

    return merged_data

# --- Upload Exchange Rate Data ---
st.subheader("📥 Upload Exchange Rate Data")
exchange_rate_file = st.file_uploader("Upload Exchange Rate Data (CSV or Excel)", type=['csv', 'xls', 'xlsx'], key='exchange')
exchange_rate_data = load_data(exchange_rate_file, 'Exchange Rate')

if exchange_rate_data is not None:
    st.write("📄 **Exchange Rate Data Preview (first 10 rows)**")
    st.dataframe(exchange_rate_data.head(10))

# --- Upload Export Data ---
st.subheader("📥 Upload Export Data")
export_file = st.file_uploader("Upload Export Data (CSV or Excel)", type=['csv', 'xls', 'xlsx'], key='export')
export_data = load_data(export_file, 'Export')

if export_data is not None:
    st.write("📄 **Export Data Preview (first 10 rows)**")
    st.dataframe(export_data.head(10))

# --- Process and display merged data ---
if exchange_rate_data is not None and export_data is not None:
    merged_data = process_data(exchange_rate_data, export_data)

    st.success("✅ Data merged successfully!")

    st.write("🔗 **Merged Data Preview (first 10 rows)**")
    st.dataframe(merged_data.head(10))

    # Download merged data
    csv = merged_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Merged Data as CSV",
        data=csv,
        file_name='merged_data.csv',
        mime='text/csv',
    )
else:
    st.info("Please upload both Exchange Rate and Export data to proceed.")
