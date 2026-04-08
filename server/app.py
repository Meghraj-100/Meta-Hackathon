"""
FastAPI application for the Legal Contract Risk Reviewer Environment.

Exposes the ContractRiskEnvironment over HTTP endpoints for OpenEnv compatibility.

Usage:
    # Development (with auto-reload):
    uvicorn server.app:app --reload --host 0.0.0.0 --port 8000

    # Production:
    uvicorn server.app:app --host 0.0.0.0 --port 8000
"""

import json
import os
import uuid
from typing import Any, Dict, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from models import ContractAction, ContractObservation, ContractState
from server.contract_environment import ContractRiskEnvironment
from server.contracts import get_all_task_ids


# ─── App setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Legal Contract Risk Reviewer",
    description=(
        "An OpenEnv environment where AI agents analyze legal contracts "
        "for risky terms, missing clauses, and legal loopholes."
    ),
    version="0.1.0",
)

# Store environment instances per session
_environments: Dict[str, ContractRiskEnvironment] = {}


def _get_or_create_env(session_id: str = "default") -> ContractRiskEnvironment:
    """Get or create an environment instance for a session."""
    if session_id not in _environments:
        _environments[session_id] = ContractRiskEnvironment()
    return _environments[session_id]


# ─── Request/Response models ─────────────────────────────────────────────────

class ResetRequest(BaseModel):
    task_id: Optional[str] = "task_1_easy"
    seed: Optional[int] = None
    episode_id: Optional[str] = None


class StepRequest(BaseModel):
    identified_risks: list = []
    missing_clauses: list = []
    contradictions: list = []
    overall_assessment: str = ""
    recommendations: list = []


# ─── HTTP Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "environment": "legal_contract_risk_reviewer"}


@app.get("/info")
async def info():
    """Environment information."""
    return {
        "name": "legal_contract_risk_reviewer",
        "version": "0.1.0",
        "description": "Legal Contract Risk Reviewer - AI agents analyze contracts for risks",
        "tasks": get_all_task_ids(),
        "action_schema": ContractAction.model_json_schema(),
        "observation_schema": ContractObservation.model_json_schema(),
    }


@app.post("/reset")
async def reset(request: ResetRequest = ResetRequest()):
    """Reset the environment with a specific task."""
    env = _get_or_create_env()
    obs = env.reset(
        task_id=request.task_id,
        seed=request.seed,
        episode_id=request.episode_id,
    )
    return {
        "observation": obs.model_dump(),
        "reward": 0.0,
        "done": False,
        "info": {"task_id": request.task_id},
    }


@app.post("/step")
async def step(request: StepRequest):
    """Submit agent analysis and receive graded feedback."""
    env = _get_or_create_env()
    action = ContractAction(
        identified_risks=request.identified_risks,
        missing_clauses=request.missing_clauses,
        contradictions=request.contradictions,
        overall_assessment=request.overall_assessment,
        recommendations=request.recommendations,
    )
    obs = env.step(action)
    return {
        "observation": obs.model_dump(),
        "reward": obs.score,
        "done": obs.done,
        "info": obs.metadata,
    }


@app.get("/state")
async def state():
    """Get current environment state."""
    env = _get_or_create_env()
    return env.state().model_dump()


@app.get("/tasks")
async def list_tasks():
    """List all available tasks."""
    return {"tasks": get_all_task_ids()}


