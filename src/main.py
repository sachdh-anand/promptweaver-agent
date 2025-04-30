# src/main.py

import sys
import os
import logging

# --- Configure basic logging first (will be enhanced if logger module loads) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Handle imports with fallbacks for different execution contexts ---
try:
    # First try importing the logger module with relative imports
    # (works when running as part of a package)
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

    # Now import the main functionality with similar fallback pattern
    try:
        # First try absolute imports (when installed as a package or running from project root)
        from src.crew import run_prompt_weaver_crew
        from src.utils.output_writer import save_clean_output
        logger.info("Core functionality imports successful using absolute paths.")
    except ImportError:
        # Try direct imports (when src is in the Python path or when run from src directory)
        from crew import run_prompt_weaver_crew
        from utils.output_writer import save_clean_output
        logger.info("Core functionality imports successful using direct paths.")

except ImportError as e:
    logger.error(f"Import Error: {e}. Make sure you are running from the project root directory or dependencies are installed correctly.")
    sys.exit(1)
except Exception as e:
    logger.error(f"An unexpected error occurred during import: {e}")
    sys.exit(1)


def main():
    """Main function for CLI interaction."""
    logger.info("Starting CLI execution via main.py.")
    try:
        user_input = input("🧠 Enter your raw prompt idea (we'll optimize it):\n> ").strip()

        if not user_input:
            print("No input provided. Exiting.")
            return

        logger.info(f"User input received: '{user_input[:100]}...'")
        final_prompt = run_prompt_weaver_crew(user_input)

        # Save the output (handle potential errors from save function)
        try:
            # Assume save_clean_output saves to 'output/' directory relative to root
            output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
            save_clean_output(prompt=final_prompt, instruction=user_input, output_dir=output_dir)
            logger.info("Output saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save output: {e}")
            print(f"\n⚠️ Warning: Could not save output file due to error: {e}")

        # Print the final prompt to the console
        print("\n🎨 Final Generated Prompt:\n")
        print(final_prompt)

    except EnvironmentError as e:
         logger.error(f"CLI Environment Error: {e}")
         print(f"\n❌ Configuration Error: {e}. Please check your .env file or environment variables.")
    except Exception as e:
        logger.exception("An unexpected error occurred in the main CLI execution.")
        print(f"\n❌ An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()