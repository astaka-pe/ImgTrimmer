import streamlit as st
from utils import initialize_session_state, browse_images, paste_images, clear_all_images, display_images, display_canvas

def main():
    # Initialize session state variables
    uploaded_files = initialize_session_state()

    # File upload handler
    if uploaded_files:
        browse_images(uploaded_files)

    # Clipboard image load button
    if st.button("Load from clipboard"):
        paste_images()

    # Display images and delete buttons
    if st.session_state.images:
        display_images()

        if st.button("Clear all images"):
            clear_all_images()

        # Canvas functionality
        display_canvas()

if __name__ == "__main__":
    main()
