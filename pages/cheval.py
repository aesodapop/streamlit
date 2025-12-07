import streamlit as st
import os

# --- CONFIG ---
st.set_page_config(page_title="Cheval Hill Country Hideaway", layout="wide")

# Directory containing your images
IMAGE_DIR = "images"  # Folder containing your images

st.title("Cheval Hill Country Hideaway")
st.subheader("In the Heart of Wine Country – Stonewall, Texas")


# 🔥 CUSTOM ORDER + CUSTOM DISPLAY NAMES
custom_images = [
    {"file": "01_Entryway.jpg",        "name": "Front of the Property"},
    {"file": "02_Living Room.jpg",  "name": "Living Room"},
    {"file": "03_Living Room.jpg",      "name": "Living Room"},
    {"file": "04_Kitchen.jpg",     "name": "Kitchen"},
    {"file": "5_Kitchen.jpg",     "name": "Kitchen"},
    {"file": "5.5_Master.jpg",     "name": "Master Bedroom"},
    {"file": "06_Master.jpg",     "name": "Master Bedroom"},
    {"file": "07_Master Bath.jpg",     "name": "Master Bathroom"},
    {"file": "08_Guest Room.jpg",     "name": "Guest Bedroom 1"},
    {"file": "09_Guest Bath.jpg",     "name": "Guest Bathroom"},
    {"file": "10_Guest 2.jpg",     "name": "Guest Room 2"},
    {"file": "11_Exterior.jpg",     "name": "Exterior"},
    {"file": "12_View.jpg",     "name": "View"},
    {"file": "13_Exterior.jpg",     "name": "Exterior"},
    {"file": "111_Wine.jpg",     "name": ""}

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
