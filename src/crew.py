# src/crew.py

import os
import sys
import logging
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
import openai  # For fallback mechanism

# --- Setup Logging ---
# Configure basic logging first (will be enhanced if logger module loads)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Handle logger import with fallbacks for different execution contexts ---
try:
    # First try importing the logger module with relative imports
    try:
        from .utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Logger loaded using relative import.")
    except ImportError:
        # Next, try direct import (when running as a script)
        try:
            # Add parent directory to path if needed
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
            
            from src.utils.logger import get_logger
            logger = get_logger(__name__)
            logger.info("Logger loaded using absolute import from parent directory.")
        except ImportError:
            # Finally try local import (when src is in path)
            try:
                from utils.logger import get_logger
                logger = get_logger(__name__)
                logger.info("Logger loaded using direct import.")
            except ImportError:
                logger.warning("Could not import custom logger. Using basic logging configuration.")
                # Already set up basic logging above, so continue
except Exception as e:
    logger.warning(f"Logger import failed: {e}. Using basic logging configuration.")

# --- Load environment variables ---
# Construct the path to the .env file, assuming it's in the parent directory of src/
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)
    logger.info(f"Loaded .env file from: {dotenv_path}")
else:
    logger.warning(f".env file not found at: {dotenv_path}. Relying on environment variables.")


# --- Import Utils & Tools using relative paths within the src package ---
try:
    # Assuming utils/retry.py exists in src/utils/
    from .utils.retry import run_with_retries
    logger.info("Imported run_with_retries from utils.retry.")
except ImportError:
    try:
        # Try direct import if relative import fails
        from utils.retry import run_with_retries
        logger.info("Imported run_with_retries from utils.retry (direct import).")
    except ImportError:
        logger.warning("Could not import run_with_retries from retry. Retries disabled.")
        # Define a dummy function if retry logic is expected but module is missing
        def run_with_retries(func, *args, **kwargs):
            logger.warning("Executing function without retries due to import failure.")
            return func(*args, **kwargs)

try:
    # Assuming tools/docling_tool.py exists in src/tools/
    from .tools.docling_tool import get_docling_tool
    knowledge_source_config = get_docling_tool()
    if knowledge_source_config:
         logger.info("Knowledge source configured successfully via get_docling_tool.")
    else:
         logger.info("get_docling_tool ran but returned no knowledge source config.")
except ImportError:
    try:
        # Try direct import if relative import fails
        from tools.docling_tool import get_docling_tool
        knowledge_source_config = get_docling_tool()
        logger.info("Knowledge source configured successfully via direct import.")
    except ImportError:
        logger.warning("Could not import get_docling_tool from docling_tool. Knowledge source disabled.")
        knowledge_source_config = None
except Exception as e:
    logger.error(f"Failed to load knowledge source via get_docling_tool: {e}", exc_info=True)
    knowledge_source_config = None


# --- Configuration Flags (Read from Environment) ---
# Default to Lean Mode if not specified
USE_LEAN_MODE = os.getenv("USE_LEAN_MODE", "true").lower() == "true"
# Default to including the note if not specified
INCLUDE_LLM_EXEC_NOTE = os.getenv("INCLUDE_LLM_EXEC_NOTE", "true").lower() == "true"
# New configuration flag for CrewAI verbosity (default to false)
CREWAI_VERBOSE = os.getenv("CREWAI_VERBOSE", "false").lower() == "true"
OPERATING_MODE = "Lean" if USE_LEAN_MODE else "Full"
logger.info(f"Crew initializing in **{OPERATING_MODE} Mode** (Verbose: {CREWAI_VERBOSE}).")


# --- LLM Setup with Fallback Mechanism ---
OPENROUTER_MODEL_ID = os.getenv("OPENROUTER_MODEL_ID", "mistralai/mistral-7b-instruct") # Sensible default
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Fallback to OpenAI if available

# Configure OpenAI as fallback if available
has_openai_fallback = bool(OPENAI_API_KEY)
if has_openai_fallback:
    openai.api_key = OPENAI_API_KEY
    logger.info("OpenAI fallback configured with API key.")
else:
    logger.warning("No OpenAI fallback configured. Will rely only on OpenRouter.")

if not OPENROUTER_API_KEY:
    logger.error("CRITICAL: OPENROUTER_API_KEY environment variable not found.")
    if has_openai_fallback:
        logger.info("Will use OpenAI fallback exclusively.")
    else:
        logger.error("No API keys available. Crew execution will fail.")
        # Depending on requirements, you might want to raise an error here:
        # raise EnvironmentError("Missing required API keys")

