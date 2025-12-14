import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys

# ================= USER PARAMETERS =================
INPUT_FILE = "E:\Project_RadExPro\Data\GeomSprd2sxsy.txt"     # Input geometry file
OUTPUT_TRACE_FILE = "E:\Project_RadExPro\Data\cdp_traces2.txt"
OUTPUT_FOLD_FILE = "E:\Project_RadExPro\Data\cdp_fold2.txt"
RECEIVER_INTERVAL = 20.0        # meters
# ===================================================


def read_geometry(filename):
    """Read geometry file (space or comma delimited)."""
    try:
        df = pd.read_csv(filename, sep=",")
    except:
        df = pd.read_csv(filename, sep=",")

    required_cols = {"Sx", "Sy", "Rx", "Ry"}
    if not required_cols.issubset(df.columns):
        raise ValueError("Input file must contain columns: Sx Sy Rx Ry")

    return df


def assign_cmp_and_fold(df, receiver_interval):
    """Assign CMP numbers starting from min CMPx and compute fold."""

    cmp_spacing = receiver_interval / 2.0  # 10 m

    # Compute CMP coordinates
    df["CMPx"] = (df["Sx"] + df["Rx"]) / 2.0
    df["CMPy"] = (df["Sy"] + df["Ry"]) / 2.0

    # Reference CMPx (minimum CMPx)
    min_cmpx = df["CMPx"].min()

    # Assign CMP number starting from 1
    df["CMP"] = np.round((df["CMPx"] - min_cmpx) / cmp_spacing).astype(int) + 1

    # Compute fold per CMP
    fold_df = df.groupby("CMP").size().reset_index(name="Fold")

    return df, fold_df


def plot_cmp(df):
    """Plot CMPx vs CMPy."""
    plt.figure(figsize=(8, 4))
    plt.scatter(df["CMPx"], df["CMPy"], c=df["CMP"], cmap="viridis", s=20)
    plt.colorbar(label="CMP Number")
    plt.xlabel("CMP X (m)")
    plt.ylabel("CMP Y (m)")
    plt.title("CMP Geometry Plot (CMPx vs CMPy)")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def main():
    if not os.path.exists(INPUT_FILE):
        print(f"ERROR: File '{INPUT_FILE}' not found.")
        sys.exit(1)

    print("Reading geometry...")
    df = read_geometry(INPUT_FILE)

    print("Assigning CMP numbers and calculating fold...")
    df, fold_df = assign_cmp_and_fold(df, RECEIVER_INTERVAL)

    print("Writing output files...")
    df.to_csv(OUTPUT_TRACE_FILE, index=False, sep=" ")
    fold_df.to_csv(OUTPUT_FOLD_FILE, index=False, sep=" ")

    print("Plotting CMP geometry...")
    plot_cmp(df)

    print("\n=== PROCESSING COMPLETE ===")
    print(f"Trace file : {OUTPUT_TRACE_FILE}")
    print(f"Fold file  : {OUTPUT_FOLD_FILE}")
    print(f"Total CMPs : {fold_df['CMP'].max()}")
    print(f"Max Fold  : {fold_df['Fold'].max()}")


if __name__ == "__main__":
    main()
