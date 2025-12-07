import streamlit as st
import os

# --- CONFIG ---
st.set_page_config(page_title="Cheval Property Gallery", layout="wide")

# Directory containing your images
IMAGE_DIR = "images"  # Make sure this folder exists and contains your property images

st.title("Cheval Property Image Gallery")
st.write("")

# Load images
if not os.path.exists(IMAGE_DIR):
    st.error(f"Image directory '{IMAGE_DIR}' not found. Please create it and add images.")
else:
    image_files = [
        f for f in os.listdir(IMAGE_DIR)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))
    ]

    # ✅ Sort alphabetically (A → Z)
    image_files = sorted(image_files)

    if not image_files:
        st.warning("No images found in the directory.")
    else:
        cols = st.columns(3)
        for idx, img_name in enumerate(image_files):
            img_path = os.path.join(IMAGE_DIR, img_name)
            with cols[idx % 3]:
                st.image(img_path, use_column_width=True, caption=img_name)
