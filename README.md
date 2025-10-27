# ReAct LLM Fix Agent (local model)

This project implements a ReAct-style agent that attempts to fix buggy Python functions using a local LLM (via `transformers`) and evaluates them on a HumanEvalFix subset.

## Requirements
- Python 3.10+
- pip packages from `requirements.txt`

## Install
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
