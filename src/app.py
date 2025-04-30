# src/app.py

import os
import sys
import logging
import streamlit as st
from dotenv import load_dotenv

# --- Configure basic logging first ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("root")

# --- Ensure the parent directory is in the path for absolute imports ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# --- Now try direct absolute imports (most reliable for Streamlit) ---
try:
    # Import logger first
    from src.utils.logger import get_logger

    logger = get_logger("streamlit_app")
    logger.info("Logger loaded successfully for Streamlit.")

    # Then import other modules
    from src.crew import run_prompt_weaver_crew, OPERATING_MODE, USE_LEAN_MODE
    from src.utils.output_writer import save_clean_output

    logger.info("Streamlit App imports successful using absolute imports.")
except ImportError as e:
    logger.error(
        f"CRITICAL Import Error: Failed to load core components: {e}. Application cannot start."
    )
    st.error(f"Failed to load core components: {e}. Application cannot start.")
    st.stop()
except Exception as e:
    logger.error(f"Unexpected error during import: {e}")
    st.error(f"An unexpected error occurred: {e}")
    st.stop()

# --- Load environment variables ---
dotenv_path = os.path.join(parent_dir, ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(f"Loaded .env file from: {dotenv_path}")
else:
    logger.warning(
        f".env file not found at: {dotenv_path}. Relying on environment variables."
    )

# -- PRESET DEFINITIONS --------------------------------------
PRESETS = {
    "Breakthrough Business Idea": "Create a unique online business concept that requires zero upfront investment, leverages existing platforms, and has potential to scale to 7-figures. Include target audience, revenue model, and first 30-day action plan.",
    "Passive Income Generator": "Design a scalable online business that can generate $5,000/month in passive income within 12 months. Focus on minimal maintenance, automation, and leveraging digital assets or platforms.",
    "AI-Powered Startup": "Develop a business concept that uses AI tools to solve a meaningful problem for a specific industry. Include monetization strategy, competitive advantage, and why now is the perfect timing for this solution.",
    "Micro-SaaS Opportunity": "Create a highly focused SaaS concept targeting a specific business pain point. Outline the solution, target market, pricing strategy, and how to build a minimum viable product with limited resources.",
    "Bootstrapped Empire": "Design a business that can start with under $1,000 investment and scale to $1M+ annual revenue. Focus on high-margin digital products, viral growth mechanisms, and strategic partnerships.",
    "Product Manager - Feature Pitch": "Create a compelling one-pager to pitch a new feature that drives user engagement. Include problem statement, proposed solution, success metrics, implementation timeline, and ROI projection.",
    "Developer - API Documentation": "Generate comprehensive API documentation for a microservice. Include authentication methods, endpoints with request/response examples, error handling, rate limits, and integration best practices.",
    "Newsletter Growth Strategy": "Develop a comprehensive plan to grow an email newsletter from 100 to 10,000 engaged subscribers in 6 months. Include content strategy, growth tactics, monetization options, and automation workflows.",
    "QA Test Suite Creator": "Create detailed test cases for a critical user flow in a web/mobile application. Include happy paths, edge cases, security considerations, and performance testing scenarios.",
    "Personal Brand Builder": "Design a 90-day strategy to establish yourself as a thought leader in your industry. Include content pillars, platform strategy, networking tactics, and visibility milestones.",
    "Digital Product Launch": "Create a step-by-step launch strategy for a digital product (course, ebook, template, etc.) that maximizes initial sales and builds long-term momentum. Include pre-launch, launch day, and post-launch phases.",
    "Niche Marketplace Concept": "Develop a concept for a specialized marketplace connecting buyers and sellers in an underserved niche. Include platform features, monetization model, and critical mass acquisition strategy.",
    "Content Creator Expansion": "Design a strategy to expand a successful social media presence on one platform into a multi-channel brand with diverse revenue streams. Include content repurposing, audience migration, and monetization diversification.",
    "B2B Service Positioning": "Create positioning for a B2B service that commands premium pricing. Include unique value proposition, ideal client profile, competitive differentiation, and sales messaging framework.",
    "Community-Based Business": "Design a business model built around a passionate community. Include community structure, value exchange, monetization approach, and growth strategy that preserves culture.",
}


def load_preset(preset: str) -> str:
    return PRESETS.get(preset, "")


# -- MODE DEFINITIONS ---------------------------------------
OPERATING_MODES = {
    "Speed Mode": {
        "description": "Faster generation with 4 agents (Analysis, Research, Draft, Final)",
        "value": "true",
    },
    "Quality Mode": {
        "description": "Comprehensive generation with 6 agents including Critic and Validator",
        "value": "false",
    },
}

# Get the current mode (from .env or environment)
initial_mode = "Speed Mode" if USE_LEAN_MODE else "Quality Mode"


# Function to update the operating mode
def update_operating_mode(mode_name):
    mode_value = OPERATING_MODES[mode_name]["value"]
    # Get the .env file path
    env_file = os.path.join(parent_dir, ".env")

    if os.path.exists(env_file):
        # Read the existing .env file
        with open(env_file, "r") as file:
            lines = file.readlines()

        # Update the USE_LEAN_MODE line
        updated = False
        for i, line in enumerate(lines):
            if line.strip().startswith("USE_LEAN_MODE="):
                lines[i] = f'USE_LEAN_MODE="{mode_value}"\n'
                updated = True
                break

        # If the line doesn't exist, add it
        if not updated:
            lines.append(f'USE_LEAN_MODE="{mode_value}"\n')

        # Write the updated content back to the .env file
        with open(env_file, "w") as file:
            file.writelines(lines)

        logger.info(
            f"Updated operating mode to {mode_name} (USE_LEAN_MODE={mode_value})"
        )
        return True
    else:
        logger.warning("Could not update operating mode: .env file not found")
        return False


# -- STREAMLIT CONFIG (via .streamlit/config.toml) -----------
# st.set_page_config call is still needed for title, icon, layout
st.set_page_config(
    page_title="PromptWeaver Studio",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "# PromptWeaver Studio\nEnterprise-Grade Prompt Engineering for the PromptWeaver Agent"
    },
)

