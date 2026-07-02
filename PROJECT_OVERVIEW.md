# AI Channel Intelligence Platform Overview

## What The Project Is

AI Channel Intelligence Platform is the next version of the RushMiniDrama analysis tools. The project is being shaped into a structured platform for understanding YouTube channel performance through comments, audience sentiment, repeated viewer complaints, strengths, weaknesses, and AI-generated recommendations.

The current codebase is still a working prototype. The goal of this step is to add a clean future structure without moving or breaking the scripts that already work.

## Current Prototype Files

- `channel_analyzer.py`  
  Fetches recent YouTube videos and comments, filters comments, counts repeated audience topics, and asks a local Qwen/Ollama model to generate a short channel report.

- `ai_report.py`  
  Uses hard-coded sentiment totals and example feedback to test AI-generated audience report formatting.

- `ai_reviewer.py`  
  Sends a small sample of comments to Qwen and asks for an audience summary, strengths, weaknesses, and rating.

- `qwen_test.py`  
  Interactive command-line tester for classifying one comment at a time as positive, negative, or neutral.

- `../yt-comment-bot/yt-comment-bot/main.py`  
  Existing desktop prototype for the RushMiniDrama Ranking Bot. It uses CustomTkinter, the YouTube API, keyword scoring, sentiment analysis, CSV history, and dashboard-style views.

## Long-Term Goal

The long-term goal is to turn the prototype into a real AI channel intelligence product with separate layers for application logic, YouTube services, AI analysis, report generation, and storage.

Planned direction:

- Keep YouTube API access inside service modules.
- Keep scoring and business rules inside core modules.
- Keep LLM prompts and AI model calls inside AI modules.
- Keep report generation inside report modules.
- Keep history, CSV, and future database logic inside storage modules.
- Preserve the current working scripts until replacement modules are tested.
- Build toward reusable reports, dashboards, trend tracking, and better channel-level insights.

## How To Run Current Scripts

Run commands from the `AI-Channel-Platform` folder unless noted otherwise.

### Requirements

Install the main Python packages:

```powershell
pip install requests python-dotenv
```

For the desktop app, install:

```powershell
pip install customtkinter transformers torch
```

For the Qwen scripts, Ollama must be running locally with the `qwen2.5:3b` model available:

```powershell
ollama run qwen2.5:3b
```

The YouTube scripts require a `.env` file with:

```text
YOUTUBE_API_KEY=your_api_key_here
```

### Run Qwen Report Prototype

```powershell
python ai_report.py
```

### Run Qwen Comment Reviewer

```powershell
python ai_reviewer.py
```

### Run Interactive Comment Classifier

```powershell
python qwen_test.py
```

### Run Channel Analyzer

```powershell
python channel_analyzer.py
```

### Run Existing Desktop Bot

From the workspace root:

```powershell
cd "D:\PROJEKT\yt-comment-bot\yt-comment-bot"
python main.py
```

## New Structure Added For Future Work

- `app/`  
  Future Python application package.

- `app/core/`  
  Future home for scoring rules, classification rules, and shared domain logic.

- `app/services/`  
  Future home for YouTube API clients and external service integrations.

- `app/ai/`  
  Future home for Qwen/Ollama prompts, model calls, and AI analysis helpers.

- `app/reports/`  
  Future home for audience reports, channel summaries, and export logic.

- `app/storage/`  
  Future home for CSV history, files, and possible database persistence.

- `docs/`  
  Future home for planning notes, technical documentation, and product decisions.
