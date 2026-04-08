"""
Baseline Inference Script for the Legal Contract Risk Reviewer.

Uses the OpenAI API client to run an LLM agent against all 3 tasks.
Produces structured [START], [STEP], and [END] logs as required
by the hackathon evaluation format.

Required environment variables:
    OPENAI_API_KEY  — API key for the LLM service
    API_BASE_URL    — API endpoint (default: https://api.openai.com/v1)
    MODEL_NAME      — Model identifier (default: gpt-4o-mini)

Usage:
    export OPENAI_API_KEY=sk-...
    python inference.py
"""

import json
import os
import sys
import time
import traceback
from typing import Any, Dict, List

import requests
from openai import OpenAI

# ─── Configuration ───────────────────────────────────────────────────────────

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")

# Environment server URL (local by default)
ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:8000")

# ─── OpenAI Client Setup ────────────────────────────────────────────────────

client = OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=API_BASE_URL,
)

# ─── System Prompt ───────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert legal contract risk reviewer. Your job is to carefully analyze legal contracts and identify potential risks, missing protections, and problematic clauses.

When analyzing a contract, you must provide your analysis in a specific JSON format. Your response MUST be valid JSON with the following structure:

{
    "identified_risks": [
        {
            "clause_reference": "Section X.Y",
            "risk_type": "description of the type of risk",
            "explanation": "detailed explanation of why this is risky"
        }
    ],
    "missing_clauses": [
        {
            "clause_type": "name of the missing clause type",
            "importance": "critical/high/medium/low"
        }
    ],
    "contradictions": [
        {
            "clause_a": "Section X",
            "clause_b": "Section Y",
            "explanation": "how these clauses contradict each other"
        }
    ],
    "overall_assessment": "A comprehensive summary of the contract's risk profile",
    "recommendations": [
        "Specific recommendation 1",
        "Specific recommendation 2"
    ]
}

Be thorough and precise. Reference specific section numbers. Explain your reasoning clearly.
IMPORTANT: Respond ONLY with valid JSON. No markdown, no code blocks, no extra text."""


# ─── Helper Functions ────────────────────────────────────────────────────────

def env_reset(task_id: str) -> Dict[str, Any]:
    """Reset the environment via HTTP API."""
    response = requests.post(
        f"{ENV_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def env_step(action: Dict[str, Any]) -> Dict[str, Any]:
    """Submit an action to the environment via HTTP API."""
    response = requests.post(
        f"{ENV_BASE_URL}/step",
        json=action,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def env_state() -> Dict[str, Any]:
    """Get environment state via HTTP API."""
    response = requests.get(
        f"{ENV_BASE_URL}/state",
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def call_llm(contract_text: str, task_description: str, instructions: str) -> Dict[str, Any]:
    """
    Call the LLM to analyze a contract.

    Returns the parsed JSON action from the LLM response.
    """
    user_prompt = f"""## Task
{task_description}

## Instructions
{instructions}

## Contract to Analyze
{contract_text}

Analyze this contract and provide your findings in the required JSON format. Remember to respond ONLY with valid JSON."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,  # Deterministic for reproducibility
        max_tokens=4096,
    )

    raw_response = response.choices[0].message.content.strip()

    # Clean up response — remove markdown code blocks if present
    if raw_response.startswith("```"):
        lines = raw_response.split("\n")
        # Remove first line (```json) and last line (```)
        lines = [l for l in lines if not l.strip().startswith("```")]
        raw_response = "\n".join(lines)

    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        start = raw_response.find("{")
        end = raw_response.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                parsed = json.loads(raw_response[start:end])
            except json.JSONDecodeError:
                parsed = {
                    "identified_risks": [],
                    "missing_clauses": [],
                    "contradictions": [],
                    "overall_assessment": raw_response,
                    "recommendations": [],
                }
        else:
            parsed = {
                "identified_risks": [],
                "missing_clauses": [],
                "contradictions": [],
                "overall_assessment": raw_response,
                "recommendations": [],
            }

    # Ensure all required keys exist
    parsed.setdefault("identified_risks", [])
    parsed.setdefault("missing_clauses", [])
    parsed.setdefault("contradictions", [])
    parsed.setdefault("overall_assessment", "")
    parsed.setdefault("recommendations", [])

    return parsed


