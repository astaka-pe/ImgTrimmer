import streamlit as st
from PIL import Image, ImageGrab
import io
from streamlit_drawable_canvas import st_canvas
import uuid

def read_clipboard_image():
    try:
        image = ImageGrab.grabclipboard()
        if isinstance(image, Image.Image):
            return image
        else:
            st.warning("No image found in clipboard.")
            return None
    except Exception as e:
        st.error(f"Error reading clipboard: {e}")
        return None

def main():
    if "clipboard_images" not in st.session_state:
        st.session_state.clipboard_images = []
        st.session_state.clipboard_filenames = []
    
    uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

    clip_load, clip_clear = st.columns(2)
    with clip_load:
        if st.button("Load from clipboard"):
            clipboard_image = read_clipboard_image()
            if clipboard_image:
                # Generate unique filename with timestamp
                clipboard_filename = f"clipboard_{uuid.uuid4().hex[:8]}"
                st.session_state.clipboard_images.append(clipboard_image)
                st.session_state.clipboard_filenames.append(clipboard_filename)
                st.success("Image loaded from clipboard!")
                st.rerun()
    
    with clip_clear:
        if st.session_state.clipboard_images and st.button("Clear clipboard images"):
            st.session_state.clipboard_images = []
            st.session_state.clipboard_filenames = []
            st.rerun()
    
    images = []
    filenames = []

    if uploaded_files:
        images = [Image.open(f) for f in uploaded_files]
        filenames = [f.name for f in uploaded_files]

    images.extend(st.session_state.clipboard_images)
    filenames.extend(st.session_state.clipboard_filenames)

    if images:
        img_size = images[0].size
        img_width, img_height = img_size

        for i, img in enumerate(images[1:], 1):
            if img.size != img_size:
                st.info(f"Resizing image '{filenames[i]}' from {img.size} to {img_size}")
                images[i] = img.resize(img_size)

        canvas_width = 400
        scale = canvas_width / img_width
        canvas_height = int(img_height * scale)

        st.subheader("Input Images")
        num_cols = min(len(images), 4)
        cols = st.columns(len(images))
        for i , (img, filename) in enumerate(zip(images, filenames)):
            col_idx = i % num_cols
            with cols[col_idx]:
                st.image(img, caption=filename, use_container_width=True)

        st.subheader("Drawing Canvas")
        selected_idx = st.selectbox("Select image for drawing", range(len(images)), format_func=lambda i: filenames[i])
        selected_image = images[selected_idx]
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
        
        # Create a canvas to draw cropping rectangle
        if canvas_result.json_data is not None:
            objects = canvas_result.json_data["objects"]
            if objects:
                obj = objects[-1]
                x, y, w, h = int(obj["left"] / scale), int(obj["top"] / scale), int(obj["width"] / scale), int(obj["height"] / scale)

                cropped_images = [img.crop((x, y, x + w, y + h)) for img in images]

                st.subheader("Cropped Images")
                cropped_cols = st.columns(num_cols)
                for i, (cropped, filename) in enumerate(zip(cropped_images, filenames)):
                    col_idx = i % num_cols
                    with cropped_cols[col_idx]:
                        st.image(cropped, caption=filename, use_container_width=True)
                        buffer = io.BytesIO()
                        cropped.save(buffer, format="PNG")
                        st.download_button(
                            label=f"Download {filename}",
                            data=buffer.getvalue(),
                            file_name=f"cropped_{filename}.png",
                            mime="image/png"
                        )

if __name__ == "__main__":
    main()