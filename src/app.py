import os
import streamlit as st
from dotenv import load_dotenv
from pathlib import Path

from crew import run_prompt_weaver_crew
from utils.output_writer import save_clean_output

# -- PRESET DEFINITIONS --------------------------------------
PRESETS = {
    "Startup Ideation": "Come up with a unique business idea that's easy to start online, requires no upfront investment, and can scale to millions.",
    
    "Product Manager - Feature Pitch": "Help me write a compelling one-pager to pitch a new feature for our mobile app to company executives.",
    
    "Developer - Technical Documentation": "Create clean, easy-to-follow API documentation for a backend microservice built with FastAPI.",
    
    "Newsletter Growth Hack": "How can I grow my email newsletter from 100 to 10,000 subscribers quickly and sustainably?",
    
    "QA Engineer - Test Case Generation": "Write detailed test cases for a user login and password reset flow in a responsive web application."
}

def load_preset(preset: str) -> str:
    return PRESETS.get(preset, "")

# -- PRELOAD SETTINGS ----------------------------------------
os.environ["STREAMLIT_WATCHER_IGNORE_MODULES"] = "torch,torch._classes,torch.nn,torch.utils,torch._C"
load_dotenv()

# -- STREAMLIT CONFIG ----------------------------------------
st.set_page_config(
    page_title="PromptForge Studio",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# PromptForge Studio\nEnterprise-Grade Prompt Engineering for the PromptWeaver Agent"
    }
)

# -- CUSTOM STYLING ------------------------------------------
st.markdown("""
<style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    .stTextInput, .stTextArea, .stSelectbox { background-color: #262730; color: #FAFAFA; }
    .stButton>button { background-color: #4CAF50; color: white !important; font-weight: 500; }
    .stButton>button:hover { background-color: #45a049; }
    .stButton>button:active, .stButton>button:focus { background-color: #3d8b3d; }
</style>
""", unsafe_allow_html=True)

# -- SESSION STATE INIT --------------------------------------
if "output" not in st.session_state:
    st.session_state.output = ""

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# -- BACKEND CALL FUNCTION -----------------------------------
def enhance_prompt(user_input):
    final_prompt = run_prompt_weaver_crew(user_input)
    save_clean_output(prompt=final_prompt, instruction=user_input)
    return final_prompt

# -- SIDEBAR -------------------------------------------------
with st.sidebar:
    st.image("https://emojicdn.elk.sh/🧠", width=36)
    st.title("PromptForge Studio")
    st.caption("Enterprise-Grade Prompt Engineering for the PromptWeaver Agent")

    preset = st.selectbox(
        "🎯 Choose a Real-World Starting Point",
        [""] + list(PRESETS.keys()),
        index=0,
        help="Select a realistic query to jumpstart prompt generation."
    )

    if preset and not st.session_state.input_text:
        st.session_state.input_text = load_preset(preset)

    st.markdown("---")
    st.caption("⚙️ PromptWeaver v1.0.0")

# -- MAIN LAYOUT ---------------------------------------------
st.markdown("## 📝 Enter Your Raw Prompt Idea")

col1, col2 = st.columns([0.45, 0.55])

with col1:
    input_text = st.text_area("Prompt Input", key="input_text", height=200)

    if st.button("🚀 Generate Optimized Prompt", use_container_width=True):
        if not input_text.strip():
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner("🧠 Enhancing prompt with PromptWeaver..."):
                try:
                    result = enhance_prompt(input_text)
                    st.session_state.output = result
                    st.toast("✅ Prompt enhanced successfully!")
                except Exception as e:
                    error_message = str(e)
                    st.error(f"❌ Error: {error_message}")

with col2:
    if st.session_state.output:
        st.markdown("### 🎯 Engineered Prompt Output")

        with st.expander("📄 View Prompt (Markdown)", expanded=True):
            st.code(st.session_state.output, language="markdown")

            st.download_button(
                label="⬇️ Download .md",
                data=st.session_state.output,
                file_name="optimized_prompt.md",
                mime="text/markdown",
                use_container_width=True
            )

# -- FOOTER --------------------------------------------------
st.markdown("---")
st.caption("🚀 PromptForge Studio · Crafted with 💡 by PromptWeaver Agent")
