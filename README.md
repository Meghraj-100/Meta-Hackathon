# 📜 Legal Contract Risk Reviewer

An **OpenEnv** environment where AI agents analyze legal contracts to identify risky terms, missing standard clauses, and legal loopholes. Built for the OpenEnv Round 1 Bootcamp hackathon.

## 🎯 Environment Description

This environment simulates the real-world task of **legal contract risk review** — a task performed daily by lawyers, paralegals, and contract managers. An AI agent receives a legal contract and must produce a comprehensive risk analysis including:

- **Risky clauses**: One-sided terms, unfair provisions, unconscionable limitations
- **Missing protections**: Standard clauses that should be present but are absent
- **Contradictions**: Conflicting provisions that create legal loopholes
- **Recommendations**: Actionable remediation suggestions

### Why This Domain?

Legal contract review is a high-value, high-stakes real-world task where:
- Mistakes can cost millions (missed liability clauses, unnoticed loopholes)
- Expert human review is expensive ($300-800/hour for senior attorneys)
- The task requires multi-step reasoning across long documents
- There's a clear gradient of difficulty from obvious issues to subtle contradictions

## 📋 Tasks (3 Difficulty Levels)

| Task ID | Difficulty | Description | What the Agent Must Do |
|---------|-----------|-------------|----------------------|
| `task_1_easy` | Easy | One-sided liability clause | Spot a blatantly unfair Section 7 that excludes ALL provider liability including gross negligence and fraud |
| `task_2_medium` | Medium | Missing indemnification | Identify that a consulting agreement completely lacks an indemnification clause despite having IP and data handling provisions |
| `task_3_hard` | Hard | Contradictory clauses | Detect that Section 4 (comprehensive warranty) fundamentally contradicts Section 11 (extreme liability cap), creating an exploitable loophole in a 14-section contract |

### Scoring

All tasks are scored on a **0.0-1.0 scale** with partial credit:

- **Clause identification** (25-35%): Did the agent find the right section(s)?
- **Risk classification** (20-25%): Did it correctly categorize the issue type?
- **Explanation quality** (20-25%): Does the analysis contain substantive legal reasoning?
- **Recommendations** (15-20%): Did the agent suggest remediation?

Graders are **fully deterministic** — same analysis always produces the same score.

## 🔧 Action & Observation Spaces

### Action Space (`ContractAction`)

```json
{
    "identified_risks": [
        {
            "clause_reference": "Section 7.1",
            "risk_type": "one-sided liability exclusion",
            "explanation": "Provider excludes all liability including gross negligence..."
        }
    ],
    "missing_clauses": [
        {
            "clause_type": "indemnification",
            "importance": "critical"
        }
    ],
    "contradictions": [
        {
            "clause_a": "Section 4",
            "clause_b": "Section 11",
            "explanation": "Warranty promises in S4 are nullified by liability cap in S11..."
        }
    ],
    "overall_assessment": "This contract contains significant risk imbalances...",
    "recommendations": [
        "Negotiate mutual liability provisions",
        "Add indemnification clause"
    ]
}
```

### Observation Space (`ContractObservation`)

On `reset()`:
- `contract_text`: Full contract text to analyze
- `task_id`: Current task identifier
- `task_description`: What to look for
- `task_difficulty`: easy / medium / hard
- `instructions`: Detailed analysis instructions

On `step()`:
- `feedback`: Detailed grading feedback with ✓/✗ markers
- `score`: Numerical score (0.0-1.0)
- `done`: Episode completion flag

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Docker (for containerized deployment)

### Local Development

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/legal-contract-risk-reviewer
cd legal-contract-risk-reviewer

# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Run the server locally
uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

# In another terminal, run inference
python inference.py
```

### Docker

```bash
# Build the image
docker build -t legal-contract-risk-reviewer .

# Run locally
docker run -p 7860:7860 \
  -e OPENAI_API_KEY=sk-... \
  -e ENABLE_WEB_INTERFACE=true \
  legal-contract-risk-reviewer
```

### Deploy to Hugging Face Spaces

```bash
# Install OpenEnv CLI
pip install openenv-core

# Push to HF Spaces
openenv push --repo-id YOUR_USERNAME/legal-contract-risk-reviewer
```

## 📊 Baseline Scores

Baseline scores using `gpt-4o-mini` with `temperature=0`:

| Task | Difficulty | Score | Description |
|------|-----------|-------|-------------|
| `task_1_easy` | Easy | ~0.75-0.90 | One-sided liability (well-detected) |
| `task_2_medium` | Medium | ~0.55-0.75 | Missing indemnification (moderate) |
| `task_3_hard` | Hard | ~0.40-0.65 | Contradictory clauses (challenging) |

*Scores may vary slightly based on model version and API endpoint.*

## 🏗️ Project Structure

```
legal-contract-risk-reviewer/
├── openenv.yaml                  # OpenEnv manifest
├── pyproject.toml                # Dependencies & config
├── models.py                     # Pydantic Action/Observation/State models
├── client.py                     # EnvClient subclass
├── __init__.py                   # Package exports
├── inference.py                  # Baseline inference script (OpenAI API)
├── Dockerfile                    # HF Spaces deployment
├── .env.example                  # Environment variable template
├── README.md                     # This file
└── server/
    ├── __init__.py
    ├── app.py                    # FastAPI server + Gradio web UI
    ├── contract_environment.py   # Core environment logic
    ├── contracts.py              # Contract data & ground truth
    └── graders.py                # Deterministic grading functions
```

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes | — | API key for LLM inference |
| `API_BASE_URL` | Yes | `https://api.openai.com/v1` | LLM API endpoint |
| `MODEL_NAME` | Yes | `gpt-4o-mini` | Model identifier |
| `HF_TOKEN` | For deploy | — | Hugging Face token |
| `ENABLE_WEB_INTERFACE` | No | `false` | Enable Gradio UI at `/web` |
| `ENV_BASE_URL` | No | `http://localhost:8000` | Environment server URL |

## 🧪 Testing

```bash
# Run the server
uvicorn server.app:app --host 0.0.0.0 --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test reset
curl -X POST http://localhost:8000/reset \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task_1_easy"}'

# Test step
curl -X POST http://localhost:8000/step \
  -H "Content-Type: application/json" \
  -d '{
    "identified_risks": [{"clause_reference": "Section 7", "risk_type": "one-sided liability", "explanation": "Provider excludes all liability"}],
    "overall_assessment": "Contract has significant liability issues",
    "recommendations": ["Add mutual liability cap"]
  }'

# Run full inference
python inference.py
```

## 📜 License

MIT License
