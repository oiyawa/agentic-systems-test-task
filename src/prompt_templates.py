PROMPT_INITIAL = """You fix Python functions.

Return ONLY the corrected function in **one** fenced code block:

```python
<function code>
```

Strict rules:

Keep the SAME function name.
Do NOT add or remove parameters.
Do NOT change formatting unnecessarily.
Do NOT add comments or explanations.
Do NOT output anything before or after the code block.
Make the smallest change needed to pass the tests.

Buggy function:
{buggy_code}

Tests (do not modify):
{test_code}

Return the corrected function now:
"""

PROMPT_FEEDBACK = """You are correcting your previous function based on test failure.

Return ONLY the corrected function in this exact format:

```python
<function code>
```

Rules:

No comments.
No explanations.
No reasoning.
No repetition of the prompt or feedback.
Output exactly one fenced python code block.

Original function:
{buggy_code}

Test feedback:
{feedback}

Return corrected function now:
"""