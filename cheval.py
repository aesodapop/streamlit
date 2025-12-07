import streamlit as st
import os

pg = st.navigation([st.Page("About.py"), st.Page("Gallery.py")])
pg.run()

# --- CONFIG ---
st.set_page_config(
    page_title="Cheval Hill Country Hideaway", 
    layout="wide")

# Directory containing your images
IMAGE_DIR = "images"  # Folder containing your images

st.title("Cheval Hill Country Hideaway")
st.subheader("In the Heart of Wine Country – Stonewall, Texas")

st.write("""
Escape to our charming **3-bedroom, 2-bath retreat** nestled in the rolling hills of
Stonewall—right in the center of Texas Wine Country. Whether you’re planning a
weekend getaway or a relaxed country escape, this cozy home offers comfort, serenity,
and unbeatable access to the area’s best attractions.

Just minutes from award-winning **wineries, distilleries, and tasting rooms**, you’ll
have your choice of memorable Hill Country experiences. Spend the day exploring local
vineyards, sipping spirits, or enjoying the nearby historic towns of **Fredericksburg** and
**Johnson City**.

After a day out, unwind on the large **front porch** outfitted with classic rocking
chairs—perfect for sunsets and slow mornings.
""")

st.markdown("### Inside the Home")
st.write("""
- Three comfortable bedrooms ideal for families or small groups  
- Two full bathrooms stocked with essentials  
- A welcoming living space and fully equipped kitchen  

Whether you're here for wine tours, a peaceful retreat, or to explore the natural beauty
of the Hill Country, our Stonewall home is the perfect base for your adventure.

**No pets and no smokers please.**
""")

st.markdown("### Sleeping Arrangements")
st.write("""
- **Bedroom 1:** King Bed  
- **Bedroom 2:** Queen Bed  
- **Bedroom 3:** Queen Bed  
""")

st.markdown("### Bathroom Details")
st.write("""
- **Bathroom 1:** Shower and tub for 2  
- **Bathroom 2:** Shower/tub combo  
""")

st.markdown("### Kitchen Amenities")
st.write("""
- Stove  
- Fridge  
- Keurig (coffee pods provided)  
- Microwave  
- Cooking essentials  
""")

st.markdown("## Guest Access")
st.write("""
On the **day of check-in**, you will receive an **Access Code Email at 4:00 PM**, which will include:

- Property address  
- Door code and instructions  
- **24-hour on-call phone number** (main contact for any questions or issues during your stay)
""")


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