# -- CUSTOM STYLING ------------------------------------------
# This CSS targets various Streamlit components and general page elements
st.markdown(
    """
<style>
    /* Basic styling for the app - simplified version */
    .stApp {
        background-color: #1E2130;
        color: #FFFFFF;
    }
    h1, h2, h3 {
        color: #4CAF50;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
    }
    /* Fix for button text disappearing on hover */
    .stButton>button:hover {
        background-color: #3d8c40; /* Slightly darker green for hover effect */
        color: white; /* Ensure text remains white on hover */
    }
</style>
""",
    unsafe_allow_html=True,
)

# -- SESSION STATE INIT --------------------------------------
if "output" not in st.session_state:
    st.session_state.output = ""
if "input_text" not in st.session_state:
    st.session_state.input_text = ""
if "processing" not in st.session_state:
    st.session_state.processing = False
if "current_mode" not in st.session_state:
    st.session_state.current_mode = initial_mode
if "restart_required" not in st.session_state:
    st.session_state.restart_required = False


# Function to check if a restart is needed based on the current env settings
def check_restart_needed():
    current_mode_value = OPERATING_MODES[st.session_state.current_mode]["value"]
    current_env_value = "true" if USE_LEAN_MODE else "false"
    # If the session state mode doesn't match the actual env value, restart is needed
    return current_mode_value != current_env_value


# Reset restart flag if it matches current env settings
if st.session_state.restart_required and not check_restart_needed():
    st.session_state.restart_required = False


# -- BACKEND CALL FUNCTION -----------------------------------
def call_crew_backend(user_input):
    """Calls the crew backend and handles output saving."""
    logger.info(f"Streamlit calling crew backend for: '{user_input[:100]}...'")

    try:
        # Call the imported function
        final_prompt = run_prompt_weaver_crew(user_input)
        logger.info(f"Crew backend call completed. Output: {final_prompt[:100]}...")

        # Save output (handle potential errors)
        try:
            # Define output directory relative to project root
            output_dir = os.path.join(parent_dir, "output")
            os.makedirs(output_dir, exist_ok=True)
            save_clean_output(
                prompt=final_prompt, instruction=user_input, output_dir=output_dir
            )
            logger.info("Streamlit saved output successfully.")
        except Exception as e:
            logger.error(f"Streamlit failed to save output: {e}")
            st.warning(f"Note: Could not save output file due to error: {e}")

        return final_prompt
    except Exception as e:
        logger.exception(f"Error in call_crew_backend: {e}")
        return f"Error: {str(e)}"


