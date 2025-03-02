import streamlit as st
from PIL import Image, ImageGrab
import io
from streamlit_drawable_canvas import st_canvas
import uuid
import win32clipboard

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

def read_clipboard_images():
    images = []
    try:
        win32clipboard.OpenClipboard()
        
        if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
            data = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
            image = Image.open(io.BytesIO(data))
            images.append(image)

        elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_HDROP):
            filepaths = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            for filepath in filepaths:
                try:
                    img = Image.open(filepath)
                    images.append(img)
                except Exception as e:
                    st.error(f"Error loading image {filepath}: {e}")

    except Exception as e:
        st.error(f"Error reading clipboard: {e}")

    finally:
        win32clipboard.CloseClipboard()

    return images

def main():
    if "images" not in st.session_state:
        st.session_state.images = []
        st.session_state.filenames = []
    
    if "file_uploader_key" not in st.session_state:
        st.session_state.file_uploader_key = str(uuid.uuid4())
    
    uploaded_files = st.file_uploader("Upload images", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key=st.session_state.file_uploader_key)

    if uploaded_files:
        for file in uploaded_files:
            if file.name not in st.session_state.filenames:
                image = Image.open(file)
                st.session_state.images.append(image)
                st.session_state.filenames.append(file.name)
        st.session_state.file_uploader_key = str(uuid.uuid4())

    clip_load, clear_all = st.columns(2)
    with clip_load:
        if st.button("Load from clipboard"):
            clipboard_images = read_clipboard_images()
            if clipboard_images:
                for clipboard_image in clipboard_images:
                    clipboard_filename = f"clipboard_{uuid.uuid4().hex[:8]}"
                    st.session_state.images.append(clipboard_image)
                    st.session_state.filenames.append(clipboard_filename)
                st.success(f"Loaded {len(clipboard_images)} images from clipboard!")
                st.rerun()
    
    with clear_all:
        if st.session_state.images and st.button("Clear all images"):
            st.session_state.images = []
            st.session_state.filenames = []
            st.session_state.file_uploader_key = str(uuid.uuid4())
            st.rerun()

    images = st.session_state.images
    filenames = st.session_state.filenames

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

        images_to_delete = []
        for i , (img, filename) in enumerate(zip(images, filenames)):
            col_idx = i % num_cols
            with cols[col_idx]:
                st.image(img, caption=filename, use_container_width=True)
                if st.button(f"Delete {filename}", key=f"delete_{i}"):
                    images_to_delete.append(i)
        
        if images_to_delete:
            for i in sorted(images_to_delete, reverse=True):
                del st.session_state.images[i]
                del st.session_state.filenames[i]
            st.rerun()

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