import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# USER PARAMETERS
# -----------------------------
GEOM_FILE = "E:\Project_RadExPro\Data\GeomSprd2sxsy.txt"    # input text file
RECEIVER_SPACING = 20.0      # meters
CDP_SPACING = RECEIVER_SPACING / 2  # 10 m

# -----------------------------
# 1. Read geometry file
# -----------------------------
df = pd.read_csv(GEOM_FILE, sep=',')

required_cols = {"Sx", "Sy", "Rx", "Ry"}
if not required_cols.issubset(df.columns):
    raise ValueError("File must contain columns: Sx, Sy, Rx, Ry")

if df.empty:
    raise ValueError("Input geometry file is empty")

print(f"Loaded {len(df)} traces")

# Preserve original order
df["ORIG_IDX"] = df.index

# -----------------------------
# 2. CDP midpoint calculation
# -----------------------------
df["CDP_X"] = (df["Sx"] + df["Rx"]) / 2.0
df["CDP_Y"] = (df["Sy"] + df["Ry"]) / 2.0

# -----------------------------
# 3. Sort midpoints for distance calculation
# -----------------------------
df_sorted = df.sort_values(by=["CDP_X", "CDP_Y"]).reset_index(drop=True)

# -----------------------------
# 4. Distance along crooked line
# -----------------------------
dx = df_sorted["CDP_X"].diff().fillna(0.0)
dy = df_sorted["CDP_Y"].diff().fillna(0.0)
df_sorted["DIST_ALONG_LINE"] = np.sqrt(dx**2 + dy**2).cumsum()

# -----------------------------
# 5. CDP binning
# -----------------------------
df_sorted["CDP_BIN"] = np.round(df_sorted["DIST_ALONG_LINE"] / CDP_SPACING).astype(int)

# -----------------------------
# 6. Assign CDP numbers
# -----------------------------
df_sorted["CDP_NO"] = df_sorted.groupby("CDP_BIN").ngroup() + 1

# -----------------------------
# 7. Fold per CDP
# -----------------------------
fold = df_sorted.groupby("CDP_NO").size().reset_index(name="FOLD")
df_sorted = df_sorted.merge(fold, on="CDP_NO", how="left")

# -----------------------------
# 8. Merge results back to original order
# -----------------------------
df_final = df.merge(
    df_sorted[["ORIG_IDX", "DIST_ALONG_LINE", "CDP_BIN", "CDP_NO", "FOLD"]],
    on="ORIG_IDX",
    how="left"
).drop(columns="ORIG_IDX")

# -----------------------------
# 9. Save output tables
# -----------------------------
df_final.to_csv("E:\\Project_RadExPro\\Data\\cdp_output.txt", index=False)
fold.to_csv("E:\\Project_RadExPro\\Data\\fold_table.txt", index=False)

print("Output written:")
print(" - cdp_output.txt")
print(" - fold_table.txt")

# -----------------------------
# 10. CDP X–Y geometry plot
# -----------------------------
cdp_curve = df_final.groupby("CDP_NO")[["CDP_X", "CDP_Y", "FOLD"]].mean().reset_index()

plt.figure(figsize=(10, 4))
scatter = plt.scatter(
    cdp_curve["CDP_X"],
    cdp_curve["CDP_Y"],
    c=cdp_curve["FOLD"],       # color by fold
    cmap="viridis",
    s=50,
    edgecolor="k"
)
plt.xlabel("CDP X (m)")
plt.ylabel("CDP Y (m)")
plt.title("Crooked-Line 2D CDP Geometry (Colored by Fold)")
plt.grid(True)
plt.axis("equal")
cbar = plt.colorbar(scatter)
cbar.set_label("Fold")
plt.tight_layout()
plt.show()
# -----------------------------
# 11. Fold plot
# -----------------------------
plt.figure(figsize=(8, 3))
plt.plot(fold["CDP_NO"], fold["FOLD"], "-k")
plt.xlabel("CDP Number")
plt.ylabel("Fold")
plt.title("Fold vs CDP")
plt.grid(True)
plt.tight_layout()
plt.show()
