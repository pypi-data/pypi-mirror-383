---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Run command '...'
2. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
What actually happened instead.

## Error Messages
```text
Paste any error messages here
```

## System Information
 - OS: [e.g., Windows 11, macOS 14, Ubuntu 22.04]
 - Python Version: [run `python --version`]
 - uv Version: [run `uv --version`]
 - MCP Client: [e.g., Claude Code, LangGraph, etc.]
 - MCP Context Server Version: [from pyproject.toml]

## Diagnostic Output
Please run and paste output:
```bash
# Test if server starts
uv run python -m app.server

# Check database location
ls -la ~/.mcp/context_storage.db
```

## Additional Context
Add any other context about the problem here.

## Possible Solution
If you have suggestions on how to fix the issue.
