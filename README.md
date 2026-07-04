# AI Channel Intelligence Platform

AI Channel Intelligence Platform is a modular Python backend for analyzing creator channels, extracting audience intelligence from viewer comments, and generating structured AI-assisted insights.

This project is currently under active development.

## Current Architecture

```text
YouTube Service
-> Comment Filter Service
-> Audience Intelligence Service
-> Qwen/Ollama Report Flow
```

## Current Features

- Fetch latest YouTube videos.
- Fetch comments from YouTube videos.
- Clean and filter metadata/noise comments.
- Preserve comment video context with a structured comment model.
- Detect audience themes such as praise, criticism, humor, and repeated concerns.
- Generate local Qwen/Ollama-based reports from structured audience insights.

## Project Structure

- `app/services/` contains service modules for YouTube access, comment filtering, and audience intelligence.
- `docs/` contains public project documentation, currently including `PROJECT_OVERVIEW.md`.
- `channel_analyzer.py` is the current end-to-end entry point for fetching videos, analyzing comments, and generating a Qwen/Ollama report.
- `ai_report.py`, `ai_reviewer.py`, and `qwen_test.py` are supporting scripts for testing report prompts and local model behavior.

## How To Run

Install dependencies:

```powershell
pip install requests python-dotenv
```

Create a `.env` file in the project root with your YouTube API key:

```text
YOUTUBE_API_KEY=your_api_key_here
```

Run Ollama locally with the required model:

```powershell
ollama run qwen2.5:3b
```

Run the channel analyzer:

```powershell
python channel_analyzer.py
```

## Current Foundation ✅

- YouTube Service
- Comment Filter
- Audience Intelligence
- Structured Comment Model
- Evidence Context

## Next Milestone 🚧

- Comparison Engine
- Report Generator
- Hybrid AI Classifier

## Future Platform

- Database
- Smart Analysis Cache
- FastAPI backend
- React dashboard
- Multi-platform support
