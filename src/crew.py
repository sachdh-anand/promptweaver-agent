import os
from crewai import Crew, Agent, Task, Process, LLM
from tools.docling_tool import get_docling_tool

def load_crew():
    llm = LLM(
        model=f"openrouter/{os.getenv('OPENROUTER_MODEL_ID')}",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
    )

    agent = Agent(
        role="LLM Prompt Architect & Knowledge Integrator",
        goal=(
            "Design world-class, execution-ready prompts that transform high-level ideas into modular, LLM-optimized instructions, "
            "by deeply applying advanced prompt engineering frameworks and integrating insights from a curated internal knowledge base."
        ),
        backstory=(
            "You are PromptWeaver — a legendary prompt architect trained by the original developers of SCQA, PECRA, and RISEN. "
            "You mastered prompt grammar, context control, and multi-agent orchestration for systems at OpenAI, DeepSeek, and Anthropic. "
            "Every prompt you craft must demonstrate surgical clarity, dynamic reasoning, and strategic impact — "
            "structured to be directly usable by LLM agents or human operators without requiring manual cleanup. "
            "**Do NOT include Quality Assurance notes, self-evaluation scores, or Version Control logs inside the delivered prompt.** "
            "Only include clean, execution-ready instructions: objective setting, personas or context, workflows (if applicable), constraints, and validation points, "
            "formatted professionally in Markdown."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm,
    )

    task = Task(
        description=(
            "Using elite prompt engineering frameworks (such as PECRA, SCQA, RISEN) and mandatorily leveraging insights from the provided internal knowledge base, "
            "craft the most optimized, structured, and LLM-ready prompt for: {instruction}. "
            "The output should be organized into the following sections (if applicable to the instruction context): "
            "- **Objective**\n"
            "- **Context and Personas**\n"
            "- **Workflow Steps** (if needed)\n"
            "- **Constraints and Edge Cases**\n"
            "- **Validation Criteria** (if applicable)\n\n"
            "Sections may be omitted if irrelevant to the instruction. "
            "The prompt must be cleanly structured in Markdown, without including any meta-analysis, quality scoring, or version history."
        ),
        expected_output=(
            "A premium-grade, knowledge-enriched prompt, beginning with a clear Title Case heading, logically segmented into clean Markdown headers. "
            "Prompt must be free from Quality Assurance scores, self-evaluation notes, or versioning artifacts — pure execution-ready material."
        ),
        agent=agent,
    )

    return Crew(
        agents=[agent],
        tasks=[task],
        knowledge_sources=[get_docling_tool()],
        process=Process.sequential,
        verbose=True,
    )
