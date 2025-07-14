import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Anggaran Cerdas MVP", layout="wide")

st.title("Anggaran Cerdas: Budget Anomaly Detector")
st.markdown("Upload a RAPBD file and compare prices with reference values to detect anomalies.")

# Simulated reference price database
reference_prices = {
    "Lem Aibon": 5000,
    "Pensil": 1800,
    "Kertas A4": 1400,
    "Kursi Kantor": 600000,
    "Laptop": 10000000
}

# Upload file (simulation only accepts CSV/Excel for now)
uploaded_file = st.file_uploader("Upload RAPBD File (.xlsx, .csv)", type=["csv", "xlsx"])

def process_data(df):
    df["Ref Price (Rp)"] = df["Item Name"].map(reference_prices)
    df["% Difference"] = ((df["Unit Price (Rp)"] - df["Ref Price (Rp)"]) / df["Ref Price (Rp)"]) * 100
    df["Flag"] = np.where(df["% Difference"] > 50, "Flagged", "OK")
    return df

if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Parsed Budget Data")
    processed_df = process_data(df)
    st.dataframe(processed_df, use_container_width=True)

    flagged = processed_df[processed_df["Flag"] == "Flagged"]
    st.markdown(f"### Flagged Anomalies ({len(flagged)} items)")
    st.dataframe(flagged, use_container_width=True)

    # Download
    st.download_button("Download Result as CSV", processed_df.to_csv(index=False), file_name="anggaran_cerdas_output.csv", mime="text/csv")

else:
    st.info("Upload a file to get started. You can also use the following sample format:")
    sample_data = pd.DataFrame({
        "Item Name": ["Lem Aibon", "Pensil", "Kertas A4", "Kursi Kantor", "Laptop"],
        "Quantity": [1, 100, 50, 10, 5],
        "Unit Price (Rp)": [82000, 2000, 1500, 750000, 12000000]
    })
    st.dataframe(sample_data)


