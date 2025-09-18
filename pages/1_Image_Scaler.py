

import io
import streamlit as st
from PIL import Image, ImageOps

st.set_page_config(page_title="Image Scaler", page_icon="🖼️", layout="wide")

st.markdown("""
<style>
div.stButton > button {
    background-color: #14532d !important; /* dark green fill */
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5em 1.5em !important;
    font-size: 1.08em !important;
    font-weight: 600 !important;
    transition: background 0.2s;
}
div.stButton > button:hover {
    background-color: #d1d5db !important; /* lighter gray on hover */
    color: #fff !important;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<h1 style='font-size:2.3em; color:#14532d; margin-bottom:0.5em;'>Image Scaler</h1>
<div style='font-size:1.15em; color:#222; margin-bottom:2em;'>Resize, crop, and preview your project images for website and Instagram formats.</div>
""", unsafe_allow_html=True)

def fit_image_with_offset(img: Image.Image, frame_w, frame_h, zoom=1.0, offset_x=0.0, offset_y=0.0):
    base = ImageOps.exif_transpose(img).convert("RGB")
    iw, ih = base.size
    target_ratio = frame_w / frame_h
    img_ratio = iw / ih

    # Calculate scale to cover the frame
    if img_ratio > target_ratio:
        scale = frame_h / ih
    else:
        scale = frame_w / iw
    scale *= max(zoom, 0.1)

    new_w = int(iw * scale)
    new_h = int(ih * scale)
    scaled = base.resize((new_w, new_h), Image.LANCZOS)

    # Center the image, then apply offset
    max_dx = max(0, new_w - frame_w)
    max_dy = max(0, new_h - frame_h)
    # Offset is always relative to center
    px = int((frame_w - new_w) / 2 - (max_dx / 2) * offset_x)
    py = int((frame_h - new_h) / 2 - (max_dy / 2) * offset_y)

    canvas = Image.new("RGB", (frame_w, frame_h), (255, 255, 255))
    canvas.paste(scaled, (px, py))
    return canvas

def show_framed_image(img, caption, aspect_w, aspect_h):
    import base64
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    # Responsive width: fill container, keep aspect ratio
    html = f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        max-width: 900px;
        margin: 0 auto 16px auto;
    ">
      <div style="
        border:2px solid #444;
        border-radius:18px;
        background:#222;
        overflow:hidden;
        width:100%;
        aspect-ratio:{aspect_w}/{aspect_h};
        box-sizing:border-box;
        display:flex;
        align-items:center;
        justify-content:center;
      ">
        <img src="data:image/png;base64,{b64}" style="
            width:100%;
            height:100%;
            object-fit:cover;
            display:block;
        ">
      </div>
    </div>
    <div style="font-size:1rem;margin-bottom:1.5em;text-align:center;">{caption}</div>
    """
    st.markdown(html, unsafe_allow_html=True)

def copy_image_button(label, img: Image.Image):
    import base64
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    html = f"""
    <button id="cpy_{hash(b64)}" style="padding:8px 12px;border:1px solid #198754;border-radius:8px;background:#222;color:white;cursor:pointer;margin-bottom:8px;">
        {label}
    </button>
    <span id="msg_{hash(b64)}" style="margin-left:8px;color:#198754;"></span>
    <script>
    const btn = document.getElementById("cpy_{hash(b64)}");
    const msg = document.getElementById("msg_{hash(b64)}");
    btn.addEventListener("click", async () => {{
      try {{
        const b = atob("{b64}");
        const len = b.length;
        const bytes = new Uint8Array(len);
        for (let i=0; i<len; i++) bytes[i] = b.charCodeAt(i);
        const blob = new Blob([bytes], {{type: "image/png"}});
        await navigator.clipboard.write([new ClipboardItem({{"image/png": blob}})]);
        msg.textContent = "Copied!";
        setTimeout(() => msg.textContent = "", 1600);
      }} catch(e) {{
        msg.textContent = "Copy failed";
        setTimeout(() => msg.textContent = "", 1600);
      }}
    }});
    </script>
    """
    st.components.v1.html(html, height=60)

base_img = st.session_state.get("base_img", None)
if base_img:
    st.subheader("Website Hero Image (1600×900)")
    colZ1, colXY1 = st.columns([1,1])
    with colZ1:
        zoom_web = st.slider("Website Zoom", 0.1, 3.0, 1.0, 0.01, key="zoom_web")
    with colXY1:
        offset_x_web = st.slider("Website Pan X", -1.0, 1.0, 0.0, 0.01, key="offset_x_web")
        offset_y_web = st.slider("Website Pan Y", -1.0, 1.0, 0.0, 0.01, key="offset_y_web")
    hero = fit_image_with_offset(base_img, 1600, 900, zoom_web, offset_x_web, offset_y_web)
    show_framed_image(hero, "Hero 1600×900 (website)", 1600, 900)
    buf_h = io.BytesIO(); hero.save(buf_h, "JPEG", quality=92)
    st.download_button("Download hero (JPEG)", data=buf_h.getvalue(), file_name="web_hero_1600x900.jpg", mime="image/jpeg")
    copy_image_button("Copy website image", hero)
    # Save website image as bytes in session_state
    buf_h_png = io.BytesIO(); hero.save(buf_h_png, "PNG")
    st.session_state["website_img"] = buf_h_png.getvalue()

    st.subheader("Instagram Image (1080×1080)")
    colZ2, colXY2 = st.columns([1,1])
    with colZ2:
        zoom_insta = st.slider("Instagram Zoom", 0.1, 3.0, 1.0, 0.01, key="zoom_insta")
    with colXY2:
        offset_x_insta = st.slider("Instagram Pan X", -1.0, 1.0, 0.0, 0.01, key="offset_x_insta")
        offset_y_insta = st.slider("Instagram Pan Y", -1.0, 1.0, 0.0, 0.01, key="offset_y_insta")
    insta = fit_image_with_offset(base_img, 1080, 1080, zoom_insta, offset_x_insta, offset_y_insta)
    show_framed_image(insta, "Instagram 1080×1080", 1080, 1080)
    buf_i = io.BytesIO(); insta.save(buf_i, "PNG")
    st.download_button("Download Instagram (PNG)", data=buf_i.getvalue(), file_name="instagram_1080.png", mime="image/png")
    copy_image_button("Copy Instagram image", insta)
    # Save Instagram image as bytes in session_state
    st.session_state["instagram_img"] = buf_i.getvalue()
else:
    st.info("No image uploaded. Please upload an image in the main page sidebar.")