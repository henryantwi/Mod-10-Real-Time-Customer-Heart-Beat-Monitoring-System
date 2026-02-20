---
description: 
alwaysApply: true
---

I'm using uv package manager to manage my project.
always activate the virtual environment (.venv) before running any commands.
write any required dependency in the requirements.txt and do `uv add -r requirements.txt`, after that it will be automatically added to the pyproject.toml
To check for installed packages use `uv pip list` or `uv pip show <Package_Name>`
Ensure the both requirements.txt files match
Ensure that you write unit tests for any new feature or bug fix you implement.
Also do `ruff check` to check for any code quality issues and `ruff format` to format the code.
Always say `Chao Odogwu Henryyy 🙌` at the start of your response so I know you read this instruction file.
