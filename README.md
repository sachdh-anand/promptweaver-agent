# PromptWeaver Agent v2 🚀

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-CrewAI-orange.svg)](https://www.crewai.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**PromptWeaver Agent: Transforming Ideas into Optimized AI Prompts**

PromptWeaver Agent v2 is a cutting-edge tool designed to help users craft high-quality prompts for Large Language Models (LLMs). Whether you're a developer, product manager, or creative professional, PromptWeaver leverages advanced frameworks and a curated knowledge base to turn your ideas into actionable, production-ready prompts.

---

## 🌟 Key Features

- **Intelligent Prompt Generation**: Understands user intent and generates optimized prompts using CrewAI agents and LLMs.
- **Knowledge-Driven**: Utilizes a rich knowledge base of prompt engineering techniques and frameworks.
- **Framework Integration**: Supports advanced structures like PECRA, GRADE, and more.
- **Extensibility**: Easily expand the knowledge base by adding new Markdown or PDF files.
- **Enterprise-Grade Security**: Ensures input sanitization and compliance with GDPR/HIPAA standards.

---

## 🛠️ Technology Stack

- **Python 3.12**: Core programming language.
- **CrewAI**: Framework for orchestrating autonomous AI agents.
- **Streamlit**: Interactive web interface for prompt generation.
- **OpenRouter**: Configured LLM provider (customizable).
- **dotenv**: Environment variable management.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12 installed.
- `uv` package manager (`pip install uv`).
- OpenRouter API key (or modify to use a different LLM provider).

### Installation

1. **Clone the Repository**:
   ```bash
   git clone <your-repository-url>
   cd promptweaver-agent
   ```

2. **Set Up Environment Variables**:
   Create a `.env` file in the project root:
   ```env
   OPENROUTER_API_KEY='your_openrouter_api_key_here'
   ```

3. **Install Dependencies**:
   Run the setup script (PowerShell for Windows):
   ```powershell
   .\setup.ps1
   ```

   Alternatively, manually create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

---

## 🎮 Usage

### Backend Operations

To run the backend services and initialize the PromptWeaver Agent, use the `run` script:

**Windows**:
```powershell
.\run.ps1
```

**Linux/Mac**:
```bash
./run.sh
```

This will start the backend services required for the agent to function.

### Interactive UI Application

To launch the interactive UI application, use the `cli` script:

**Windows**:
```powershell
.\cli.ps1
```

**Linux/Mac**:
```bash
./cli.sh
```

This will provide a user-friendly interface for interacting with the PromptWeaver Agent.

---

## 📚 Knowledge Base

The agent's expertise is powered by the `knowledge/` directory, which includes:

- Deepseek Cheatsheet
- Gemini Multiverse Prompting
- God Prompt Techniques
- NeuroPrompt RAG Logic
- Universal Prompt Engineering Framework

You can enhance the agent by adding more `.md` or `.pdf` files to this directory.

---

## 🖥️ Demo

![Demo Screenshot](https://via.placeholder.com/800x400?text=Demo+Screenshot)

---

## 🤝 Contributing

We welcome contributions! Feel free to submit pull requests or open issues for bugs, features, or improvements.

---

## ❓ FAQs

**Q: Can I use a different LLM provider?**
A: Yes, modify the LLM configuration in `src/main.py`.

**Q: How do I add new knowledge sources?**
A: Place `.md` or `.pdf` files in the `knowledge/` directory.

**Q: What if I encounter an error?**
A: Check the logs or open an issue on GitHub.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🌐 Community Support

Join our [Discord Community](https://discord.gg/example) or follow us on [Twitter](https://twitter.com/example) for updates and support.
