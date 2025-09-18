import streamlit as st
import textwrap
import os
import json
import re
import openai

def style_headline(text, font, size, color):
    return f'<div style="font-size:{size}px;font-weight:700;margin-bottom:0.2em;font-family:{font}, Century, Arial, sans-serif;color:{color};">{text}</div>'

def style_body(text, font, size, color):
    return f'<div style="font-size:{size}px;line-height:1.6;font-family:{font}, Century, Arial, sans-serif;color:{color};">{text}</div>'

def style_project_info_grid(items):
    grid_html = '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.2em 2em;margin-bottom:1.2em;">'
    for label, value in items:
        grid_html += f'<div style="color:#888;font-size:13px;font-family:Century Gothic, Century, Arial, sans-serif;">{label}: <span style="color:#888;">{value}</span></div>'
    grid_html += '</div>'
    return grid_html

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

# (Removed duplicate/incomplete style_headline, style_body, and style_project_info_grid definitions)
st.set_page_config(page_title="Website Content", page_icon="📰", layout="wide")
st.markdown("""
<h1 style='font-size:2.3em; color:#14532d; margin-bottom:0.5em;'>Website Content Generator</h1>
<div style='font-size:1.15em; color:#222; margin-bottom:2em;'>Create and preview website headlines, body text, and project info for your architecture project.</div>
""", unsafe_allow_html=True)

STYLE_PATH = "data/website_styles.json"
os.makedirs("data", exist_ok=True)

def load_styles():
    try:
        with open(STYLE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_styles(styles):
    with open(STYLE_PATH, "w", encoding="utf-8") as f:
        json.dump(styles, f, ensure_ascii=False, indent=2)

styles = load_styles()
style_names = ["(new style)"] + sorted(styles.keys())

FONT_OPTIONS = [
    "Arial", "Georgia", "Verdana", "Courier New", "Times New Roman",
    "Century", "Century Gothic"
]

with st.sidebar:
    st.header("Text Style Preset")
    chosen_style = st.selectbox("Choose style preset", style_names, index=0, key="chosen_style")
    if chosen_style == "(new style)":
        style_name = st.text_input("Style name", "")

    st.markdown("---")
    st.subheader("Headline Style")
    headline_font = st.selectbox("Headline Font Family", FONT_OPTIONS, index=FONT_OPTIONS.index("Century Gothic") if "Century Gothic" in FONT_OPTIONS else 0, key="headline_font")
    headline_size = st.slider("Headline Font Size", min_value=18, max_value=48, value=32, step=1, key="headline_size")
    headline_color = st.color_picker("Headline Color", value="#222222", key="headline_color")

    st.markdown("---")
    st.subheader("Body Style")
    body_font = st.selectbox("Body Font Family", FONT_OPTIONS, index=FONT_OPTIONS.index("Century Gothic") if "Century Gothic" in FONT_OPTIONS else 0, key="body_font")
    body_size = st.slider("Body Font Size", min_value=12, max_value=32, value=18, step=1, key="body_size")
    body_color = st.color_picker("Body Color", value="#222222", key="body_color")

web_content = st.session_state.get("web", None)
website_img_bytes = st.session_state.get("website_img", None)

if web_content:
    title = web_content.get("title", "")
    # Remove 'Headline:' prefix if present
    if title.lower().startswith('headline:'):
        title = title[len('headline:'):].strip()
    sections = web_content.get("sections", [])
    # Combine all section bodies into one text
    full_body = " ".join([sec.get("body","") for sec in sections]).strip()
    preview_map = {
        "Short Preview": "short",
        "Medium Preview": "medium",
        "Long Preview": "long"
    }
    # Prepare project info for grid
    project = st.session_state.get("active_project", {})
    if not project or not project.get("name"):
        # Fallback: use the most recently saved project from PROJECTS
        try:
            with open("data/projects.json", "r", encoding="utf-8") as f:
                projects = json.load(f)
            if projects:
                # Use the last project in the dict
                last_proj = list(projects.values())[-1]
                project = last_proj
        except Exception:
            project = {}
    name = project.get("name", "")
    client = project.get("client", "")
    location = project.get("location", "")
    ptype = project.get("type", "")
    size = project.get("size_scope", "")
    timeline = project.get("timeline", "")
    phase = project.get("phase", "")
    firms = project.get("architectural_firm", [])
    office_str = ", ".join(firms) if firms else ""

    for label, key in preview_map.items():
        st.markdown(f"### {label}")
        col_img, col_text = st.columns([1,2])
        with col_img:
            if website_img_bytes:
                import base64
                img_data = base64.b64encode(website_img_bytes).decode()
                st.markdown(f"<img src='data:image/png;base64,{img_data}' style='width:100%;max-width:320px;border-radius:16px;box-shadow:0 2px 12px #0002;margin-bottom:1em;'>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='width:100%;height:180px;background:#eee;border-radius:16px;display:flex;align-items:center;justify-content:center;color:#aaa;font-size:1.2em;'>No Image</div>", unsafe_allow_html=True)
        with col_text:
            # Ensure project info fallback is applied for each preview
            project = st.session_state.get("active_project", {})
            if not project or not project.get("name"):
                try:
                    with open("data/projects.json", "r", encoding="utf-8") as f:
                        projects = json.load(f)
                    if projects:
                        last_proj = list(projects.values())[-1]
                        project = last_proj
                except Exception:
                    project = {}
            name = project.get("name", "")
            client = project.get("client", "")
            location = project.get("location", "")
            ptype = project.get("type", "")
            size = project.get("size_scope", "")
            timeline = project.get("timeline", "")
            phase = project.get("phase", "")
            firms = project.get("architectural_firm", [])
            office_str = ", ".join(firms) if firms else ""

            preview_data = web_content.get(key, {})
            headline_text = preview_data.get("title", "")
            # Remove 'Headline:' prefix if present
            if headline_text.lower().startswith('headline:'):
                headline_text = headline_text[len('headline:'):].strip()
            # Remove leading/trailing '**' if present
            if headline_text.startswith('**') and headline_text.endswith('**'):
                headline_text = headline_text[2:-2].strip()
            body_text = ""
            sections = preview_data.get("sections", [])
            if sections and isinstance(sections[0], dict):
                body_text = sections[0].get("body", "")
            preview_html = (
                '<div style="background:#fff;padding:2em;border-radius:12px;box-shadow:0 2px 12px #0002;max-width:800px;margin:left;">'
                + style_headline(headline_text, headline_font, headline_size, headline_color)
                + style_project_info_grid([
                    ("Project", name),
                    ("Client", client),
                    ("Location", location),
                    ("Architectural Office", office_str),
                    ("Type", ptype),
                    ("Size", size),
                    ("Timeline", timeline),
                    ("Phase", phase)
                ])
                + style_body(body_text, body_font, body_size, body_color)
                + '</div>'
            )
            st.markdown(preview_html, unsafe_allow_html=True)
            st.markdown("<div style='height: 1.2em'></div>", unsafe_allow_html=True)

            # --- Working HTML copy button using JS and hidden textarea ---
            st.markdown("Download the HTML code below or copy it manually:")
            st.text_area(f"HTML for {label}", value=preview_html, height=180, key=f"html_area_{label}")
            st.download_button(
                label=f"Download HTML ({label})",
                data=preview_html,
                file_name=f"website_content_{label.replace(' ', '_').lower()}.html",
                mime="text/html"
            )



# If no web_content, show info message
if not web_content:
    st.info("No website content found. Please generate content from the Project Setup page.")