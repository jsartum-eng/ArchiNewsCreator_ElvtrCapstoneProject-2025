import streamlit as st
import openai
from PIL import Image
import io

st.set_page_config(page_title="Instagram Content", page_icon="📸", layout="wide")
st.markdown("""
<h1 style='font-size:2.3em; color:#14532d; margin-bottom:0.5em;'>Instagram Content Generator</h1>
<div style='font-size:1.15em; color:#222; margin-bottom:2em;'>Create and preview Instagram captions, images, and hashtags for your project.</div>
""", unsafe_allow_html=True)
import base64

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

# Example initialization for img_bytes and col_right
img_bytes = b""  # Replace with actual image bytes as needed
img_data = base64.b64encode(img_bytes).decode()

col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("### Instagram Image – Live Preview")
    img_bytes = st.session_state.get("instagram_img", None)
    img_box_style = "background:#fff;max-width:320px;width:320px;height:320px;margin:auto;border-radius:18px;box-shadow:0 2px 12px #0002;display:flex;align-items:center;justify-content:center;padding:0;margin-bottom:1.2em;"
    if img_bytes:
        import base64
        img_data = base64.b64encode(img_bytes).decode()
        st.markdown(f"""
            <div style='{img_box_style}'>
                <img src='data:image/png;base64,{img_data}' style='width:100%;height:100%;object-fit:cover;border-radius:18px;'>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='{img_box_style}color:#aaa;font-size:1.2em;'>No Image</div>", unsafe_allow_html=True)

    st.markdown("### Caption Preview")
    clean_caption = st.session_state.get("generated_caption", "")
    st.markdown(f'''
        <div style="
            max-width:320px;
            margin:auto;
            border-radius:18px;
            box-shadow:0 2px 12px #0002;
            display:flex;
            align-items:center;
            justify-content:center;
            padding:0;
        ">
            <div style="
                font-family:Arial,sans-serif;
                font-size:18px;
                margin:0;
                text-align:center;
                padding:16px;
                overflow-y:auto;
                max-height:90%;
                width:100%;
                word-break:break-word;
            ">
                {clean_caption}
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown("<div style='height: 1.5em'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Download Caption",
        data=clean_caption,
        file_name="caption.txt",
        mime="text/plain",
        key="download_caption"
    )
    st.markdown("<div style='height: 2em'></div>", unsafe_allow_html=True)

    st.markdown("### Hashtags Preview")
    web_content = st.session_state.get("web", None)
    hashtags = ""
    auto_hashtags = []
    if web_content is not None:
        long_preview = web_content.get("long", {})
        long_text = long_preview.get("title", "")
        sections = long_preview.get("sections", [])
        if sections and isinstance(sections[0], dict):
            long_text += " " + sections[0].get("body", "")
        # Use OpenAI to generate hashtags
        if long_text.strip():
            prompt = f"Generate 15 relevant hashtags for the following Instagram post:\n{long_text}\nOnly output hashtags separated by spaces."
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=150,
                    temperature=0.7
                )
                hashtags_text = response.choices[0].message.content.strip()
                auto_hashtags = [tag for tag in hashtags_text.split() if tag.startswith("#")][:15]
            except Exception as e:
                auto_hashtags = []
    custom_hashtags = st.session_state.get("custom_hashtags", ["#architecture", "#design"])
    ticked_hashtags = [tag for tag in custom_hashtags if st.session_state.get(f"hashtag_{tag}", False)]
    # Only show ticked custom hashtags, and 15 auto hashtags
    all_hashtags = auto_hashtags + ticked_hashtags
    if all_hashtags:
        hashtags = " ".join(all_hashtags)
    else:
        hashtags = "No hashtags generated. Please check your website content or select custom hashtags."
    st.session_state["generated_hashtags"] = hashtags
    st.markdown(f'''
        <div style="
            background:#fff;
            min-height:80px;
            max-width:320px;
            margin:auto;
            border-radius:18px;
            box-shadow:0 2px 12px #0002;
            display:flex;
            align-items:center;
            justify-content:center;
            padding:0;
        ">
            <div style="
                font-family:Arial,sans-serif;
                font-size:18px;
                margin:0;
                text-align:center;
                padding:16px;
                overflow-y:auto;
                max-height:90%;
                width:100%;
                word-break:break-word;
            ">
                {hashtags}
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown("<div style='height: 1.5em'></div>", unsafe_allow_html=True)
    st.download_button(
        label="Download Hashtags",
        data=hashtags,
        file_name="hashtags.txt",
        mime="text/plain",
        key="download_hashtags"
    )

with col_right:
    # Controls and customization
    col_len1, col_len2, col_len3 = st.columns(3)

    def auto_generate_caption(length):
        web = st.session_state.get("web", None)
        if web is not None:
            long_preview = web.get("long", {})
            website_text = long_preview.get("title", "")
            sections = long_preview.get("sections", [])
            if sections and isinstance(sections[0], dict):
                website_text += " " + sections[0].get("body", "")
            website_text = website_text.strip()
            all_endings = st.session_state.get("caption_endings", ["www.scherzer-architekten.de", "Photo: Max Mustermann"])
            ticked_endings = [e for e in all_endings if st.session_state.get(f"ending_{e}", False)]
            caption_style = st.session_state.get("caption_style", "neutral")
            if not website_text:
                main_caption = "[No website content available. Please generate website content first.]"
            else:
                prompt = f"""
You are an expert social media copywriter. Write an Instagram caption for the following architecture project, using the given style/tone and length. Do NOT repeat the website headline. Make it engaging and suitable for Instagram.

Project text:
{website_text}

Style/Tone: {caption_style}
Length: {length} characters

Only output the caption text, no hashtags, no headline.
"""
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=length+50,
                        temperature=0.7
                    )
                    main_caption = response.choices[0].message.content.strip()
                except Exception as exc:
                    main_caption = f"[Error generating caption: {exc}]"
            # Append only ticked endings, each on a new line
            if ticked_endings:
                main_caption += "\n" + "\n".join(ticked_endings)
            st.session_state["generated_caption"] = main_caption
            st.session_state["caption_length"] = length
            st.rerun()

    with st.container():
        if col_len1.button("Short 80", key="caption_len_short"):
            auto_generate_caption(80)
        if col_len2.button("Medium 200", key="caption_len_medium"):
            auto_generate_caption(200)
        if col_len3.button("Long 400", key="caption_len_long"):
            auto_generate_caption(400)
            auto_generate_caption(400)
    # 1. Caption Style
    st.markdown("#### Choose Caption Style/Tone")
    caption_styles = ["neutral", "enthusiastic", "conversational", "formal"]
    caption_style = st.selectbox("Caption Style", caption_styles, index=0, key="caption_style")

    # 2. Caption Length
    # ...existing code...

    # 3. Custom Endings
    st.markdown("#### Add custom endings to captions")
    default_endings = ["www.scherzer-architekten.de", "Photo: Max Mustermann"]
    endings = st.session_state.get("caption_endings", default_endings)
    selected_endings = []
    for ending in endings:
        if st.checkbox(ending, key=f"ending_{ending}"):
            selected_endings.append(ending)
    new_ending = st.text_input("Add custom ending", "")
    if st.button("Add ending"):
        if new_ending and new_ending not in endings:
            endings.append(new_ending)
            st.session_state["caption_endings"] = endings
            st.rerun()

    # 4. Custom Hashtags
    st.markdown("---")
    st.markdown("#### Add custom hashtags to list")
    custom_hashtags = st.session_state.get("custom_hashtags", ["#architecture", "#design"])
    selected_hashtags = st.session_state.get("selected_hashtags", [])
    new_hashtag = st.text_input("Add custom hashtag", "", key="new_hashtag")
    if st.button("Add hashtag", key="add_hashtag_btn"):
        if new_hashtag and new_hashtag not in custom_hashtags:
            custom_hashtags.append(new_hashtag)
            st.session_state["custom_hashtags"] = custom_hashtags
            st.rerun()

    st.markdown("#### Select hashtags to include")
    selected_hashtags = []
    for tag in custom_hashtags:
        if st.checkbox(tag, key=f"hashtag_{tag}"):
            selected_hashtags.append(tag)
    st.session_state["selected_hashtags"] = selected_hashtags






