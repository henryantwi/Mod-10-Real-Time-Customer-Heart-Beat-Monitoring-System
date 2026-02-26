# Using uv with pre-commit | uv

**Source:** https://docs.astral.sh/uv/guides/integration/pre-commit/
**Saved:** 2026-02-26T15:04:42.060Z

*Generated with [markdown-printer](https://github.com/levz0r/markdown-printer) (v1.1.1) by [Lev Gelfenbuim](https://lev.engineer)*

---

# [Using uv in pre-commit](https://docs.astral.sh/uv/guides/integration/pre-commit/#using-uv-in-pre-commit)

An official pre-commit hook is provided at [`astral-sh/uv-pre-commit`](https://github.com/astral-sh/uv-pre-commit).

To use uv with pre-commit, add one of the following examples to the `repos` list in the `.pre-commit-config.yaml`.

To make sure your `uv.lock` file is up to date even if your `pyproject.toml` file was changed:

.pre-commit-config.yaml

`[](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-0-1)repos: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-0-2)  - repo: https://github.com/astral-sh/uv-pre-commit [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-0-3)    # uv version. [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-0-4)    rev: 0.10.6 [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-0-5)    hooks: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-0-6)      - id: uv-lock`

To keep a `requirements.txt` file in sync with your `uv.lock` file:

.pre-commit-config.yaml

`[](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-1-1)repos: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-1-2)  - repo: https://github.com/astral-sh/uv-pre-commit [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-1-3)    # uv version. [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-1-4)    rev: 0.10.6 [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-1-5)    hooks: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-1-6)      - id: uv-export`

To compile requirements files:

.pre-commit-config.yaml

`[](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-1)repos: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-2)  - repo: https://github.com/astral-sh/uv-pre-commit [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-3)    # uv version. [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-4)    rev: 0.10.6 [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-5)    hooks: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-6)      # Compile requirements [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-7)      - id: pip-compile [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-2-8)        args: [requirements.in, -o, requirements.txt]`

To compile alternative requirements files, modify `args` and `files`:

.pre-commit-config.yaml

`[](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-1)repos: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-2)  - repo: https://github.com/astral-sh/uv-pre-commit [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-3)    # uv version. [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-4)    rev: 0.10.6 [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-5)    hooks: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-6)      # Compile requirements [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-7)      - id: pip-compile [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-8)        args: [requirements-dev.in, -o, requirements-dev.txt] [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-3-9)        files: ^requirements-dev\.(in|txt)$`

To run the hook over multiple files at the same time, add additional entries:

.pre-commit-config.yaml

`[](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-1)repos: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-2)  - repo: https://github.com/astral-sh/uv-pre-commit [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-3)    # uv version. [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-4)    rev: 0.10.6 [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-5)    hooks: [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-6)      # Compile requirements [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-7)      - id: pip-compile [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-8)        name: pip-compile requirements.in [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-9)        args: [requirements.in, -o, requirements.txt] [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-10)      - id: pip-compile [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-11)        name: pip-compile requirements-dev.in [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-12)        args: [requirements-dev.in, -o, requirements-dev.txt] [](https://docs.astral.sh/uv/guides/integration/pre-commit/#__codelineno-4-13)        files: ^requirements-dev\.(in|txt)$`

February 24, 2026