# ─── Main Inference Loop ────────────────────────────────────────────────────

def run_task(task_id: str) -> Dict[str, Any]:
    """
    Run a single task: reset → LLM analysis → step → score.

    Returns dict with task results.
    """
    # Reset environment
    reset_result = env_reset(task_id)
    observation = reset_result["observation"]

    contract_text = observation["contract_text"]
    task_description = observation["task_description"]
    instructions = observation["instructions"]
    difficulty = observation["task_difficulty"]

    print(f"[STEP] task_id={task_id} difficulty={difficulty} status=analyzing", flush=True)

    # Call LLM to analyze the contract
    llm_start = time.time()
    action = call_llm(contract_text, task_description, instructions)
    llm_duration = round(time.time() - llm_start, 2)

    print(f"[STEP] task_id={task_id} llm_duration={llm_duration}s status=submitting", flush=True)

    # Submit action to environment for grading
    step_result = env_step(action)

    score = step_result.get("reward", 0.0)
    done = step_result.get("done", True)
    feedback = step_result.get("observation", {}).get("feedback", "")

    print(f"[STEP] task_id={task_id} score={score} done={done} llm_time={llm_duration}s", flush=True)

    return {
        "task_id": task_id,
        "difficulty": difficulty,
        "score": score,
        "done": done,
        "feedback": feedback,
        "llm_duration": llm_duration,
        "action_summary": {
            "num_risks": len(action.get("identified_risks", [])),
            "num_missing": len(action.get("missing_clauses", [])),
            "num_contradictions": len(action.get("contradictions", [])),
            "has_assessment": bool(action.get("overall_assessment")),
            "num_recommendations": len(action.get("recommendations", [])),
        },
    }


def main():
    """Run inference on all 3 tasks and produce baseline scores."""

    # Validate configuration
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    tasks = ["task_1_easy", "task_2_medium", "task_3_hard"]
    total_start = time.time()

    # ── [START] ──
    print(f"[START] environment=legal_contract_risk_reviewer model={MODEL_NAME} "
          f"api_base={API_BASE_URL} num_tasks={len(tasks)}", flush=True)

    results = []
    total_score = 0.0

    for task_id in tasks:
        try:
            result = run_task(task_id)
            results.append(result)
            total_score += result["score"]
        except Exception as e:
            print(f"[STEP] task_id={task_id} status=error error={str(e)}", flush=True)
            traceback.print_exc()
            results.append({
                "task_id": task_id,
                "score": 0.0,
                "error": str(e),
            })

    total_duration = round(time.time() - total_start, 2)
    avg_score = round(total_score / len(tasks), 4) if tasks else 0.0

    # ── [END] ──
    scores_summary = " ".join(
        f"{r['task_id']}={r.get('score', 0.0)}" for r in results
    )
    print(f"[END] total_score={round(total_score, 4)} avg_score={avg_score} "
          f"duration={total_duration}s {scores_summary}", flush=True)

    # Print detailed results
    print("\n" + "=" * 60)
    print("BASELINE RESULTS SUMMARY")
    print("=" * 60)
    for r in results:
        status = "✓" if r.get("score", 0) >= 0.5 else "✗"
        print(f"  {status} {r['task_id']}: {r.get('score', 0.0):.4f}")
        if "action_summary" in r:
            s = r["action_summary"]
            print(f"    Risks: {s['num_risks']}, Missing: {s['num_missing']}, "
                  f"Contradictions: {s['num_contradictions']}, "
                  f"Recommendations: {s['num_recommendations']}")
    print(f"\n  Average Score: {avg_score:.4f}")
    print(f"  Total Duration: {total_duration}s")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
