# PromptWeaver Agent v2

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-CrewAI-orange.svg)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Transform vague ideas into powerful, optimized AI prompts using cutting-edge frameworks and a curated knowledge base.**

PromptWeaver Agent v2 is an intelligent agent built with CrewAI designed to assist users in generating high-quality prompts for Large Language Models (LLMs). It leverages a dedicated knowledge base containing various prompt engineering strategies, frameworks (like PECRA, GRADE, Alex Formula), and best practices to convert simple instructions into effective prompts.

## Key Features

*   **Intelligent Prompt Generation:** Utilizes an LLM (configured via OpenRouter) and CrewAI agents to understand user intent and generate optimized prompts.
*   **Knowledge-Driven:** References a local knowledge base (`knowledge/` directory) containing Markdown files on prompt engineering techniques.
*   **Framework Integration:** Capable of applying and combining various prompt structures (e.g., PECRA, GRADE) for optimal results.
*   **Extensible:** Add new documents to the `knowledge/` folder to expand the agent's expertise.
*   **Security and Compliance:** Implements input sanitization, GDPR/HIPAA compliance checks, and context isolation for robust security.

## Technology Stack

*   **Python 3.12:** Core programming language.
*   **CrewAI:** Framework for orchestrating autonomous AI agents.
*   **Docling:** Library used by CrewAI for processing knowledge base documents (PDFs, Markdown).
*   **OpenRouter:** Configured LLM provider (can be changed in `src/main.py`).
*   **dotenv:** For managing environment variables (like API keys).

## Getting Started

### Prerequisites

*   Python 3.12 installed.
*   `uv` installed (`pip install uv` or see [uv installation guide](https://github.com/astral-sh/uv)).
*   An OpenRouter API key (or modify `src/main.py` to use a different LLM provider).

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd promptweaver-agent
    ```
2.  **Set up Environment Variable:**
    Create a `.env` file in the project root and add your OpenRouter API key:
    ```env
    OPENROUTER_API_KEY='your_openrouter_api_key_here'
    ```
3.  **Run the setup script (using PowerShell on Windows):**
    This script will create a virtual environment, install dependencies using `uv`, and run the agent.
    ```powershell
    .\setup.ps1
    ```
    *(Alternatively, you can manually create a venv, activate it, and run `uv pip install -r requirements.txt` if you generate one from `pyproject.toml`)*

## Usage

Once the setup is complete, the `setup.ps1` script will automatically run `src/main.py`. The script will prompt you to enter your instruction:

```
Enter your instruction: [Your vague idea or goal here]
```

The agent will then process your input, consult its knowledge base, and generate an optimized prompt based on established frameworks. The final prompt will be printed to the console.

Example:

```
Enter your instruction: Create a social media post about the benefits of using AI for content creation
```

*(Agent processing output will appear here)*

```
🔧 Final Generated Prompt:
[Generated optimized prompt using a framework like PECRA or similar]
```

## Knowledge Base

The agent's expertise comes from the files located in the `knowledge/` directory. Currently, it includes resources on:

*   Deepseek Cheatsheet
*   Gemini Multiverse Prompting
*   God Prompt Techniques
*   Grok Cheatsheet
*   NeuroPrompt RAG Logic
*   NeuroPrompt Situational Playbook
*   Universal Prompt Engineering Framework

You can enhance the agent's capabilities by adding more relevant `.md` or `.pdf` files to this directory. The agent automatically scans and incorporates these files upon startup.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
