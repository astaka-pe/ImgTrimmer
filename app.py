import streamlit as st
from PIL import Image, ImageGrab
import io
from streamlit_drawable_canvas import st_canvas


# Function to read image from clipboard
def read_clipboard_image():
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            return image
        else:
            print("No image found in clipboard.")
            return None
    except Exception as e:
        st.error(f"Error reading clipboard: {e}")
        return None

# Upload multiple images
uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

# Option to load image from clipboard
if st.button('Load from clipboard'):
    clipboard_image = read_clipboard_image()
    if clipboard_image is not None:
        uploaded_files.append(clipboard_image)

# Handling uploaded files
if uploaded_files:
    images = [Image.open(f) for f in uploaded_files]
    filenames = [f.name for f in uploaded_files]

    img_size = images[0].size
    img_width, img_height = img_size
    for img in images[1:]:
        assert img.size == img_size, f"Image sizes do not match! Found {img.size}, expected {img_size}"

    canvas_width = 150  # Set the canvas width
    scale = canvas_width / img_width  # Calculate scale factor
    canvas_height = int(img_height * scale)  # Calculate height to maintain aspect ratio

    st.subheader("Input Images")
    key = 0
    cols = st.columns(len(images))
    for i in range(len(cols)):
        with cols[i]:
            if i == 0:
                canvas_result = st_canvas(
                    fill_color="rgba(0, 0, 0, 0)",  # Transparent fill
                    stroke_width=3,
                    stroke_color="red",
                    background_image=images[0].resize((canvas_width, canvas_height)),  # Show the first image as reference
                    update_streamlit=True,
                    height=canvas_height,
                    width=canvas_width,
                    drawing_mode="rect",
                    key="canvas",
                    initial_drawing=None,
                )
            else:
                st.image(images[i], caption=filenames[i], width=canvas_width)
    
    # Create a canvas to draw cropping rectangle

    if canvas_result.json_data is not None:
        # Extract rectangle coordinates from the canvas
        objects = canvas_result.json_data["objects"]
        if objects:
            obj = objects[-1]  # Take the first rectangle
            x, y, w, h = int(obj["left"] / scale), int(obj["top"] / scale), int(obj["width"] / scale), int(obj["height"] / scale)

            # Crop images using the selected region
            cropped_images = [img.crop((x, y, x + w, y + h)) for img in images]

            st.subheader("Cropped Images")
            cols = st.columns(len(cropped_images))
            for i in range(len(cols)):
                with cols[i]:
                    st.image(cropped_images[i], caption=filenames[i], use_container_width=True)

            # Provide download buttons
            for i, cropped in enumerate(cropped_images):
                buffer = io.BytesIO()
                cropped.save(buffer, format="PNG")
