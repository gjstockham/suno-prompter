#! /bin/bash

npm install -g @openai/codex
npm install -g @google/gemini-cli
npm install -g @fission-ai/openspec@latest

codex mcp add context7 --url  "https://mcp.context7.com/mcp"
codex mcp add mslearn --url  "https://learn.microsoft.com/api/mcp"
codex mcp add playwright npx "@playwright/mcp@latest"
