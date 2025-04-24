from crewai import LLM, Agent, Crew, Process, Task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
import os

# Auto-scan the knowledge folder

def get_knowledge_files(directory="knowledge"):
    valid_exts = (".pdf", ".md")
    return [
        f # Return only the filename
        for f in os.listdir(directory)
        if f.endswith(valid_exts)
    ]

# Use scanned files in CrewDoclingSource
doc_source = CrewDoclingSource(file_paths=get_knowledge_files(), knowledge_base_directory='knowledge') # Explicitly provide the base directory

llm = LLM(
    model=f'openrouter/{os.getenv("OPENROUTER_MODEL_ID")}',
    # model="openrouter/microsoft/mai-ds-r1:free", # Explicitly specify 'openrouter' provider    
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
    llm=llm,
)


task = Task(
    name="Prompt Generation Task", # Add a name here
    description="Create the best possible prompt for: {instruction}",
    expected_output="A well-structured and context-aware prompt that leverages the available knowledge base.",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    knowledge_sources=[doc_source],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    user_input = input("Enter your instruction: ")
    result = crew.kickoff(inputs={"instruction": user_input})
    print("\n🔧 Final Generated Prompt:\n", result)
