import os
import re
import hashlib
from datetime import datetime

def extract_simple_title(text: str) -> str:
    # Try to extract a concise title from the prompt (first sentence or main keywords)
    # Use up to 7 words from the first sentence or phrase
    first_sentence = re.split(r'[.!?\n]', text.strip())[0]
    words = re.findall(r'\w+', first_sentence)
    title = " ".join(words[:7])
    return title.title() if title else "Prompt Output"

def extract_markdown_header(text: str) -> str:
    # Extract the first Markdown H1 header (e.g., '# Title')
    match = re.search(r'^# (.+)', text, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return None

def sanitize_filename(text: str) -> str:
    # Limit filename to first 10 words and add a short hash for uniqueness
    base = "_".join(re.findall(r'\w+', text.strip().lower()))[:100]
    short_text = "_".join(base.split("_")[:10])  # first 10 tokens
    hash_id = hashlib.md5(text.encode()).hexdigest()[:6]
    return f"{short_text}_{hash_id}"

def get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

def save_clean_output(prompt: str, instruction: str, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    # Try to extract the first Markdown header from the prompt
    header_title = extract_markdown_header(prompt)
    if header_title:
        simple_title = header_title
    else:
        # Fallback to extracting from instruction
        simple_title = extract_simple_title(instruction)
    sanitized_title = "_".join(simple_title.lower().split())
    filename = f"{sanitized_title}_{get_timestamp()}.md"
    filepath = os.path.join(output_dir, filename)

    # Strip framework explanation if present
    clean_prompt = prompt.split("This prompt combines")[0].strip()

    # Only prepend H1 if not already present
    if not re.match(r"^# ", clean_prompt):
        markdown_output = f"# {simple_title}\n\n{clean_prompt}\n"
    else:
        markdown_output = f"{clean_prompt}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"\n✅ Prompt saved to: {filepath}")
