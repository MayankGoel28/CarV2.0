from image_handler import update_image, update_locs

import time
import streamlit as st

locs = {}

def get_display_data():
    batch = get_batch()
    locs = update_locs(locs, batch)
    return update_image(locs)

st.title("Dashboard")

display = st.empty()

while True:
    image = get_display_data()
    display.image(image)
    time.sleep(1)