# ─── WebSocket Endpoint (for OpenEnv client compatibility) ───────────────────

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for OpenEnv client communication."""
    await websocket.accept()
    session_id = str(uuid.uuid4())
    env = _get_or_create_env(session_id)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            msg_type = message.get("type", "")

            if msg_type == "reset":
                task_id = message.get("task_id", "task_1_easy")
                obs = env.reset(task_id=task_id)
                response = {
                    "type": "reset_result",
                    "observation": obs.model_dump(),
                    "reward": 0.0,
                    "done": False,
                }
            elif msg_type == "step":
                action_data = message.get("action", {})
                action = ContractAction(**action_data)
                obs = env.step(action)
                response = {
                    "type": "step_result",
                    "observation": obs.model_dump(),
                    "reward": obs.score,
                    "done": obs.done,
                }
            elif msg_type == "state":
                response = {
                    "type": "state_result",
                    "state": env.state().model_dump(),
                }
            else:
                response = {
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                }

            await websocket.send_text(json.dumps(response))

    except WebSocketDisconnect:
        if session_id in _environments:
            del _environments[session_id]
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": str(e),
            }))
        except Exception:
            pass
        if session_id in _environments:
            del _environments[session_id]


# ─── Gradio Web Interface (optional) ────────────────────────────────────────

if os.environ.get("ENABLE_WEB_INTERFACE", "").lower() in ("true", "1", "yes"):
    try:
        import gradio as gr

        def gradio_reset(task_id: str) -> str:
            env = _get_or_create_env("gradio")
            obs = env.reset(task_id=task_id)
            return json.dumps(obs.model_dump(), indent=2)

        def gradio_step(
            risks_json: str,
            missing_json: str,
            contradictions_json: str,
            assessment: str,
            recommendations: str,
        ) -> str:
            env = _get_or_create_env("gradio")
            try:
                risks = json.loads(risks_json) if risks_json.strip() else []
                missing = json.loads(missing_json) if missing_json.strip() else []
                contras = json.loads(contradictions_json) if contradictions_json.strip() else []
                recs = [r.strip() for r in recommendations.split("\n") if r.strip()]
            except json.JSONDecodeError as e:
                return f"JSON parse error: {e}"

            action = ContractAction(
                identified_risks=risks,
                missing_clauses=missing,
                contradictions=contras,
                overall_assessment=assessment,
                recommendations=recs,
            )
            obs = env.step(action)
            return json.dumps(obs.model_dump(), indent=2)

        def gradio_state() -> str:
            env = _get_or_create_env("gradio")
            return json.dumps(env.state().model_dump(), indent=2)

        with gr.Blocks(title="Legal Contract Risk Reviewer") as demo:
            gr.Markdown("# 📜 Legal Contract Risk Reviewer")
            gr.Markdown("An OpenEnv environment for AI agents to analyze legal contracts.")

            with gr.Tab("Reset"):
                task_dropdown = gr.Dropdown(
                    choices=get_all_task_ids(),
                    value="task_1_easy",
                    label="Select Task",
                )
                reset_btn = gr.Button("Reset Environment", variant="primary")
                reset_output = gr.Textbox(label="Observation", lines=20)
                reset_btn.click(gradio_reset, inputs=[task_dropdown], outputs=[reset_output])

            with gr.Tab("Step"):
                risks_input = gr.Textbox(
                    label="Identified Risks (JSON array)",
                    placeholder='[{"clause_reference": "Section 7", "risk_type": "one-sided", "explanation": "..."}]',
                    lines=3,
                )
                missing_input = gr.Textbox(
                    label="Missing Clauses (JSON array)",
                    placeholder='[{"clause_type": "indemnification", "importance": "critical"}]',
                    lines=3,
                )
                contra_input = gr.Textbox(
                    label="Contradictions (JSON array)",
                    placeholder='[{"clause_a": "Section 4", "clause_b": "Section 11", "explanation": "..."}]',
                    lines=3,
                )
                assessment_input = gr.Textbox(
                    label="Overall Assessment",
                    lines=3,
                )
                recs_input = gr.Textbox(
                    label="Recommendations (one per line)",
                    lines=3,
                )
                step_btn = gr.Button("Submit Analysis", variant="primary")
                step_output = gr.Textbox(label="Grading Result", lines=15)
                step_btn.click(
                    gradio_step,
                    inputs=[risks_input, missing_input, contra_input, assessment_input, recs_input],
                    outputs=[step_output],
                )

            with gr.Tab("State"):
                state_btn = gr.Button("Get State")
                state_output = gr.Textbox(label="Current State", lines=10)
                state_btn.click(gradio_state, outputs=[state_output])

        app = gr.mount_gradio_app(app, demo, path="/web")
    except ImportError:
        pass  # Gradio not installed, skip web interface


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    """Entry point for direct execution."""
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
