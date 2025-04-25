import os
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource

def get_knowledge_files(directory="knowledge"):
    valid_exts = (".pdf", ".md")
    return [f for f in os.listdir(directory) if f.endswith(valid_exts)]

def get_docling_tool():
    return CrewDoclingSource(
        file_paths=get_knowledge_files(),
        knowledge_base_directory="knowledge"
    )
