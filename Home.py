# Instagram Content Generator
# Author: [Jannes Scherzer]
# Date: 2025-09-18
# This script generates website/social mediacontent for architecture projects using OpenAI.




import streamlit as st

st.set_page_config(page_title="ArchiNewsCreator", page_icon="📰", layout="wide")

# Hide sidebar and hamburger menu on Home page
st.markdown("""
<style>
[data-testid="stSidebar"], [data-testid="stSidebarNav"], [data-testid="stSidebarNavItems"], [data-testid="stSidebarUserContent"], [data-testid="stSidebarCollapseControl"] {
    display: none !important;
}
header [data-testid="stHeader"] { z-index: 1; }
</style>
""", unsafe_allow_html=True)

# App headline in a green box with more shadow
st.markdown(
    """
    <div style='background: linear-gradient(90deg, #e0fbe0 0%, #f3f4f6 100%); border-radius: 18px; padding: 2.5em 2em 2em 2em; margin-bottom: 2em; box-shadow: 0 8px 32px 0 rgba(22,163,74,0.18), 0 2px 16px 0 #0002;'>
        <h1 style='font-size: 2.5em; color: #14532d; margin-bottom: 0.5em;'>ArchiNewsCreator</h1>
        <div style='margin-bottom: 1.5em;'>
            <span style='font-size: 1.2em; color: #14532d; font-weight: bold;'>An AI-powered content generator for architecture firms — from websites to social media.</span><br>
            <span style='display: block; font-size: 1.1em; color: #14532d; margin-top: 0.5em; font-style: italic;'>Turn projects into posts – effortlessly.</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# Links to all 4 subpages
st.markdown("<h3 style='color: #14532d; margin-top: 2em;'>Tools</h3>", unsafe_allow_html=True)
st.page_link("pages/0_Project_Setup.py", label="🗂️ Project Setup")
st.page_link("pages/1_Image_Scaler.py", label="🖼️ Image Scaler")
st.page_link("pages/2_Website_Content.py", label="🌐 Website Content")
st.page_link("pages/3_Instagram_Content.py", label="📸 Instagram Content")

# How it works block
st.markdown(
    """
    <div style='margin-top: 2em; background: #f3f4f6; border-radius: 12px; padding: 1.5em 1.2em; box-shadow: 0 2px 8px #0001;'>
        <div style='font-size: 1.2em; font-weight: bold; color: #14532d; margin-bottom: 0.5em;'>How it works</div>
        <ol style='font-size: 1.05em; color: #222; padding-left: 1.2em;'>
            <li><b>Set up your project</b> - Enter project details and select USPs.</li>
            <li><b>Choose your style</b> - Pick or create a style profile for your content.</li>
            <li><b>Upload an image</b> (optional) - Add a rendering or photo to inform the AI.</li>
            <li><b>Generate content</b> - Click the green button to create professional news copy.</li>
            <li><b>Copy & use</b> - Review, copy, and use the generated content for your website or social media.</li>
        </ol>
        <div style='margin-top: 1.2em; color: #16a34a; font-size: 1em;'>
            <b>Tip:</b> Use the sidebar to navigate between tools!
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

