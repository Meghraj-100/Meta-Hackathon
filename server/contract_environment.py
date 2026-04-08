"""
Legal Contract Risk Reviewer Environment.

Core environment implementing the OpenEnv spec: reset(), step(), state().
Simulates a legal contract review task where an AI agent must identify
risky terms, missing clauses, and contradictions in legal contracts.
"""

import random
import uuid
from typing import Any, Optional

from models import ContractAction, ContractObservation, ContractState
from server.contracts import get_task, get_all_task_ids
from server.graders import grade_task

try:
    from openenv.core.env_server import Environment
except ImportError:
    # Fallback for standalone development
    class Environment:
        """Minimal base class for standalone development."""
        pass


class ContractRiskEnvironment(Environment):
    """
    Legal Contract Risk Reviewer Environment.

    An AI agent reads contract clauses and must identify risky terms,
    missing standard clauses, and red flags.

    Tasks (3 difficulty levels):
    - task_1_easy: Spot a one-sided liability clause
    - task_2_medium: Identify a missing indemnification clause
    - task_3_hard: Detect contradictions between clauses creating a loophole

    Usage:
        >>> env = ContractRiskEnvironment()
        >>> obs = env.reset(task_id="task_1_easy")
        >>> print(obs.contract_text)  # Read the contract
        >>> action = ContractAction(
        ...     identified_risks=[{"clause_reference": "Section 7", ...}],
        ...     overall_assessment="...",
        ... )
        >>> obs = env.step(action)
        >>> print(obs.score)  # 0.0 - 1.0
    """

    def __init__(self):
        """Initialize the environment."""
        super().__init__()
        self._state = ContractState()
        self._current_task_data = None
        self._episode_done = False
        self._history = []

    def reset(
        self,
        seed: Optional[int] = None,
        task_id: Optional[str] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> ContractObservation:
        """
        Reset the environment for a new episode.

        Args:
            seed: Optional random seed (unused — tasks are deterministic)
            task_id: Which task to load. One of: task_1_easy, task_2_medium, task_3_hard.
                     Defaults to task_1_easy if not specified.
            episode_id: Optional custom episode ID.
            **kwargs: Additional reset options.

        Returns:
            ContractObservation with the contract text and task instructions.
        """
        if task_id is None:
            task_id = kwargs.get("task_id", "task_1_easy")

        # Handle case where task_id comes as part of a dict action
        if isinstance(task_id, dict):
            task_id = task_id.get("task_id", "task_1_easy")

        # Support for seeding
        if seed is not None:
            random.seed(seed)

        task_data = get_task(task_id)
        self._current_task_data = task_data
        self._episode_done = False
        self._history = []

        gt = task_data["ground_truth"]

        self._state = ContractState(
            episode_id=episode_id or str(uuid.uuid4()),
            step_count=0,
            current_task=task_id,
            current_difficulty=gt["difficulty"],
            total_score=0.0,
            is_done=False,
        )

        return ContractObservation(
            contract_text=task_data["contract"],
            task_id=task_id,
            task_description=gt["description"],
            task_difficulty=gt["difficulty"],
            instructions=gt["instructions"],
            feedback="",
            score=0.0,
            done=False,
            metadata={
                "available_tasks": get_all_task_ids(),
                "status": "ready",
                "expected_output_format": {
                    "identified_risks": "list of risk objects",
                    "missing_clauses": "list of missing clause objects",
                    "contradictions": "list of contradictions",
                    "overall_assessment": "string summary",
                    "recommendations": "list of recommendations"
                }
            },
        )

    def step(
        self,
        action: Any,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> ContractObservation:
        """
        Execute a step: receive agent's analysis and grade it.

        Args:
            action: ContractAction or dict with the agent's analysis.
            timeout_s: Optional timeout (unused).
            **kwargs: Additional arguments.

        Returns:
            ContractObservation with feedback and score.
        """
        # Handle case where environment hasn't been reset
        if self._current_task_data is None:
            return ContractObservation(
                feedback="Error: Environment must be reset before stepping. "
                         "Call reset(task_id='task_1_easy') first.",
                done=True,
                metadata={"error": "not_reset"},
            )

        # Handle already-done episodes
        if self._episode_done:
            return ContractObservation(
                feedback="Episode is already complete. Call reset() to start a new episode.",
                score=self._state.total_score,
                done=True,
                metadata={"status": "already_done"},
            )

        # Parse action if it's a dict
        if isinstance(action, dict):
            try:
                action = ContractAction(**action)
            except Exception as e:
                return ContractObservation(
                    feedback=f"Error parsing action: {str(e)}. "
                             "Action must conform to ContractAction schema.",
                    done=False,
                    metadata={"error": "parse_error", "details": str(e)},
                )

        # Ensure action is a ContractAction
        if not isinstance(action, ContractAction):
            try:
                if hasattr(action, "model_dump"):
                    action = ContractAction(**action.model_dump())
                elif hasattr(action, "dict"):
                    action = ContractAction(**action.dict())
                else:
                    action = ContractAction(**dict(action))
            except Exception:
                return ContractObservation(
                    feedback="Error: Action must be a ContractAction or compatible dict.",
                    done=False,
                    metadata={"error": "invalid_action_type"},
                )

        # Anti-Hack: Reject empty actions
        if not action.identified_risks and not action.missing_clauses and not action.contradictions:
            return ContractObservation(
                feedback="Empty analysis provided. Please identify risks or issues.",
                score=0.0,
                done=True,
                metadata={"error": "empty_action"},
            )

        # Track history
        self._history.append(action)

        # Increment step count
        self._state.step_count += 1

        # Grade the action
        task_id = self._state.current_task
        score, feedback = grade_task(task_id, action)

        # Update state
        self._state.total_score = score
        self._state.is_done = True
        self._episode_done = True

        return ContractObservation(
            contract_text=self._current_task_data.get("contract", ""),
            task_id=task_id,
            task_description="",
            task_difficulty=self._state.current_difficulty,
            instructions="",
            feedback=feedback,
            score=score,
            done=True,
            metadata={
                "status": "graded",
                "task_id": task_id,
                "difficulty": self._state.current_difficulty,
                "steps_taken": self._state.step_count,
                "history_length": len(self._history),
            },
        )

    def state(self) -> ContractState:
        """Get the current environment state."""
        return self._state
