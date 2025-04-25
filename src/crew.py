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
        role="AI Prompt Strategist",
        goal="Transform raw user ideas into high-impact, structured prompts using elite prompt frameworks and contextual knowledge.",
        backstory=(
            "You're PromptWeaver — a legendary prompt strategist trained on advanced techniques like PECRA, SCQA, and RISEN. "
            "You're fluent in multimodal prompting and have instant access to a rich library of prompt engineering guides. "
            "You're trusted to synthesize high-quality, LLM-optimized prompts based on minimal input and supporting material."
        ),
        allow_delegation=False,
        verbose=True,
        llm=llm
    )

    task = Task(
        description="Create the best possible prompt for: {instruction}",
        expected_output="A well-structured and context-aware prompt that leverages the available knowledge base.",
        agent=agent
    )

    return Crew(
        agents=[agent],
        tasks=[task],
        knowledge_sources=[get_docling_tool()],
        process=Process.sequential,
        verbose=True
    )
