# AI Channel Intelligence Platform

AI Channel Intelligence Platform is the future home of the RushMiniDrama channel analysis tools. It currently contains working prototype scripts for analyzing YouTube comments with local Qwen/Ollama prompts, plus a new clean package structure for future development.

The current priority is to preserve the working prototypes while gradually moving stable logic into `app/`.

## Current State

- Prototype scripts remain at the project root.
- No existing Python script has been moved.
- `app/` contains only package markers for future modules.
- `docs/` is ready for planning and technical notes.

## Run Current Scripts

Install basic dependencies:

```powershell
pip install requests python-dotenv
```

Run a prototype:

```powershell
python ai_report.py
python ai_reviewer.py
python qwen_test.py
python channel_analyzer.py
```

Qwen-based scripts expect Ollama to be running locally with `qwen2.5:3b`.

For more detail, see `PROJECT_OVERVIEW.md`.
