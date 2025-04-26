import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from crew import load_crew
from utils.output_writer import save_clean_output

# Load environment variables
load_dotenv()

# Avoid torch hot reload overhead and related errors
os.environ["STREAMLIT_WATCHER_IGNORE_MODULES"] = "torch,torch._classes,torch.nn,torch.utils"

# -- CONFIG --------------------------------------------------
st.set_page_config(
    page_title="PromptForge Studio",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "# PromptForge Studio\nEnterprise-Grade Prompt Engineering for the PromptWeaver Agent"
    }
)

# Force dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .stTextInput, .stTextArea, .stSelectbox {
        background-color: #262730;
        color: #FAFAFA;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white !important;
        font-weight: 500;
        text-align: center;
        position: relative;
    }
    .stButton>button:hover {
        background-color: #45a049;
        color: white !important;
    }
    .stButton>button:active, .stButton>button:focus {
        background-color: #3d8b3d;
        color: white !important;
        border-color: #2d672d;
    }
    /* Add a rocket icon to the Generate button */
    .stButton>button:has(div:contains("Generate")) {
        padding-left: 2.5rem;
    }
    .stButton>button:has(div:contains("Generate"))::before {
        content: "🚀";
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
    }
</style>
""", unsafe_allow_html=True)

# -- STATE INIT ----------------------------------------------
if "output" not in st.session_state:
    st.session_state.output = ""

if "input_text" not in st.session_state:
    st.session_state.input_text = ""

# -- UTILS ---------------------------------------------------
def load_preset(preset: str) -> str:
    presets = {
        "SEO Optimizer": "Generate an SEO-optimized prompt for product descriptions...",
        "Academic Paper": "Create a scholarly prompt based on a research question...",
        "Creative Story": "Craft a whimsical story prompt for a fantasy world...",
    }
    return presets.get(preset, "")

def enhance_prompt(text: str) -> str:
    """
    Generate an optimized prompt using the PromptWeaver agent.

    Args:
        text: The raw prompt idea from the user

    Returns:
        The optimized prompt as a string

    Raises:
        ValueError: If the API key is not set or invalid
    """
    # Check if API key is set
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_api_key_here" or api_key == "your_actual_openrouter_api_key_here":
        raise ValueError("OpenRouter API key is not properly configured in the .env file")

    # Load the CrewAI crew
    crew = load_crew()

    # Process the input through the crew
    result = crew.kickoff(inputs={"instruction": text})

    # Convert result to string
    final_prompt = str(result)

    # Save the output to a file
    try:
        save_clean_output(prompt=final_prompt, instruction=text)
    except Exception as e:
        print(f"Warning: Could not save output to file: {e}")
        # Continue even if saving fails - we still want to return the prompt

    return final_prompt

# -- SIDEBAR -------------------------------------------------
with st.sidebar:
    st.image("https://emojicdn.elk.sh/🧠", width=36)
    st.title("PromptForge Studio")
    st.caption("Enterprise-Grade Prompt Engineering for the PromptWeaver Agent")

    preset = st.selectbox(
        "🎛️ Load Prompt Template",
        ["", "SEO Optimizer", "Academic Paper", "Creative Story"],
        index=0,
        help="Start with a ready-made template",
    )

    if preset and not st.session_state.input_text:
        st.session_state.input_text = load_preset(preset)

    if st.checkbox("📘 Show Quick Guide"):
        guide_path = Path("GUIDE.md")
        if guide_path.exists():
            st.markdown(guide_path.read_text())
        else:
            st.info("No guide found. Add a GUIDE.md to your root directory.")

    st.markdown("---")
    st.caption("⚙️ PromptWeaver v1.0.0")

# -- MAIN LAYOUT ---------------------------------------------
st.markdown("## 📝 Enter Raw Prompt Idea")
st.markdown("What would you like to generate a prompt for?")

col1, col2 = st.columns([0.45, 0.55])

with col1:
    input_text = st.text_area("Prompt Input", key="input_text", height=200)

    if st.button("Generate Optimized Prompt", use_container_width=True):
        if not input_text.strip():
            st.warning("Please enter a prompt first.")
        else:
            with st.spinner("🧠 Enhancing prompt with PromptWeaver..."):
                try:
                    # Call the backend to generate the prompt
                    result = enhance_prompt(input_text)
                    st.session_state.output = result
                    st.toast("✅ Prompt enhanced successfully!")
                except Exception as e:
                    error_message = str(e)
                    if "OpenRouter API key is not properly configured" in error_message:
                        st.error("❌ API key not configured. Please add your OpenRouter API key to the .env file.")
                    elif "AuthenticationError" in error_message:
                        st.error("❌ Authentication failed. Please check your OpenRouter API key in the .env file.")
                    elif "No auth credentials found" in error_message:
                        st.error("❌ No API key found. Please add your OpenRouter API key to the .env file.")
                    elif "Invalid argument" in error_message or "Permission denied" in error_message:
                        st.error("❌ File system error. Could not save the output file.")
                    else:
                        st.error(f"❌ Failed to optimize prompt: {e}")

                    # Show detailed error in expandable section for debugging
                    with st.expander("Show detailed error"):
                        st.code(error_message)

                        # Add helpful instructions for fixing API key issues
                        if "API key" in error_message or "auth" in error_message:
                            st.markdown("""
                            ### How to fix:
                            1. Open the `.env` file in the project root
                            2. Replace `your_openrouter_api_key_here` with your actual OpenRouter API key
                            3. Save the file and restart the app

                            If you don't have an OpenRouter API key, you can get one at [openrouter.ai](https://openrouter.ai)
                            """)

with col2:
    if st.session_state.output:
        # Display the output
        st.markdown("### 🎯 Engineered Prompt Output")

        with st.expander("📄 View Prompt (Markdown)", expanded=True):
            st.code(st.session_state.output, language="markdown")

            # Add download button
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