# -- SIDEBAR -------------------------------------------------
with st.sidebar:
    st.image("https://emojicdn.elk.sh/🧠", width=50)
    st.markdown("## PromptWeaver Studio")
    st.caption("Enterprise-Grade Prompt Engineering")

    st.markdown("---")

    st.markdown("### 🎯 Starting Point")

    # Add a state variable for tracking if preset selection dialog is open
    if "preset_dialog_open" not in st.session_state:
        st.session_state.preset_dialog_open = False

    # Add a state variable to store the pending preset selection
    if "pending_preset" not in st.session_state:
        st.session_state.pending_preset = None

    # Function to handle preset selection
    def on_preset_select():
        if st.session_state.preset_selector != "":
            st.session_state.preset_dialog_open = True
            st.session_state.pending_preset = st.session_state.preset_selector

    preset = st.selectbox(
        "Choose a Real-World Idea",
        [""] + list(PRESETS.keys()),
        index=0,
        key="preset_selector",
        on_change=on_preset_select,
        help="Select a realistic query to jumpstart prompt generation.",
        label_visibility="collapsed",
    )

    # Show confirmation dialog when preset is selected
    if st.session_state.preset_dialog_open:
        # Create a container for the modal-like dialog
        dialog_container = st.container()
        with dialog_container:
            st.warning(f"Apply template: **{st.session_state.pending_preset}**?")
            st.caption("This will replace your current input text.")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Apply", key="confirm_preset", use_container_width=True):
                    # Apply the preset
                    st.session_state.input_text = load_preset(st.session_state.pending_preset)
                    st.session_state.preset_dialog_open = False
                    st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_preset", use_container_width=True):
                    # Reset the selection
                    st.session_state.preset_selector = ""
                    st.session_state.preset_dialog_open = False
                    st.session_state.pending_preset = None
                    st.rerun()

    st.markdown("---")
    st.markdown("### ⚙️ Agent Configuration")

    # Operating mode dropdown with better names
    selected_mode = st.selectbox(
        "Operating Mode",
        list(OPERATING_MODES.keys()),
        index=list(OPERATING_MODES.keys()).index(st.session_state.current_mode),
        help="Select how you want the agents to operate",
    )

    # Show description of the selected mode
    st.caption(f"{OPERATING_MODES[selected_mode]['description']}")

    # If mode changed, update .env file and set flag for restart
    if selected_mode != st.session_state.current_mode:
        if update_operating_mode(selected_mode):
            st.session_state.current_mode = selected_mode
            st.session_state.restart_required = True

    # Advanced options expander
    with st.expander("Advanced Options"):
        st.caption("These settings are controlled via the .env file")
        st.code(
            f"USE_LEAN_MODE={OPERATING_MODES[st.session_state.current_mode]['value']}"
        )
        st.caption("Current agent status:")
        current_env_value = "true" if USE_LEAN_MODE else "false"
        expected_env_value = OPERATING_MODES[st.session_state.current_mode]["value"]

        if current_env_value == expected_env_value:
            # Display actual running agents based on current env settings
            if USE_LEAN_MODE:
                st.info("Running: Analysis, Research, Draft, Final")
            else:
                st.info("Running: Analysis, Research, Draft, Critic, Validator, Final")
        else:
            # Show what will run after restart
            if expected_env_value == "true":
                st.warning("After restart will run: Analysis, Research, Draft, Final")
            else:
                st.warning(
                    "After restart will run: Analysis, Research, Draft, Critic, Validator, Final"
                )

    # Show restart message only if needed
    if st.session_state.restart_required:
        st.warning("⚠️ Mode changed - restart needed to apply changes")
        if st.button(
            "🔄 Reload App to Apply Changes",
            key="restart_button",
            use_container_width=True,
        ):
            # Force a full browser page refresh (more reliable than st.rerun())
            st.markdown(
                """
                <script>
                    window.parent.location.reload()
                </script>
                """,
                unsafe_allow_html=True,
            )
            # As a fallback if the script doesn't work
            st.rerun()

    st.markdown("---")
    st.markdown("### About")
    st.info(
        "PromptWeaver Studio leverages a multi-agent system built with CrewAI to generate highly structured and optimized prompts from your raw ideas."
    )

# -- MAIN LAYOUT ---------------------------------------------
st.markdown("## 📝 Enter Your Raw Prompt Idea")

# Input area
input_text = st.text_area(
    "Your Instruction / Idea:",
    key="input_text",
    height=200,
    placeholder="e.g., Create a marketing plan for a new SaaS product...",
)

# Generate button
if st.button(
    "🚀 Generate Optimized Prompt",
    use_container_width=True,
    type="primary",
    disabled=st.session_state.processing,
):
    if not input_text.strip():
        st.warning("🅿️ Please enter a prompt idea first.")
    else:
        # Set processing state and trigger generation
        st.session_state.processing = True
        st.rerun()

# Handle the processing and output
st.markdown("### ✨ Engineered Prompt Output")

# Process the generation if we're in processing state
if st.session_state.processing:
    with st.spinner("🧠 PromptWeaver crew is thinking..."):
        # Actually call the backend here
        result = call_crew_backend(st.session_state.input_text)
        # Store the result in session state
        st.session_state.output = result
        # Clear the processing flag
        st.session_state.processing = False
        # Success message
        if not result.startswith("Error:"):
            st.success("✅ Prompt generated successfully!")
        st.rerun()  # Rerun to update the UI with the output

# Display output if available
if st.session_state.output:
    if st.session_state.output.startswith("Error:"):
        st.error(st.session_state.output)
    else:
        st.markdown(st.session_state.output)

        st.divider()

        # Download button
        st.download_button(
            label="⬇️ Download as Markdown",
            data=st.session_state.output,
            file_name="optimized_prompt.md",
            mime="text/markdown",
        )

        # View raw markdown
        with st.expander("View Raw Markdown", expanded=False):
            st.code(st.session_state.output, language="markdown")
else:
    st.info("Output will appear here after generation.")

# -- FOOTER --------------------------------------------------
st.markdown("---")
st.caption("PromptWeaver Studio | Enterprise Prompt Engineering Platform | Powered by CrewAI")
