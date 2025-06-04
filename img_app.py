# Import libraries
import streamlit as st
from io import BytesIO
from PIL import Image
import numpy as np
import imageio
import os

# Preset: Change colors of all slider elements using CSS custom styles
ColorMinMax = st.markdown(''' <style> div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {
            background: rgb(1 1 1 / 0%); } </style>''', unsafe_allow_html = True)

Slider_Cursor = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{
            background-color: rgb(255, 255, 255); box-shadow: rgb(100 100 255 / 100%) 0px 0px 0px 0.2rem;} </style>''', unsafe_allow_html = True)

Slider_Number = st.markdown(''' <style> div.stSlider > div[data-baseweb="slider"] > div > div > div > div
                                        { color: rgb(255, 255, 255); } </style>''', unsafe_allow_html = True)

col = f''' <style> div.stSlider > div[data-baseweb = "slider"] > div > div {{
            background: rgb(0, 0, 0); }} </style>'''
ColorSlider = st.markdown(col, unsafe_allow_html = True)

def equalize_channel(channel_data):
    # Hitung histogram
    histogram = [0] * 256
    for pixel in channel_data:
        histogram[pixel] += 1

    # Hitung CDF
    cdf = [0] * 256
    cumulative = 0
    for i in range(256):
        cumulative += histogram[i]
        cdf[i] = cumulative

    # Normalisasi CDF
    cdf_min = min(val for val in cdf if val > 0)
    total_pixels = len(channel_data)
    cdf_normalized = [round((val - cdf_min) * 255 / (total_pixels - cdf_min)) if val > 0 else 0 for val in cdf]

    # Mapping piksel
    equalized_data = [cdf_normalized[p] for p in channel_data]
    return equalized_data

def rgb_histogram_equalization(image):
    width, height = image.size
    r_data, g_data, b_data = image.split()
    r_pixels = list(r_data.getdata())
    g_pixels = list(g_data.getdata())
    b_pixels = list(b_data.getdata())

    # Equalisasi masing-masing channel
    r_eq = equalize_channel(r_pixels)
    g_eq = equalize_channel(g_pixels)
    b_eq = equalize_channel(b_pixels)

    # Gabungkan kembali channel
    r_img = Image.new("L", (width, height))
    r_img.putdata(r_eq)
    g_img = Image.new("L", (width, height))
    g_img.putdata(g_eq)
    b_img = Image.new("L", (width, height))
    b_img.putdata(b_eq)

    # Gabungkan channel jadi gambar RGB
    equalized_img = Image.merge("RGB", (r_img, g_img, b_img))
    return equalized_img


def process_image(input_image, r_gain, g_gain, b_gain, brightness, contrast, flip, flop, equalize):
    img = input_image.copy()

    if flip:
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if flop:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)

    # Histogram equalization (on grayscale, converted back to RGB)
    if equalize:
        img = rgb_histogram_equalization(img)

    # RGB gain
    img_np = np.array(img).astype(np.float32)
    img_np[..., 0] *= r_gain    
    img_np[..., 1] *= g_gain
    img_np[..., 2] *= b_gain
    img_np = np.clip(img_np, 0, 255).astype(np.uint8)
    img = Image.fromarray(img_np)

    # Brightness and contrast

    img = np.array(img).astype(np.float32)  # ubah tipe data menjadi float untuk operasi matematis
    img *= brightness       # Adjust brightness

    mean = 128
    img = mean + (img - mean) * contrast    # Adjust contrast
    img = np.clip(img, 0, 255).astype(np.uint8)
    img = Image.fromarray(img)


    return img

def main():
    st.markdown("## :blue[Tugas Project Pengolahan Citra Digital]")  # Updated title
    st.markdown("##### Mochamad Fathurahman Aldesrand (1301220325)")
    st.markdown("##### Robby Kishan Pardamean (1301223242)")
    st.markdown("##### Krisna Aditya David Putra (1301223132)")
    st.divider()

    uploaded_file = st.file_uploader(" #### :camera: :blue[1. Upload Image] ", type=["JPG", "JPEG", "PNG"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")

        # Initialize session state variables if not already present
        if 'original_image' not in st.session_state:
            st.session_state.original_image = image.copy()

        # Initialize attributes if not already present
        if 'r_gain' not in st.session_state:
            st.session_state.r_gain = 1.0
        if 'g_gain' not in st.session_state:
            st.session_state.g_gain = 1.0
        if 'b_gain' not in st.session_state:
            st.session_state.b_gain = 1.0
        if 'brightness' not in st.session_state:
            st.session_state.brightness = 1.0
        if 'contrast' not in st.session_state:
            st.session_state.contrast = 1.0
        if 'flip' not in st.session_state:
            st.session_state.flip = False
        if 'flop' not in st.session_state:
            st.session_state.flop = False
        if 'equalize' not in st.session_state:
            st.session_state.equalize = False

        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        st.divider()

        st.write("#### :crystal_ball: :blue[2. Adjust Image Parameters]")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.r_gain = st.slider("Red Channel", 0.0, 2.0, st.session_state.r_gain, 0.05)
            st.session_state.brightness = st.slider("Brightness", 0.0, 2.0, st.session_state.brightness, 0.1)
        with col2:
            st.session_state.g_gain = st.slider("Green Channel", 0.0, 2.0, st.session_state.g_gain, 0.05)
            st.session_state.contrast = st.slider("Contrast", 0.0, 2.0, st.session_state.contrast, 0.1)
        with col3:
            st.session_state.b_gain = st.slider("Blue Channel", 0.0, 2.0, st.session_state.b_gain, 0.05)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.flip = st.checkbox("Flip Vertical", st.session_state.flip)
        with col2:
            st.session_state.flop = st.checkbox("Flip Horizontal", st.session_state.flop)
        with col3:
            st.session_state.equalize = st.checkbox("Histogram Equalization", st.session_state.equalize)

        if st.button("🔁 Reset to Original"):
            st.session_state.r_gain = 1.0
            st.session_state.g_gain = 1.0
            st.session_state.b_gain = 1.0
            st.session_state.brightness = 1.0
            st.session_state.contrast = 1.0
            st.session_state.flip = False
            st.session_state.flop = False
            st.session_state.equalize = False

        processed_image_pil = process_image(
            st.session_state.original_image,
            st.session_state.r_gain,
            st.session_state.g_gain,
            st.session_state.b_gain,
            st.session_state.brightness,
            st.session_state.contrast,
            st.session_state.flip,
            st.session_state.flop,
            st.session_state.equalize
        )

        st.image(processed_image_pil, caption="Processed Image", use_container_width=True)

        original_name, original_extension = os.path.splitext(uploaded_file.name)
        processed_image_name_jpeg = f"{original_name}_processed.jpg"
        processed_image_name_png = f"{original_name}_processed.png"

        st.divider()
        st.caption("Preparing Download... Please wait.")

        jpeg_buffer = BytesIO()
        processed_image_pil.save(jpeg_buffer, format="JPEG")
        jpeg_data = jpeg_buffer.getvalue()

        png_buffer = BytesIO()
        imageio.imwrite(png_buffer, np.array(processed_image_pil), format='PNG')
        png_data = png_buffer.getvalue()

        st.markdown(f"#### :floppy_disk: :blue[3. Download Processed Image] ")
        st.write('Download image in :file_folder: :blue[JPG] or :file_folder: :blue[PNG] file format:')

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label=f":file_folder: :blue[JPG] ({processed_image_name_jpeg})",
                data=jpeg_data,
                file_name=processed_image_name_jpeg,
                key="processed_image_download_jpeg",
            )
        with col2:
            st.download_button(
                label=f":file_folder: :blue[PNG] ({processed_image_name_png})",
                data=png_data,
                file_name=processed_image_name_png,
                key="processed_image_download_png",
            )

if __name__ == "__main__":
    main()
