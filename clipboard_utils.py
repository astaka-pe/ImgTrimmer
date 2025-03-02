import win32clipboard
import io
from PIL import Image
import streamlit as st

def read_clipboard_images():
    """Read images from clipboard and return them as a list"""
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
