import logging
from pathlib import Path
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource

# Configure logger for this module
logger = logging.getLogger(__name__)

def get_knowledge_files(base_directory="knowledge"):
    """
    Get list of files from the knowledge directory.
    
    Args:
        base_directory: Base name or relative path to the knowledge directory
        
    Returns:
        tuple: (list of file names, absolute path to knowledge directory)
    """
    # Try multiple potential locations for the knowledge directory
    project_root = Path(__file__).parent.parent.parent.absolute()
    
    # List of possible paths in order of preference
    possible_paths = [
        project_root / base_directory,  # Path relative to project root
        Path(base_directory).absolute(), # Absolute path if provided
        Path(__file__).parent.parent / base_directory  # Path relative to src directory
    ]
    
    valid_exts = (".pdf", ".md", ".txt")
    files = []
    knowledge_dir = None
    
    # Find the first valid directory with files
    for path in possible_paths:
        if path.is_dir():
            logger.info(f"Found knowledge directory: {path}")
            # Get just the file names, not full paths
            dir_files = [
                f.name for f in path.iterdir() 
                if f.is_file() and f.suffix.lower() in valid_exts
            ]
            
            if dir_files:
                logger.info(f"Found {len(dir_files)} knowledge files in {path}")
                files = dir_files
                knowledge_dir = path
                break
    
    if not files:
        logger.warning("No knowledge files found in any of the possible paths")
    
    return files, str(knowledge_dir) if knowledge_dir else None

def get_docling_tool():
    """
    Create a CrewDoclingSource configured with knowledge files.
    
    Returns:
        CrewDoclingSource or None: Knowledge source if files were found
    """
    try:
        # Get knowledge files and directory path
        files, knowledge_dir = get_knowledge_files("knowledge")
        
        if not files or not knowledge_dir:
            logger.warning("No knowledge files found. Knowledge source will be disabled.")
            return None
        
        # Important: CrewDoclingSource expects file_paths to be RELATIVE to knowledge_base_directory
        # NOT absolute paths!
        logger.info(f"Creating knowledge source with {len(files)} files")
        logger.info(f"Using knowledge base directory: {knowledge_dir}")
        
        # Debug: Print file paths to verify format
        for file in files[:3]:  # Show first 3 files for debugging
            logger.info(f"Knowledge file (relative path): {file}")
        
        # Create the knowledge source with RELATIVE file paths
        return CrewDoclingSource(
            file_paths=files,  # These are just the file names, relative to knowledge_base_directory
            knowledge_base_directory=knowledge_dir  # This is the absolute directory path
        )
    except Exception as e:
        logger.exception(f"Error creating knowledge source: {e}")
        return None
