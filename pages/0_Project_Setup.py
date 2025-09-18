import streamlit as st
import json
import os
from dotenv import load_dotenv
import openai

# --- Paths ---
PROJECTS_PATH = "data/projects.json"
STYLES_PATH = "data/styles.json"
os.makedirs("data", exist_ok=True)

# --- Load Data ---
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

PROJECTS = load_json(PROJECTS_PATH)
STYLES = load_json(STYLES_PATH)

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

# --- USPS Presets ---
USPS_PRESETS = {
    "School": ["Flexible classrooms", "Outdoor learning", "STEM labs"],
    "Residential": ["Energy efficient", "Smart home", "Community spaces"],
    "Office": ["Open plan", "Collaboration zones", "Green building"],
    "Mixed-use": ["Retail integration", "Transit access", "Public plaza"],
    "Cultural": ["Exhibition halls", "Performance spaces", "Historic preservation"]
}

# --- OpenAI Setup ---
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Content Generation ---
def generate_text(project, usps, style, img_bytes):
    length_map = {"short": 50, "medium": 120, "long": 250}
    results = {}
    for label, word_count in length_map.items():
        prompt = f"""
You are an expert architecture journalist. Write a news article and headline for the following project{', using the provided image for additional context' if img_bytes else ''}:

Project Name: {project.get('name','')}
Client: {project.get('client','')}
Location: {project.get('location','')}
Type: {project.get('type','')}
Size/Scope: {project.get('size_scope','')}
Timeline: {project.get('timeline','')}
Phase: {project.get('phase','')}
Architectural Firm: {', '.join(project.get('architectural_firm',[]))}
USPs: {', '.join(usps)}

Style:
- Voice: {style.get('voice','neutral')}
- Formality: {style.get('formality','semi-formal')}
- Length: {label} ({word_count} words)
- Structure: {style.get('structure','overview→details')}

Write a headline and a short news article suitable for a website. Headline first, then the article body. The article body should be about {word_count} words long.
"""
        if img_bytes:
            import base64
            img_b64 = base64.b64encode(img_bytes).decode()
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}}
                    ]
                }],
                max_tokens=800,
                temperature=0.7
            )
        else:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
        output = response.choices[0].message.content
        lines = output.strip().splitlines()
        headline = lines[0] if lines else "[No headline generated]"
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else "[No article generated]"
        results[label] = {"title": headline, "sections": [{"body": body}]}
    return results

# --- Project Card ---
st.markdown("""
<h1 style='font-size:2.3em; color:#14532d; margin-bottom:0.5em;'>Project Setup</h1>
<div style='font-size:1.15em; color:#222; margin-bottom:2em;'>Enter and save your project details, USPs, and style profiles for content generation.</div>
""", unsafe_allow_html=True)
st.header("Project Card")
project_names = ["(new project)"] + list(PROJECTS.keys())
selected_project = st.selectbox("Select project", project_names, index=0, key="project_select")
if selected_project == "(new project)":
    proj = {"name": "", "client": "", "location": "", "type": "School", "size_scope": "", "volume": "", "timeline": "", "phase": "", "architectural_firm": []}
else:
    proj = PROJECTS[selected_project]
p_name = st.text_input("Project Name", proj.get("name", ""), key="p_name")
p_client = st.text_input("Client", proj.get("client", ""), key="p_client")
p_loc = st.text_input("Location", proj.get("location", ""), key="p_loc")
p_type = st.selectbox("Type", list(USPS_PRESETS.keys()), index=list(USPS_PRESETS.keys()).index(proj.get("type", "School")), key="p_type")
p_size = st.text_input("Size/Scope", proj.get("size_scope", ""), key="p_size")
p_volume = st.text_input("Volume", proj.get("volume", ""), key="p_volume")
p_time = st.text_input("Timeline", proj.get("timeline", ""), key="p_time")
p_phase = st.text_input("Phase", proj.get("phase", ""), key="p_phase")
firm_options = ["Scherzer Architekten", "Scherzer Architekten Partnerschaft"]
selected_firms = st.multiselect("Architectural Firm", firm_options, default=proj.get("architectural_firm", []), key="firm_select")
if st.button("Save Project Card", key="save_project_btn"):
    if p_name.strip():
        PROJECTS[p_name.strip()] = {
            "name": p_name.strip(),
            "client": p_client.strip(),
            "location": p_loc.strip(),
            "type": p_type,
            "size_scope": p_size.strip(),
            "volume": p_volume.strip(),
            "timeline": p_time.strip(),
            "phase": p_phase.strip(),
            "architectural_firm": selected_firms
        }
        save_json(PROJECTS_PATH, PROJECTS)
        st.session_state["active_project"] = PROJECTS[p_name.strip()]
        st.success("Project saved. Re-select it from the dropdown to use it.")
    else:
        st.error("Project name is required.")

# --- Style Profile ---
st.header("Style profile for website content")
style_names = ["(new style)"] + sorted(STYLES.keys())
chosen_style = st.selectbox("Select style", style_names, index=0, key="style_select")
style_name_input = st.text_input("Style name (for saving or reference)", key="style_name_input")
voices = ["neutral", "enthusiastic", "formal", "conversational"] + st.session_state.get("custom_voices", [])
new_voice = st.text_input("Add custom voice style", key="new_voice_input")
if st.button("Add voice style", key="add_voice_btn"):
    if new_voice and new_voice not in voices:
        voices.append(new_voice)
        st.session_state["custom_voices"] = voices
        st.rerun()
