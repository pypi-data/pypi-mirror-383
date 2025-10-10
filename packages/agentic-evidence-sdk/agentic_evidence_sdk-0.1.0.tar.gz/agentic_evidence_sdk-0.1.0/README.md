<!-- SPDX-License-Identifier: Apache-2.0 -->
# Agentic Evidence SDK (Python)

A lightweight Python SDK for recording and retrieving agentic evidence with an ergonomic client API. It integrates with the Agentic Evidence backend to log tool invocations, attach artifacts, and verify recorded events.

## Licensing summary
- SDK & demo: Apache-2.0
- Backend: Proprietary
- Docs: CC BY 4.0 (in /docs)
- Examples: CC0 (in /examples)
- NOTICE: Yes

## Requirements
- Python >= 3.10

## Installation
- Once published to PyPI: `pip install agentic-evidence-sdk`
- For local development: `pip install -e .[dev]`

## Quickstart
- From repo root:
  - `cd sdk/python`
  - `pip install -e .`
  - `python ../../demo-agent/demo_agent.py`  # run demo agent and record a sample event
  - `pytest`  # run tests (add when available)
- See the full quickstart: https://rajeshwar77.github.io/open-agent-evidence-docs/

## Links
- Documentation: https://rajeshwar77.github.io/open-agent-evidence-docs/
- Repository: https://github.com/Rajeshwar77/open-agent-evidence
- Changelog: https://github.com/Rajeshwar77/open-agent-evidence-docs/blob/main/docs/RELEASE-NOTES.md

## Development
- Install dev extras: `pip install -e .[dev]`
- Build sdist/wheel: `python -m build`
- Check metadata: `python -m twine check dist/*`