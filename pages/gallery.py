import streamlit as st
import os

# --- CONFIG ---
st.set_page_config(
  page_title="Cheval Hill Country Hideaway", 
  layout="wide")

st.subheader("In the Heart of Wine Country – Stonewall, Texas")

# Directory containing your images
IMAGE_DIR = "images"  # Folder containing your images

custom_images = [
    {"file": "01_Entryway.jpg",        "name": "Entryway"}
    ]

# ---------------------------------------------------------
# Load and validate images
# ---------------------------------------------------------
if not os.path.exists(IMAGE_DIR):
    st.error(f"Image directory '{IMAGE_DIR}' not found. Please create it and add images.")
else:

    available_files = [
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    # Filter only the custom images that exist
    valid_images = [img for img in custom_images if img["file"] in available_files]

    # Warn if missing files
    missing = [img["file"] for img in custom_images if img["file"] not in available_files]
    if missing:
        st.warning(f"These images were not found: {missing}")

    if not valid_images:
        st.warning("No valid images found in the directory.")
    else:
        cols = st.columns(3)
        for idx, img in enumerate(valid_images):
            img_path = os.path.join(IMAGE_DIR, img["file"])
            with cols[idx % 3]:
                st.image(img_path, caption=img["name"])


