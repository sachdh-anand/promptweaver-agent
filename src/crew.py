import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM
from utils.retry import run_with_retries

# --- Optional Config Flags ---
USE_LEAN_MODE = os.getenv("USE_LEAN_MODE", "true").lower() == "true"
INCLUDE_LLM_EXEC_NOTE = os.getenv("INCLUDE_LLM_EXEC_NOTE", "true").lower() == "true"

# --- Load environment variables ---
load_dotenv()

# --- Load Knowledge Source ---
try:
    from tools.docling_tool import get_docling_tool
    knowledge_source_config = get_docling_tool()
except Exception as e:
    print(f"[WARN] Failed to load knowledge source: {e}")
    knowledge_source_config = None

# --- LLM Setup ---
llm = LLM(
    model=f"openrouter/{os.getenv('OPENROUTER_MODEL_ID')}",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)

# === AGENTS ===

requirements_analyst = Agent(
    role="Prompt Requirements Analyst",
    goal="Understand the user's request, clarify intent, audience, format, and constraints.",
    backstory="You specialize in breaking down vague or complex requests into clear specifications.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

knowledge_researcher = Agent(
    role="Prompt Engineering Knowledge Specialist",
    goal="Leverage the internal knowledge base to identify best frameworks and cite sources.",
    backstory=(
        "You are trained on all internal prompt engineering references including blueprints, cheatsheets, "
        "and logic guides. You always cite the source files you use (e.g. Blueprint.md)."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

prompt_drafter = Agent(
    role="Creative Prompt Strategist",
    goal="Generate a structured, LLM-optimized draft prompt using best-fit frameworks.",
    backstory=(
        "You're a highly creative prompt architect with deep expertise in PECRA, SCQA, RISEN and others. "
        "You write prompts with clarity, logic, and reusability in mind."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

prompt_architect = Agent(
    role="LLM Prompt Architect & Finisher",
    goal="Polish and finalize the prompt into a clean, executable artifact.",
    backstory=(
        "You specialize in prompt finalization, ensuring outputs are clean, structured, markdown-formatted "
        "and ready to be consumed by LLM APIs or chat UIs."
    ),
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# Full mode only agents
prompt_critic = Agent(
    role="Prompt Critic",
    goal="Critically evaluate structure, tone, and clarity. Offer actionable improvements.",
    backstory="You identify all flaws in prompt structure, coherence, or framework alignment and provide improvements.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

structure_enforcer = Agent(
    role="Prompt Structure Validator",
    goal="Check for strict formatting rules and enforce markdown cleanliness.",
    backstory="You ensure that prompt outputs match the expected markdown structure and rules precisely.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# === TASKS ===

task_analyze = Task(
    description="Analyze the user's instruction: '{instruction}'. Identify core objective, audience, format, and constraints.",
    expected_output=(
        "Structured spec:\n- Objective\n- Audience/LLM\n- Desired Output\n- Background Context\n- Constraints/Edge Cases"
    ),
    agent=requirements_analyst
)

task_research = Task(
    description="Research the best-suited prompt frameworks and techniques from the knowledge base for the task.",
    expected_output=(
        "Framework selection + source citation:\n- Recommended Framework(s)\n- Model-Specific Advice\n- Source Files Used"
    ),
    agent=knowledge_researcher,
    context=[task_analyze]
)

task_draft = Task(
    description="Draft a structured prompt using the specification and frameworks. Apply clarity, structure, reusability.",
    expected_output=(
        "Draft Markdown prompt including:\n- Title (Title Case)\n- Objective\n- Context\n- Workflow Steps\n"
        "- Constraints\n- Validation Criteria\n- Examples"
    ),
    agent=prompt_drafter,
    context=[task_analyze, task_research]
)

task_critique = Task(
    description="Critique the prompt draft for logic, structure, and framework fidelity. Suggest improvements.",
    expected_output="Bullet-point critique with suggested changes to title, structure, or tone.",
    agent=prompt_critic,
    context=[task_draft]
)

task_validate = Task(
    description="Validate the structure of the draft. Ensure markdown formatting, section completeness, and naming conventions.",
    expected_output="Pass/Fail report with justification for any failed structure elements.",
    agent=structure_enforcer,
    context=[task_draft]
)

# Finalize task with proper context
finalize_context = [task_draft] + (
    [task_critique, task_validate] if not USE_LEAN_MODE else []
)

final_note = (
    "\n\n**Instruction to LLM: Execute this prompt directly. No clarification needed.**"
    if INCLUDE_LLM_EXEC_NOTE else ""
)

task_finalize = Task(
    description=(
        "Finalize the prompt using all previous insights. "
        "Ensure Markdown format, structural correctness, and execution-readiness. "
        "Omit meta-comments or feedback prompts. "
        f"Append a directive line only if necessary: {final_note.strip()}"
    ),
    expected_output="Clean, professional, final Markdown prompt. No placeholder text or internal notes.",
    agent=prompt_architect,
    context=finalize_context
)

# === Assemble Crew ===

agents_list = [requirements_analyst, knowledge_researcher, prompt_drafter, prompt_architect]
tasks_list = [task_analyze, task_research, task_draft]

if not USE_LEAN_MODE:
    agents_list.insert(3, prompt_critic)
    agents_list.insert(4, structure_enforcer)
    tasks_list.append(task_critique)
    tasks_list.append(task_validate)

tasks_list.append(task_finalize)

prompt_engineering_crew = Crew(
    agents=agents_list,
    tasks=tasks_list,
    knowledge_sources=[knowledge_source_config] if knowledge_source_config else [],
    process=Process.sequential,
    verbose=True
)

# === CLI Entrypoint ===

def run_prompt_weaver_crew(instruction: str) -> str:
    if not os.getenv("OPENROUTER_API_KEY"):
        raise EnvironmentError("OPENROUTER_API_KEY environment variable not set.")

    print(f"\n🚀 Running Prompt Weaver Crew in {'Lean' if USE_LEAN_MODE else 'Full'} Mode...")
    print(f"🔹 Instruction: {instruction}\n{'-'*50}")

    result = run_with_retries(prompt_engineering_crew.kickoff, inputs={"instruction": instruction})

    print(f"\n{'-'*50}\n✅ Crew completed successfully.")

    return result.final_output if hasattr(result, 'final_output') else str(result)


if __name__ == "__main__":
    user_input = input("Enter your instruction for prompt generation:\n> ").strip()
    if user_input:
        output = run_prompt_weaver_crew(user_input)
        print("\n🎨 Final Generated Prompt:\n")
        print(output)
    else:
        print("No input provided.")
