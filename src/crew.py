import os
from crewai import Crew, Agent, Task, Process, LLM
from tools.docling_tool import get_docling_tool

def load_crew():
    llm = LLM(
        model=f'openrouter/{os.getenv("OPENROUTER_MODEL_ID")}',
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY")
    )

    agent = Agent(
        role="LLM Prompt Architect & Knowledge Integrator",
        goal=(
            "Design world-class, execution-ready prompts that transform high-level ideas into modular, LLM-optimized instructions, "
            "by deeply applying advanced prompt frameworks and integrating insights from a curated internal knowledge base."
        ),
        backstory=(
            "You are PromptWeaver — a legendary prompt architect trained by the original developers of SCQA, PECRA, and RISEN. "
            "Your knowledge spans prompt grammar, context control, and multi-agent orchestration. "
            "You were forged in the crucible of LLM evolution, optimizing thousands of prompts for OpenAI, DeepSeek, and Anthropic. "
            "You operate with surgical clarity — extracting the essence of an idea and structuring it into a fully-realized prompt, "
            "ready for deployment by AI teams or expert humans alike. "
            "You have instant access to an elite internal library of prompt playbooks, logic trees, cheatsheets, and cognitive frameworks. "
            "Every prompt you create must meet your uncompromising standards of clarity, depth, and strategic impact."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    task = Task(
        description=(
            "Using elite prompt engineering frameworks (such as PECRA, SCQA, and RISEN) and mandatorily leveraging the available knowledge base, "
            "craft the most optimized, structured, and LLM-ready prompt for: {instruction}. "
            "The prompt must start with a clear, impactful title in Title Case, followed by well-defined sections: "
            "Objective, Agent Roles, Workflow Steps, Error Handling, and Validation Criteria. "
            "Incorporate insights, structures, or techniques drawn directly from the knowledge base files (e.g., cheatsheets, playbooks, logic guides). "
            "The final output should be markdown-formatted, context-aware, and execution-ready for LLM agents."
        ),
        expected_output=(
            "A premium-grade, knowledge-enriched prompt starting with a clear title and structured with proper markdown headers, "
            "logically segmented sections, and applied prompt engineering techniques from the internal prompt knowledge base."
        ),
        agent=agent
    )

    return Crew(
        agents=[agent],
        tasks=[task],
        knowledge_sources=[get_docling_tool()],
        process=Process.sequential,
        verbose=True
    )
