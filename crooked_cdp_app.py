import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Crooked-Line 2D CDP Processing App")

# -----------------------------
# Sidebar parameters
# -----------------------------
st.sidebar.header("Geometry Parameters")

receiver_spacing = st.sidebar.number_input(
    "Receiver spacing (m)", value=20.0, step=1.0
)

cdp_spacing = receiver_spacing / 2
st.sidebar.write(f"CDP spacing = {cdp_spacing} m")

# -----------------------------
# File upload
# -----------------------------
uploaded_file = st.file_uploader(
    "Upload geometry text file",
    type=["txt", "dat", "csv"]
)

if uploaded_file is not None:

    # -----------------------------
    # Read text file
    # -----------------------------
    try:
        df = pd.read_csv(uploaded_file, delim_whitespace=True, sep=',')
    except:
        df = pd.read_csv(uploaded_file)

    st.subheader("Input Geometry Preview")
    st.dataframe(df.head())

    required_cols = {"Sx", "Sy", "Rx", "Ry"}
    if not required_cols.issubset(df.columns):
        st.error("File must contain columns: Sx, Sy, Rx, Ry")
        st.stop()

    # -----------------------------
    # CDP midpoint
    # -----------------------------
    df["CDP_X"] = (df["Sx"] + df["Rx"]) / 2
    df["CDP_Y"] = (df["Sy"] + df["Ry"]) / 2

    # -----------------------------
    # Sort midpoints spatially
    # -----------------------------
    df = df.sort_values(by=["CDP_X", "CDP_Y"]).reset_index(drop=True)

    # -----------------------------
    # Distance along crooked line
    # -----------------------------
    dx = df["CDP_X"].diff().fillna(0)
    dy = df["CDP_Y"].diff().fillna(0)

    df["DIST_ALONG_LINE"] = np.sqrt(dx**2 + dy**2).cumsum()

    # -----------------------------
    # CDP binning
    # -----------------------------
    df["CDP_BIN"] = np.round(
        df["DIST_ALONG_LINE"] / cdp_spacing
    ).astype(int)

    # -----------------------------
    # Assign CDP numbers
    # -----------------------------
    df["CDP_NO"] = df.groupby("CDP_BIN").ngroup() + 1

    # -----------------------------
    # Fold calculation
    # -----------------------------
    fold = df.groupby("CDP_NO").size().reset_index(name="FOLD")
    df = df.merge(fold, on="CDP_NO", how="left")

    # -----------------------------
    # Display results
    # -----------------------------
    st.subheader("Processed CDP Table")
    st.dataframe(
        df[
            ["CDP_NO", "CDP_X", "CDP_Y",
             "DIST_ALONG_LINE", "FOLD"]
        ]
    )

    # -----------------------------
    # CDP X-Y Curve Plot
    # -----------------------------
    st.subheader("CDP X–Y Crooked-Line Geometry")

    cdp_curve = (
        df.groupby("CDP_NO")[["CDP_X", "CDP_Y"]]
          .mean()
          .reset_index()
    )

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(cdp_curve["CDP_X"], cdp_curve["CDP_Y"], "-o")
    ax.set_xlabel("CDP X (m)")
    ax.set_ylabel("CDP Y (m)")
    ax.set_title("Crooked-Line 2D CDP Geometry")
    ax.grid(True)
    ax.axis("equal")

    st.pyplot(fig)

    # -----------------------------
    # Fold plot
    # -----------------------------
    st.subheader("Fold vs CDP Number")

    fig2, ax2 = plt.subplots(figsize=(8, 3))
    ax2.plot(fold["CDP_NO"], fold["FOLD"], "-k")
    ax2.set_xlabel("CDP Number")
    ax2.set_ylabel("Fold")
    ax2.grid(True)

    st.pyplot(fig2)

    # -----------------------------
    # Download output
    # -----------------------------
    st.subheader("Download Results")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download CDP Table (CSV)",
        csv,
        "cdp_output.csv",
        "text/csv"
    )

else:
    st.info("Upload a geometry text file to begin.")
