"""
Client for the Legal Contract Risk Reviewer Environment.

Provides a Python client for interacting with the environment server
via HTTP/WebSocket using the OpenEnv client protocol.
"""

try:
    from openenv.core import EnvClient, StepResult
    from models import ContractAction, ContractObservation, ContractState

    class ContractRiskEnv(EnvClient[ContractAction, ContractObservation, ContractState]):
        """
        Client for the Legal Contract Risk Reviewer Environment.

        Example:
            >>> with ContractRiskEnv(base_url="http://localhost:8000").sync() as env:
            ...     result = env.reset(task_id="task_1_easy")
            ...     print(result.observation.contract_text)
            ...     result = env.step(ContractAction(
            ...         identified_risks=[{"clause_reference": "Section 7", ...}],
            ...         overall_assessment="...",
            ...     ))
            ...     print(result.reward)
        """

        def _step_payload(self, action: ContractAction) -> dict:
            return action.model_dump()

        def _parse_result(self, payload: dict) -> StepResult[ContractObservation]:
            obs = ContractObservation(**payload["observation"])
            return StepResult(
                observation=obs,
                reward=payload.get("reward", 0.0),
                done=payload.get("done", False),
            )

        def _parse_state(self, payload: dict) -> ContractState:
            return ContractState(**payload)

except ImportError:
    # Fallback when openenv-core is not installed
    class ContractRiskEnv:
        """Placeholder client — install openenv-core for full client functionality."""

        def __init__(self, *args, **kwargs):
            raise ImportError(
                "openenv-core is required for the client. "
                "Install it with: pip install openenv-core"
            )