# Create a fallback function for when OpenRouter fails
def fallback_completion(prompt):
    """Fallback to OpenAI API when OpenRouter fails"""
    try:
        if has_openai_fallback:
            logger.info("Using OpenAI fallback for completion")
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        else:
            # Generate a simple response when no fallback is available
            logger.warning("No fallback LLM available. Generating placeholder response.")
            return f"I'm analyzing your request: '{prompt[:50]}...' but couldn't connect to the language model. Please try again later."
    except Exception as e:
        logger.exception(f"Fallback completion failed: {e}")
        return "Error: Both primary and fallback LLM connections failed. Please check your API keys and network connection."

# Setup the LLM configuration object
try:
    llm = LLM(
        model=f"openrouter/{OPENROUTER_MODEL_ID}",
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        # Add other LLM parameters like temperature if needed:
        temperature=0.7
    )
    logger.info(f"LLM configured for model: openrouter/{OPENROUTER_MODEL_ID}")
except Exception as e:
    logger.exception("Failed to initialize the LLM object!")
    raise RuntimeError(f"LLM initialization failed: {e}") from e


# === AGENTS Definition ===
# Define all agents, some will only be added to the crew in Full mode

# Wrap agent creation in a function to handle possible LLM failures
def create_agent(role, goal, backstory):
    try:
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            allow_delegation=False,
            verbose=CREWAI_VERBOSE,  # Use the environment variable here
            llm=llm
        )
    except Exception as e:
        logger.error(f"Failed to create agent {role}: {e}")
        # Return a simplified agent that will use our fallback mechanism
        return Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            allow_delegation=False,
            verbose=CREWAI_VERBOSE,  # Use the environment variable here
            # If we get here, llm initialization failed, so we won't pass it
        )

try:
    requirements_analyst = create_agent(
        role="Prompt Requirements Analyst",
        goal="Understand the user's request, clarify intent, audience, format, and constraints.",
        backstory="You specialize in breaking down vague or complex requests into clear, actionable specifications for prompt engineering."
    )

    knowledge_researcher = create_agent(
        role="Prompt Engineering Knowledge Specialist",
        goal="Leverage the internal knowledge base to identify best frameworks, techniques, and examples, citing sources used.",
        backstory=(
            "You are trained on all internal prompt engineering references including blueprints, cheatsheets, "
            "and logic guides. You meticulously search for relevant patterns and always cite the source files you use (e.g., from Blueprint.md)."
        )
        # Tools are implicitly handled via crew's knowledge_sources
    )

    prompt_drafter = create_agent(
        role="Creative Prompt Strategist",
        goal="Generate a structured, LLM-optimized draft prompt using best-fit frameworks and research insights.",
        backstory=(
            "You're a highly creative prompt architect with deep expertise in crafting effective prompts using frameworks like PECRA, SCQA, RISEN. "
            "You translate requirements and research into prompts with clarity, logical structure, and reusability focus."
        )
    )

    prompt_architect = create_agent(
        role="LLM Prompt Architect & Finisher",
        goal="Polish and finalize the prompt into a clean, structured, and executable artifact, removing all meta-commentary.",
        backstory=(
            "You specialize in the final editorial pass for prompts, ensuring outputs are immaculate: clean structure, precise language, "
            "perfect markdown formatting, and ready to be consumed directly by LLM APIs or chat UIs without further processing."
        )
    )

    # --- Agents used ONLY in Full Mode ---
    prompt_critic = create_agent(
        role="Prompt Critic",
        goal="Critically evaluate the draft prompt for structure, tone, clarity, and potential ambiguities. Offer actionable improvements.",
        backstory="You identify flaws, logical gaps, unclear language, or framework misalignments in prompt drafts and provide constructive, specific feedback for refinement."
    )

    structure_enforcer = create_agent(
        role="Prompt Structure Validator",
        goal="Check the draft prompt for strict adherence to formatting rules, section naming, and markdown cleanliness.",
        backstory="You are the guardian of prompt structure. You ensure that all prompts strictly match the required markdown formatting, section headers, and contain no forbidden phrases or meta-text."
    )
    logger.info("All agent configurations defined.")

except Exception as e:
    logger.exception("Failed to define one or more agents!")
    raise RuntimeError(f"Agent definition failed: {e}") from e

# === TASKS Definition ===
# Define all tasks, some will only be added to the crew in Full mode

