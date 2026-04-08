# Legal Contract Risk Reviewer Architecture

This project is structured as a resilient, OpenEnv-compliant reinforcement learning and agent evaluation benchmark.

## System Workflow

```text
 1. Agent Runtime (inference.py)
        │
        ▼  HTTP POST /step (JSON)
 2. Environment Server (app.py API Layer)
        │
        ▼  Routes action internally
 3. Core Logic (contract_environment.py)
        │
        ▼  Extracts tasks & updates state
 4. Grader Evaluation (graders.py)
        │
        ▼  Mathematical & Rule-based scoring
 5. Reward Signal (0.0 - 1.0)
        │
        ▼  Returned as OpenEnv Observation
 6. Agent Refinement
```

## Core Components

- **`contract_environment.py`**: The "brain" of the environment handling strict `reset()`, `step()`, and `state()` compliance. Now includes anti-hack guardrails, history tracking, and cost-awareness mechanics.
- **`graders.py`**: A strictly deterministic scoring engine decoupled from LLMs to ensure that standardizing and benchmarking agents is mathematical, rigorous, and 100% reproducible.
- **`app.py`**: Houses the FastAPI layer managing routing for OpenEnv protocols alongside a Gradio UI setup.
- **`models.py`**: Uses strictly typed Pydantic models to assert strong contracts between the LLM Output (`Action`) and the Environment Response (`Observation`).
