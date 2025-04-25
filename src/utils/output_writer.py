import os
import re
import hashlib
from datetime import datetime

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

    filename = f"{sanitize_filename(instruction)}_{get_timestamp()}.md"
    filepath = os.path.join(output_dir, filename)

    # Strip framework explanation if present
    clean_prompt = prompt.split("This prompt combines")[0].strip()

    markdown_output = f"# Prompt: {instruction.strip().title()}\n\n{clean_prompt}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown_output)

    print(f"\n✅ Prompt saved to: {filepath}")
