# crew.py

import os
from crewai import Crew, Agent, Task, Process
from crewai.llm import LLM
from dotenv import load_dotenv

# --- Tool Setup ---
try:
    from tools.docling_tool import get_docling_tool
    knowledge_tool = get_docling_tool()
except ImportError:
    print("Warning: Could not import get_docling_tool from tools.docling_tool.")
    knowledge_tool = None

# --- Environment Setup ---
load_dotenv()

# --- LLM Configuration ---
llm = LLM(
    model=f"openrouter/{os.getenv('OPENROUTER_MODEL_ID')}",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# --- Agent Definitions ---

requirements_analyst = Agent(
    role="Prompt Requirements Analyst",
    goal="Deeply understand and clarify the user's instruction. Identify objective, audience, format, context, and constraints.",
    backstory="You are a specialist in translating high-level ideas into clear prompt specifications for LLMs.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

knowledge_researcher = Agent(
    role="Prompt Engineering Knowledge Specialist",
    goal="Leverage the internal knowledge base to find the best prompt frameworks, techniques, and model-specific insights.",
    backstory="You instantly map user needs to advanced prompt strategies documented across our internal library.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

prompt_drafter = Agent(
    role="Creative Prompt Drafter",
    goal="Craft the initial structured prompt draft applying the analyzed requirements and research insights.",
    backstory="You are a creative architect, structuring prompts using frameworks like PECRA, SCQA, RISEN.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

prompt_critic = Agent(
    role="Critical Prompt Refiner",
    goal="Critically evaluate the draft against requirements and best practices, offering actionable refinements.",
    backstory="You rigorously critique prompts based on clarity, structure, completeness, and best practices from the knowledge base.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

prompt_architect = Agent(
    role="LLM Prompt Architect & Finisher",
    goal="Synthesize and finalize the execution-ready prompt, strictly clean, formatted, and free of meta notes.",
    backstory="You are the final authority, polishing prompts into flawless, production-grade artifacts.",
    allow_delegation=False,
    verbose=True,
    llm=llm
)

# --- Task Definitions ---

task_analyze = Task(
    description=(
        "Analyze the user's instruction: '{instruction}'. "
        "Break down core objective, target LLM (if any), desired output, key info, and constraints."
    ),
    expected_output=(
        "Structured breakdown including:\n"
        "- Core Objective\n- Target Audience/LLM\n- Desired Output\n- Context/Background\n- Constraints/Edge Cases"
    ),
    agent=requirements_analyst,
)

task_research = Task(
    description=(
        "Based on analysis, synthesize best fitting frameworks, techniques, and model-specific advice from the knowledge base."
    ),
    expected_output=(
        "Summary including:\n"
        "- Recommended Framework(s)\n- Key Techniques\n- Model-specific Tips\n- Important Constraints\n- Knowledge Base References"
    ),
    agent=knowledge_researcher,
    context=[task_analyze],
)

task_draft = Task(
    description=(
        "Draft an initial structured prompt using the requirements and research insights. Apply suitable frameworks."
    ),
    expected_output=(
        "Markdown-formatted draft prompt including sections like Objective, Context, Workflow Steps, Constraints, Validation Criteria."
    ),
    agent=prompt_drafter,
    context=[task_analyze, task_research],
)

task_critique = Task(
    description=(
        "Critique the draft for clarity, completeness, structure, and adherence to best practices."
    ),
    expected_output=(
        "Actionable critique points with specific suggestions for improving the prompt."
    ),
    agent=prompt_critic,
    context=[task_analyze, task_research, task_draft],
)

task_finalize = Task(
    description=(
        "Revise and finalize the structured prompt for immediate execution. "
        "Ensure that the final prompt:\n"
        "- Starts with a Title Case heading\n"
        "- Contains Objective, Context, Workflow Steps, Constraints, Validation Criteria, and Examples\n"
        "- Omits any 'request for clarification', 'feedback prompts', or 'next steps' sections\n"
        "- Ends cleanly without any meta comments or questions\n"
        "- Adds a final line: '**Instruction to LLM: Execute this prompt directly. No clarification needed.**'\n"
        "Format strictly in clean, professional Markdown."
    ),
    expected_output=(
        "A definitive, execution-ready structured prompt without meta sections."
    ),
    agent=prompt_architect,
    context=[task_draft, task_critique],
)


# --- Crew Definition ---

prompt_engineering_crew = Crew(
    agents=[
        requirements_analyst,
        knowledge_researcher,
        prompt_drafter,
        prompt_critic,
        prompt_architect
    ],
    tasks=[
        task_analyze,
        task_research,
        task_draft,
        task_critique,
        task_finalize
    ],
    process=Process.sequential,
    verbose=True,
    knowledge_sources=[knowledge_tool] if knowledge_tool else [],
)

# --- Execution ---

def run_prompt_weaver_crew(instruction: str) -> str:
    """
    Initializes and runs the Prompt Engineering Crew for a given instruction.

    Args:
        instruction (str): High-level user input.

    Returns:
        str: Final execution-ready prompt.
    """
    if not os.getenv("OPENROUTER_API_KEY"):
        raise EnvironmentError("OPENROUTER_API_KEY environment variable not set.")
    
    if not os.getenv("OPENROUTER_MODEL_ID"):
        print("Warning: OPENROUTER_MODEL_ID not set. Using default fallback model.")

    inputs = {'instruction': instruction}

    print("\n🚀 Running Prompt Weaver Crew...")
    print(f"🔹 Instruction: {instruction}")
    print("--------------------------------------------------")

    result = prompt_engineering_crew.kickoff(inputs=inputs)

    print("--------------------------------------------------")
    print("✅ Crew completed successfully.")

    if hasattr(result, 'final_output'):
        return result.final_output
    else:
        return str(result)

if __name__ == "__main__":
    print("Welcome to PromptWeaver!")
    user_instruction = input("Please enter the instruction:\n> ")
    if user_instruction.strip():
        final_prompt = run_prompt_weaver_crew(user_instruction)
        print("\n🎯 Final Generated Prompt:\n")
        print(final_prompt)
    else:
        print("No input provided. Exiting.")
