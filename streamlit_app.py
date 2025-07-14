import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Anggaran Cerdas", layout="wide")

st.title("Anggaran Cerdas: Budget Anomaly Detector")
st.markdown("Upload file RAPBD Anda, dan sistem akan otomatis memverifikasi dengan harga acuan internal untuk mendeteksi anomali pengadaan.")

# Load reference prices from local file
@st.cache_data
def load_reference_prices():
    path = "reference_prices_2000.csv"
    if not os.path.exists(path):
        st.error("File harga acuan internal tidak ditemukan.")
        return {}
    ref_df = pd.read_csv(path)
    return dict(zip(ref_df["Item Name"], ref_df["Reference Price (Rp)"]))

reference_prices = load_reference_prices()

# Show expected format
st.markdown("#### Format File RAPBD yang Diharapkan")
st.write("File harus memiliki kolom berikut:")
st.code("Item Name, Quantity, Unit Price (Rp)", language="csv")
sample_df = pd.DataFrame({
    "Item Name": ["Lem Aibon", "Pensil"],
    "Quantity": [1, 100],
    "Unit Price (Rp)": [82000, 2000]
})
st.dataframe(sample_df)

# Upload budget file
uploaded_file = st.file_uploader("Upload RAPBD File Anda (.xlsx atau .csv)", type=["csv", "xlsx"])

# Process function
def process_data(df, reference_prices):
    df["Ref Price (Rp)"] = df["Item Name"].map(reference_prices)
    df["Verification Status"] = df["Ref Price (Rp)"].apply(
        lambda x: "Belum diverifikasi - harga acuan tidak tersedia" if pd.isna(x) else "Terverifikasi"
    )
    df["% Difference"] = np.where(
        df["Verification Status"] == "Terverifikasi",
        ((df["Unit Price (Rp)"] - df["Ref Price (Rp)"]) / df["Ref Price (Rp)"]) * 100,
        None
    )
    df["Flag"] = np.where(
        df["Verification Status"] == "Terverifikasi",
        np.where(df["% Difference"] > 50, "Flagged", "OK"),
        "N/A"
    )
    return df

# Main logic
if uploaded_file:
    if uploaded_file.name.endswith("csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    processed_df = process_data(df, reference_prices)

    # Count items without reference price
    unverified_count = processed_df[processed_df["Verification Status"].str.contains("Belum diverifikasi")].shape[0]
    total_count = processed_df.shape[0]

    st.markdown(f"**{unverified_count} dari {total_count} item** tidak memiliki harga acuan dan tidak dianalisis untuk anomali.")


    st.subheader("Hasil Analisis Anggaran")
    st.info("Catatan: Item tanpa harga acuan akan ditandai sebagai *'Belum diverifikasi'* dan tidak diperiksa untuk anomali.")
    st.dataframe(processed_df, use_container_width=True)

    flagged = processed_df[processed_df["Flag"] == "Flagged"]
    st.markdown(f"### Anomali Terdeteksi ({len(flagged)} item)")
    st.dataframe(flagged, use_container_width=True)

    st.download_button("Download Hasil sebagai CSV", processed_df.to_csv(index=False), file_name="hasil_anggaran_cerdas.csv", mime="text/csv")
else:
    st.info("Silakan unggah file RAPBD untuk memulai analisis.")

