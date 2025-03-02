from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import uuid
from clipboard_utils import read_clipboard_images

def initialize_session_state():
    """Initialize session state variables if not already set"""
    if "images" not in st.session_state:
        st.session_state.images = []
        st.session_state.filenames = []
    
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = str(uuid.uuid4())
    
    uploaded_files = st.file_uploader(
        "Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key=st.session_state.file_uploader_key
    )
    return uploaded_files

def browse_images(uploaded_files):
    """Handle uploaded images and store them in session state"""
    for file in uploaded_files:
        if file.name not in st.session_state.filenames:
            image = Image.open(file)
            st.session_state.images.append(image)
            st.session_state.filenames.append(file.name)
    st.session_state.file_uploader_key = str(uuid.uuid4())  # Reset the uploader key to avoid duplication

def paste_images():
    clipboard_images = read_clipboard_images()
    if clipboard_images:
        for img in clipboard_images:
            filename = f"clipboard_{uuid.uuid4().hex[:8]}"
            st.session_state.images.append(img)
            st.session_state.filenames.append(filename)
        st.success(f"Loaded {len(clipboard_images)} images from clipboard!")
        st.rerun()

def clear_all_images():
    """Clear all images and reset session state"""
    st.session_state.images = []
    st.session_state.filenames = []
    st.session_state.file_uploader_key = str(uuid.uuid4())  # Reset the file uploader key
    st.rerun()

def display_images():
    images = st.session_state.images
    filenames = st.session_state.filenames

    images = resize_images(images, filenames)
    st.subheader("Input Images")
    num_cols = min(len(st.session_state.images), 4)
    cols = st.columns(num_cols)
    
    images_to_delete = []
    for i, (img, filename) in enumerate(zip(st.session_state.images, st.session_state.filenames)):
        col_idx = i % num_cols
        with cols[col_idx]:
            st.image(img, caption=filename, use_container_width=True)
            if st.button(f"Delete {filename}", key=f"delete_{i}"):
                images_to_delete.append(i)
    delete_image(images_to_delete)

def resize_images(images, filenames):
    img_size = images[0].size
    img_width, img_height = img_size

    for i, img in enumerate(images[1:], 1):
        if img.size != img_size:
            st.info(f"Resizing image '{filenames[i]}' from {img.size} to {img_size}")
            images[i] = img.resize(img_size)
    return images

def delete_image(images_to_delete):
    """Display delete buttons for images and handle removal"""
    if images_to_delete:
        for i in sorted(images_to_delete, reverse=True):
            del st.session_state.images[i]
            del st.session_state.filenames[i]
        st.rerun()

def display_canvas():
    """Display canvas for drawing and cropping images"""
    images = st.session_state.images
    filenames = st.session_state.filenames

    st.subheader("Drawing Canvas")
    selected_idx = st.selectbox("Select image for drawing", range(len(images)), format_func=lambda i: filenames[i])
    selected_image = images[selected_idx]

    img_width, img_height = selected_image.size
    canvas_width = 400
    scale = canvas_width / img_width
    canvas_height = int(img_height * scale)

    canvas_key = f"canvas_{selected_idx}"
    canvas_result = st_canvas(
        fill_color="rgba(0, 0, 0, 0)",  # Transparent fill
        stroke_width=3,
        stroke_color="red",
        background_image=selected_image.resize((canvas_width, canvas_height)),
        update_streamlit=True,
        height=canvas_height,
        width=canvas_width,
        drawing_mode="rect",
        key=canvas_key,
        initial_drawing=None,
    )

    # Handle rectangle selection for cropping
    if canvas_result.json_data is not None:
        objects = canvas_result.json_data["objects"]
        if objects:
            obj = objects[-1]
            x, y, w, h = int(obj["left"] / scale), int(obj["top"] / scale), int(obj["width"] / scale), int(obj["height"] / scale)

            cropped_images = [img.crop((x, y, x + w, y + h)) for img in images]

            st.subheader("Cropped Images")
            num_cols = min(len(images), 4)
            cols = st.columns(num_cols)
            for i, (cropped, filename) in enumerate(zip(cropped_images, filenames)):
                col_idx = i % num_cols
                with cols[col_idx]:
                    st.image(cropped, caption=filename, use_container_width=True)