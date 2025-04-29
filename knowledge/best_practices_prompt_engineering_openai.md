# Best Practices for Prompt Engineering with the OpenAI API
_Source: [OpenAI Help Center](https://help.openai.com/en/articles/6654000-best-practices-for-prompt-engineering-with-the-openai-api)_

## How prompt engineering works
Due to the way OpenAI models are trained, specific prompt formats lead to better outputs. The [official guide](https://platform.openai.com/docs/guides/prompt-engineering) is a great starting point.

## Rules of Thumb and Examples

### 1. Use the latest model
- Always use the most capable and recent models for better results.

### 2. Put instructions at the beginning and use clear separators (### or triple quotes)
- **Less Effective:**

```
Summarize the text below as bullet points. {text input here}
```

- **Better:**

```
Summarize the text below as bullet points.

Text: """ {text input here} """
```

### 3. Be specific, descriptive, and detailed
- Define the desired context, outcome, length, format, and style clearly.

### 4. Articulate output format with examples
- Models respond better when shown examples of expected output formats.

### 5. Start with zero-shot prompting, move to few-shot, then fine-tune if necessary
- Use simple examples or fine-tuning based on complexity.

### 6. Avoid vague instructions
- Be precise with length, structure, or outcome expectations.

### 7. Explain positive actions instead of only restrictions
- Instead of "Don't do X", specify "Do Y".

### 8. For code generation, use leading words
- Use keywords like `import` for Python or `SELECT` for SQL to guide the model.

### 9. Use the 'Generate Anything' feature
- Describe the task naturally and let the model create a suitable prompt.

---

## Key Parameters
- **model**: Newer models offer better performance.
- **temperature**: Controls randomness. Lower for factual accuracy (e.g., 0).
- **max_tokens**: Sets a hard limit for token generation.
- **stop**: Defines sequences that end the response.

_For deeper API parameter reference, see [OpenAI API documentation](https://platform.openai.com/docs/api-reference)._