try:
    task_analyze = Task(
        description="Analyze the user's instruction: '{instruction}'. Identify the core objective, target audience/LLM, desired output format, key entities/context, and any implicit constraints or edge cases. Break down complex requests.",
        expected_output=(

            "A structured analysis document clearly outlining:\n"
            "- Core Objective: The primary goal of the prompt.\n"
            "- Target Audience/LLM: Who or what will use the prompt.\n"
            "- Desired Output Format & Style: Key elements required.\n"
            "- Key Information/Background Context: Necessary data points.\n"
            "- Constraints & Edge Cases: Limitations or specific scenarios."
        ),
        agent=requirements_analyst,
        # Human input is provided via crew.kickoff(inputs={'instruction': ...})
    )

    task_research = Task(
        description="Based on the analyzed requirements, research the internal knowledge base to find the most relevant prompt engineering frameworks (e.g., PECRA, SCQA, RISEN), techniques, model-specific advice, and examples. Synthesize these findings and explicitly cite the source documents consulted.",
        expected_output=(

            "A concise summary of relevant knowledge:\n"
            "- Recommended Framework(s): Justification for suitability.\n"
            "- Key Techniques: Applicable methods (e.g., few-shot, chain-of-thought).\n"
            "- Model-Specific Notes: Relevant points from cheatsheets if applicable.\n"
            "- Relevant Constraints/Best Practices: Warnings or guidelines from knowledge base.\n"
            "- Source Files Cited: Explicit list (e.g., 'Consulted: Blueprint.md, Deepseek_Cheatsheet.md')."
        ),
        agent=knowledge_researcher,
        context=[task_analyze] # Depends on the analysis output
    )

    task_draft = Task(
        description="Draft the initial structured prompt using the analysis specification and the research findings (frameworks, techniques). Apply the recommended framework(s). Focus on clarity, logical structure, incorporating requirements, and reusability. Use Markdown formatting.",
        expected_output=(

            "A well-structured draft prompt in Markdown format, including preliminary sections based on requirements and research:\n"
            "- Title (Clear, Title Case)\n"
            "- ## Objective\n"
            "- ## Context / Persona (if applicable)\n"
            "- ## Workflow Steps / Instructions\n"
            "- ## Constraints / Rules\n"
            "- ## Validation Criteria (if applicable)\n"
            "- ## Examples (if applicable)"
        ),
        agent=prompt_drafter,
        context=[task_analyze, task_research] # Depends on analysis and research
    )

    # --- Tasks used ONLY in Full Mode ---
    task_critique = Task(
        description="Critically review the draft prompt provided by the drafter. Compare it against the original requirements and knowledge base best practices. Identify areas for improvement regarding logic, clarity, completeness, effectiveness, framework fidelity, and tone. Provide specific, actionable suggestions.",
        expected_output=(

            "A bullet-point critique listing specific weaknesses found in the draft and concrete suggestions for improvement.\n"
            "Example Format:\n"
            "- Issue: Workflow step 3 is ambiguous.\n  Suggestion: Reword to specify the exact input expected.\n"
            "- Issue: Persona definition lacks detail.\n  Suggestion: Add 2-3 more sentences describing motivations based on Context section."
        ),
        agent=prompt_critic,
        context=[task_draft, task_analyze, task_research] # Needs draft and original requirements/research for comparison
    )

    task_validate = Task(
        description="Validate the structure and formatting of the draft prompt against predefined rules. Check for required sections (Objective, Context, etc. if applicable), correct Markdown usage (headers, lists, code blocks), adherence to naming conventions, and absence of forbidden meta-text (like 'Feedback:', 'Notes:').",
        expected_output=(

            "A concise structure validation report:\n"
            "- Overall Status: Pass / Fail\n"
            "- Missing Sections: [List of missing required sections, or 'None']\n"
            "- Formatting Issues: [Description of any Markdown errors, or 'None']\n"
            "- Meta-Text Found: [Details of forbidden text, or 'None']"
        ),
        agent=structure_enforcer,
        context=[task_draft] # Primarily checks the draft's structure
    )

    # --- Final Task Definition (Context depends on mode) ---
    # Define the context list dynamically based on the operating mode
    finalize_context_tasks = [task_draft] + (
        [task_critique, task_validate] if not USE_LEAN_MODE else []
    )

    # Define the optional final note string
    final_llm_instruction_note = (
        "\n\n**Instruction to LLM: Execute this prompt directly. No clarification needed.**"
        if INCLUDE_LLM_EXEC_NOTE else ""
    )

    task_finalize = Task(
        description=(
            "Synthesize the draft prompt and incorporate feedback/validation results (from critique and structure validation tasks, if available) to create the final, polished, execution-ready prompt. "
            "Ensure perfect Markdown formatting, logical structure, absolute clarity, and adherence to all requirements. "
            "Crucially, remove ALL meta-commentary, critique summaries, validation reports, scores, or any text not part of the final prompt itself. "
            f"Append the following directive ONLY if configured: '{final_llm_instruction_note.strip()}'"
        ),
        expected_output=(

             "The final, clean, professional, execution-ready prompt in Markdown format. It must contain ONLY the prompt content, perfectly structured and free of any internal notes, commentary, or artifacts from the generation process."
        ),
        agent=prompt_architect,
        context=finalize_context_tasks # Use the dynamically defined context list
    )
    logger.info("All task configurations defined.")

