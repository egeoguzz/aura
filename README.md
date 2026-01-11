# Aura – AI-Powered Dating & Communication Backend

Aura is a production backend service that powers a live iOS application focused on modern dating dynamics, conversation assistance, and social interaction analysis.

The backend is implemented as a single FastAPI service to support rapid iteration during early-stage product development, while maintaining clear logical separation between features, AI orchestration, and data validation within the codebase.

---

## Features

### 1. Aura Match Analysis
Analyzes two user-provided images and evaluates visual compatibility based on style, grooming, and overall perceived vibe.

- Returns a compatibility score (0–100)
- Highlights positive alignment points and potential mismatches
- Provides a direct, realistic verdict
- Focuses on presentation, effort, and context rather than genetic traits

Implemented via a multimodal AI pipeline combining image and text inputs.

---

### 2. Chat Reply Assistant
Analyzes chat screenshots from messaging platforms (e.g. WhatsApp, iMessage, Instagram DMs) and suggests possible replies.

- Evaluates the current conversation dynamic
- Generates multiple reply styles:
  - Low-investment / neutral
  - Playful / teasing
  - Direct / forward
- Designed to keep conversations natural without over-investment

---

### 3. Instagram Story Reply Generator
Generates context-aware replies to Instagram stories based on visual content.

- Analyzes the uploaded story image
- Produces multiple opening lines with different tones
- Avoids generic or copy-paste style responses
- Tailors language usage to cultural and conversational context

---

### 4. Argument Judge
Analyzes chat screenshots from disagreements or arguments.

- Identifies the parties involved
- Evaluates logical consistency and emotional control
- Determines which side currently holds the advantage
- Detects common manipulation patterns and fallacies
- Provides practical advice for de-escalation or response strategy

This feature is designed to prioritize clarity and realism rather than emotional bias.

---

## Multilanguage Support

All AI-generated outputs support multiple languages.

- The desired output language is provided via request parameters
- Prompts are designed to adapt tone, phrasing, and conversational style to the selected language
- Cultural context is considered rather than direct translation

This allows the same backend to serve users across different locales without language-specific branching in the codebase.

---

## Architecture Overview

- Asynchronous FastAPI backend
- Single-entry service (`app.py`) optimized for early-stage agility
- Logical separation within the codebase between:
  - API endpoints
  - AI orchestration and prompt design
  - Data validation using Pydantic models
- Multimodal AI pipelines combining image and text inputs
- JSON-formatted AI outputs for predictable client integration

The architecture prioritizes reliability, iteration speed, and production simplicity.

---

## Deployment

- Deployed as a production backend service
- Powers a live iOS application available on the App Store
- Uses environment-based configuration for secrets and runtime settings
- Managed and deployed via Railway using a Procfile-based startup configuration

---

## Tech Stack

- Python
- FastAPI
- Pydantic
- Google Gemini (Multimodal Generative AI)
- Railway (Deployment)

---

## Notes

The iOS client application is maintained in a separate repository by the iOS developer.

This repository contains the backend service responsible for all AI-driven functionality, API design, and production operation of the system.

---