if chosen_style == "(new style)":
    chosen_voice = st.selectbox("Choose text voice", voices, index=0, key="voice_select_new")
    formality = st.selectbox("Formality", ["formal","semi-formal","conversational"], index=1, key="formality_select")
    structure = st.selectbox("Structure", ["overview→details","problem→solution","milestone update"], index=2, key="structure_select")
    if st.button("Save style profile", key="save_style_btn"):
        if style_name_input.strip():
            STYLES[style_name_input.strip()] = {
                "voice": chosen_voice,
                "formality": formality,
                "structure": structure
            }
            save_json(STYLES_PATH, STYLES)
            st.success("Style saved.")
        else:
            st.error("Please enter a style name before saving.")
    style_obj = {
        "voice": chosen_voice,
        "formality": formality,
        "structure": structure
    }
else:
    style_obj = STYLES[chosen_style]
    voice_value = style_obj.get("voice", voices[0])
    if voice_value not in voices:
        voices = [voice_value] + voices
    chosen_voice = st.selectbox("Choose text voice", voices, index=voices.index(voice_value), key="voice_select_existing")
    formality = st.selectbox("Formality", ["formal","semi-formal","conversational"], index=["formal","semi-formal","conversational"].index(style_obj["formality"]), key="formality_select_existing")
    structure = st.selectbox("Structure", ["overview→details","problem→solution","milestone update"], index=["overview→details","problem→solution","milestone update"].index(style_obj["structure"]), key="structure_select_existing")
    if st.button("Update style profile", key="update_style_btn"):
        STYLES[chosen_style] = {
            "voice": chosen_voice,
            "formality": formality,
            "structure": structure
        }
        save_json(STYLES_PATH, STYLES)
        st.success("Style updated.")

st.markdown("<hr style='border: none; border-top: 2px solid #d1d5db; margin: 2em 0;'>", unsafe_allow_html=True)

# --- USPs Section ---
st.header("USPs for website content")
selected_usps = []
default_group = proj.get("type", "School")
for group, items in USPS_PRESETS.items():
    with st.expander(group, expanded=(group == default_group)):
        cols = st.columns(2)
        for i, it in enumerate(items):
            with cols[i % 2]:
                if st.checkbox(it, key=f"usp_{group}_{i}"):
                    selected_usps.append(it)
custom_usps_raw = st.text_input("Custom USPs (comma-separated)")
custom_usps = [x.strip() for x in custom_usps_raw.split(",") if x.strip()]

# --- Saved Custom USPs Tick List ---
saved_custom_usps = set()
for p in PROJECTS.values():
    usps = p.get("custom_usps", [])
    for usp in usps:
        saved_custom_usps.add(usp)
saved_custom_usps = sorted(saved_custom_usps)
if saved_custom_usps:
    st.markdown("**Previously saved custom USPs:**")
    selected_saved_usps = []
    for usp in saved_custom_usps:
        if st.checkbox(usp, key=f"saved_usp_{usp}"):
            selected_saved_usps.append(usp)
    custom_usps += selected_saved_usps
def dedupe(seq):
    s = set()
    out = []
    for x in seq:
        xl = x.lower()
        if xl not in s:
            s.add(xl)
            out.append(x)
    return out
usps_final = dedupe(selected_usps + custom_usps)
if st.button("Save USPs", key="save_usps_btn"):
    if p_name.strip() and p_name.strip() in PROJECTS:
        PROJECTS[p_name.strip()]["custom_usps"] = usps_final
        save_json(PROJECTS_PATH, PROJECTS)
        st.success("USPs saved for this project.")
    else:
        st.warning("Please select or save a project card first.")

st.markdown("<hr style='border: none; border-top: 2px solid #d1d5db; margin: 2em 0;'>", unsafe_allow_html=True)

# --- Image Upload ---
st.header("Image Upload")
uploaded_img = st.file_uploader("Upload project image (photo or rendering)", type=["png", "jpg", "jpeg"])

st.markdown("<hr style='border: none; border-top: 2px solid #d1d5db; margin: 2em 0;'>", unsafe_allow_html=True)

# --- Content Generator ---
st.header("Content Generator")
if st.button("Generate Website Content", key="generate_content_btn"):
    project = PROJECTS.get(p_name.strip())
    if project and project.get("name", "").strip():
        style = style_obj
        usps = usps_final
        img_bytes = uploaded_img.read() if uploaded_img else None
        if img_bytes:
            st.session_state["website_img"] = img_bytes
            try:
                from PIL import Image
                import io
                pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                st.session_state["base_img"] = pil_img
            except Exception:
                st.session_state["base_img"] = None
        if openai.api_key:
            with st.spinner("Generating website content..."):
                try:
                    results = generate_text(project, usps, style, img_bytes)
                    st.session_state["web"] = results
                    st.success("Website content generated! Go to the Website Content page to view it.")
                except Exception as e:
                    st.error(f"Error generating content: {e}")
        else:
            st.warning("OpenAI API key not set. Cannot generate content.")
    else:
        if uploaded_img:
            st.markdown(
                "<div style='background:#fee2e2;color:#b91c1c;border-radius:8px;padding:1em 1.5em;margin:1em 0;font-weight:500;font-size:1.1em;border:1px solid #fca5a5;'>"
                "[Error] You have uploaded an image but no project is selected. Please select a project before generating content."
                "</div>", unsafe_allow_html=True)
        else:
            st.warning("Please select a project before generating content.")