except Exception as e:
    logger.exception("Failed to define one or more tasks!")
    raise RuntimeError(f"Task definition failed: {e}") from e


# === Assemble Crew based on Mode ===
# Initialize lists
agents_list = [requirements_analyst, knowledge_researcher, prompt_drafter, prompt_architect]
tasks_list = [task_analyze, task_research, task_draft] # Core sequence

# Add full mode agents and tasks if not in lean mode
if not USE_LEAN_MODE:
    # Insert agents in the logical processing order
    agents_list.insert(3, prompt_critic)      # Critic reviews draft
    agents_list.insert(4, structure_enforcer) # Validator checks draft structure
    # Append tasks in the logical processing order
    tasks_list.append(task_critique)          # Critique happens after draft
    tasks_list.append(task_validate)          # Validation happens after draft (or critique)
    logger.info("Added Critic and Validator agents/tasks for Full Mode.")

# Add the final task which depends on the mode's context
tasks_list.append(task_finalize)

# Add a planning flag to the Crew configuration
PLANNING_ENABLED = os.getenv("PLANNING_ENABLED", "false").lower() == "true"
PLANNING_LLM = os.getenv("PLANNING_LLM", "gpt-3.5-turbo")

# Update the Crew instance to include the planning flag if enabled
try:
    prompt_engineering_crew = Crew(
        agents=agents_list,
        tasks=tasks_list,
        knowledge_sources=[knowledge_source_config] if knowledge_source_config else [],
        process=Process.sequential,  # Ensures tasks run in the defined list order
        verbose=CREWAI_VERBOSE,  # Use the environment variable here
        planning=True,  # Add planning flag
        # planning_llm=PLANNING_LLM if PLANNING_ENABLED else None  # Specify the planning LLM if planning is enabled
        # memory=True # Uncomment if long-term memory across tasks is needed
    )
    logger.info(f"Prompt Engineering Crew assembled successfully for {OPERATING_MODE} Mode (Verbose: {CREWAI_VERBOSE}, Planning: {PLANNING_ENABLED}).")
    if CREWAI_VERBOSE:
        logger.debug(f"Agents in crew: {[agent.role for agent in agents_list]}")
        logger.debug(f"Tasks in crew: {[task.description[:50]+'...' for task in tasks_list]}")

except Exception as e:
    logger.exception("CRITICAL: Failed to assemble the CrewAI crew object!")
    raise RuntimeError(f"Crew object assembly failed: {e}") from e


