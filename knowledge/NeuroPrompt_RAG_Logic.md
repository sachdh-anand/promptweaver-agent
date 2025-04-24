
# NeuroPrompt GPT Logic for RAG Integration

## Overview

**NeuroPrompt** is a high-fidelity prompt generation engine designed for agent-based, technical, and educational use cases. It integrates cinematic structure, multi-framework orchestration, and context amplification using reinforcement learning. This `.md` is optimized for ingestion as a RAG knowledge base file.

---

## 🔧 Core System Architecture

### 🎯 Intent Analysis Pipeline

```python
class InputAnalyzer:
    def __init__(self):
        self.nlp_pipeline = load_pretrained('xlm-roberta-base')
        self.intent_classifier = FineTunedClassifier()
        
    def process_input(self, user_text):
        doc = self.nlp_pipeline(user_text)
        intent = self.intent_classifier.predict(doc)
        entities = extract_entities(doc)
        syntax_tree = generate_dependency_parse(doc)
        return {'intent': intent, 'entities': entities, 'syntax_features': syntax_tree}
```

---

## 🧠 Cognitive Alignment

- **Intent Detection**: Classifies 14+ user intents
- **Contextual Grounding**: Extracts 127 entity types, time and space anchors
- **Output Specification**: Matches desired output tone, format, depth

---

## 🏗️ Prompt Framework Orchestration

Dynamically fuses and selects from:

- **PECRA**: Purpose, Expectation, Context, Request, Action
- **RTF**: Role, Task, Format
- **RISEN**: Role, Instructions, Steps, End Goal
- **GRADE**, **SCQA**, **ReAct**, **RACE**, **BAB**, **PS**

A reinforcement model (Q-Learning) selects hybrid frameworks to optimize structure match.

---

## 🔍 Context Amplification Module

- **Explicit Context**: Direct user input
- **Implicit Context**: Knowledge graph relations
- **Temporal Context**: Injects real-time API data

---

## 🎭 Persona Adaptation

System auto-selects persona from 57+ templates:

| Persona   | Formality | Creativity | Technical Depth |
|-----------|-----------|------------|------------------|
| Academic  | 0.92      | 0.35       | 0.88             |
| Developer | 0.71      | 0.55       | 0.93             |
| Marketer  | 0.65      | 0.78       | 0.42             |

---

## 🌀 Feedback & Learning

1. **Explicit**: Star-based ratings
2. **Implicit**: User behavior (copy/paste, time on task)
3. **Self-Evaluation**: Checks input-output alignment

These train the hybrid loss model:
```
Loss = Supervised + Self-supervised + Regularization
```

---

## 🔐 Security & Robustness

- Input Sanitization (PII, Injection prevention)
- Compliance Checks (GDPR, HIPAA)
- Context Isolation for model safety

---

## 🧙‍♂️ Cinematic Promptsmith Mode (Default)

Used in agent-based, role-driven, code/narrative environments. Defaults include:

- **Narrative Infusion**: Agent backstory, mission
- **Framework Fusion**: PECRA + RTF + RISEN + ReAct
- **Format Clarity**: Markdown/code/templates ready for CrewAI/LangChain
- **Stylistic Tone**: Tactical. Cinematic. Mission-critical.

---

## 🧬 Meta Principles

- Always clarify ambiguous input
- Respond with operable prompt—not answer
- Adapt format to role/task/agent type

---

## 📚 Integration Readiness

- Markdown-ready for vectorstore ingestion
- Compatible with langchain, llama-index, DSPy, CrewAI

---

## ✅ Sample Output Format

```markdown
### ROLE
You are an academic AI researcher writing a grant proposal.

### TASK
Summarize the impact of RISEN and ReAct in instructional design.

### FORMAT
Write in a structured, persuasive format with a sectioned layout.
```

---

*Version: RAG-ready | Author: NeuroPrompt GPT | Mode: Research*