# === Main Execution Function ===
def run_prompt_weaver_crew(instruction: str) -> str:
    """
    Runs the configured Prompt Weaver Crew for the given instruction.
    This function is designed to be called by other modules (API, CLI, UI).

    Args:
        instruction (str): The raw user instruction or prompt idea.

    Returns:
        str: The finalized, optimized prompt string, or an error message string.
    """
    if not OPENROUTER_API_KEY and not has_openai_fallback:
        logger.error("Execution stopped: No API keys configured.")
        # Return an error string instead of raising exception here,
        # allowing calling functions (API, UI) to handle it gracefully.
        return "Error: Service configuration error - API keys not set."

    logger.info(f"🚀 Initiating Prompt Weaver Crew ({OPERATING_MODE} Mode)...")
    logger.info(f"🔹 Input Instruction: {instruction[:150]}...") # Log more context

    try:
        # Encapsulate the kickoff call with retry logic
        kickoff_inputs = {"instruction": instruction}
        try:
            # Assuming run_with_retries is available (imported or dummy function)
            result = run_with_retries(
                prompt_engineering_crew.kickoff,
                inputs=kickoff_inputs
            )
            logger.info(f"✅ Crew execution completed for instruction: {instruction[:150]}...")
        except ValueError as e:
            if "Invalid response from LLM call - None or empty" in str(e):
                logger.warning("Detected empty LLM response error. Switching to fallback prompt generation.")
                # Generate a simplified but structured prompt using the fallback mechanism
                prompt_template = f"""
# Analysis of: {instruction}

## Objective
Provide a comprehensive overview of {instruction}, focusing on key aspects, impacts, and future directions.

## Context
The user wants information about {instruction} with balanced coverage of benefits, challenges, and practical applications.

## Key Areas to Cover
- Current state and development of {instruction}
- Major benefits and advantages
- Challenges, limitations, and ethical considerations
- Real-world applications and case studies
- Future trends and potential developments

## Constraints
- Maintain objectivity and balance
- Include evidence-based information
- Consider multiple perspectives

**Instruction to LLM: Execute this prompt directly. No clarification needed.**
"""
                return prompt_template
            else:
                # Re-raise if it's not the specific error we're handling
                raise

        # --- Result Processing ---
        if isinstance(result, str):
            # Basic check for common error patterns in the result string
            if result.strip().startswith("Error:") or "Traceback (most recent call last)" in result:
                 logger.error(f"Crew kickoff returned an error string indicator: {result[:500]}") # Log more of the error
                 # Generate simplified prompt as fallback
                 logger.warning("Generating simplified fallback prompt due to execution error.")
                 return generate_fallback_prompt(instruction)
            # Success case - return the clean prompt
            return result.strip()
        elif result is None:
             logger.error("Crew kickoff returned None. This indicates a potential issue.")
             return generate_fallback_prompt(instruction)
        else:
            # Handle unexpected result types (e.g., lists, dicts if crew changes)
            logger.warning(f"Crew kickoff returned unexpected type {type(result)}. Attempting string conversion.")
            try:
                return str(result)
            except Exception as str_e:
                 logger.error(f"Failed to convert crew result of type {type(result)} to string: {str_e}")
                 return generate_fallback_prompt(instruction)

    except EnvironmentError as env_err: # Catch specific env errors if raised by crew/logic
         logger.error(f"Environment error during crew execution: {env_err}", exc_info=True)
         return f"Error: Configuration Error - {env_err}"
    except Exception as e:
        # Catch any other unexpected exception during kickoff
        logger.exception(f"CRITICAL: Unhandled exception during crew kickoff for instruction: {instruction[:150]}...")
        return generate_fallback_prompt(instruction)

def generate_fallback_prompt(instruction: str) -> str:
    """Generate a simple but structured prompt when the regular flow fails."""
    logger.info(f"Generating fallback prompt for: {instruction[:50]}...")
    
    try:
        # Try to use our fallback_completion function
        prompt_for_fallback = f"""
        You are a professional prompt engineer. Create a structured prompt for the topic: "{instruction}"

        The prompt should include:
        1. A clear title
        2. An objective section
        3. Context/background
        4. Key instructions or steps
        5. Constraints or requirements
        6. Any relevant examples

        Format the response in clean Markdown with appropriate sections.
        """
        
        return fallback_completion(prompt_for_fallback)
    except Exception as e:
        logger.exception(f"Fallback prompt generation failed: {e}")
        # Ultimate fallback - hardcoded template
        return f"""
# {instruction.title()} Analysis Prompt

## Objective
Provide a comprehensive analysis of {instruction} with key insights and implications.

## Context
This is a structured exploration of {instruction}, covering multiple dimensions and perspectives.

## Key Areas to Explore
- Definition and overview
- Current landscape and trends
- Benefits and opportunities
- Challenges and limitations
- Future outlook

## Format
Ensure the response is well-structured, evidence-based, and includes practical implications.

**Instruction to LLM: Execute this prompt directly. No clarification needed.**
"""

# === Optional: Direct CLI Execution Block for Testing ===
# This block runs only when crew.py is executed directly (e.g., python src/crew.py)
if __name__ == "__main__":
    logger.info(f"Running {__file__} directly for testing purposes...")
    print("-" * 30)
    print(f"** Direct Crew Test ({OPERATING_MODE} Mode) **")
    print("-" * 30)
    try:
        user_input_test = input("Enter a test instruction:\n> ").strip()
        if user_input_test:
            test_output = run_prompt_weaver_crew(user_input_test)
            print("\n" + "=" * 15 + " TEST OUTPUT " + "=" * 15)
            print(test_output)
            print("=" * 45)
        else:
            print("No test input provided.")
    except Exception as test_e:
         print(f"\n❌ Error during direct test execution: {test_e}")
    print("Direct test finished.")