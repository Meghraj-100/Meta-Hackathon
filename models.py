"""
Pydantic models for the Legal Contract Risk Reviewer environment.

Defines typed Action, Observation, and State models for the OpenEnv spec.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContractAction(BaseModel):
    """
    Agent's analysis submission for a contract.

    The agent sends its analysis of the contract including:
    - identified_risks: list of risky clauses/terms found
    - missing_clauses: list of standard clauses that are absent
    - contradictions: list of contradictory clause pairs
    - overall_assessment: summary of the risk analysis
    - recommendations: suggested remediation actions
    """

    identified_risks: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of identified risky clauses. Each dict should have "
        "'clause_reference' (e.g. 'Section 7.2'), 'risk_type' (e.g. 'one-sided liability'), "
        "and 'explanation' keys.",
    )
    missing_clauses: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of missing standard clauses. Each dict should have "
        "'clause_type' (e.g. 'indemnification') and 'importance' (e.g. 'critical') keys.",
    )
    contradictions: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of contradictory clause pairs. Each dict should have "
        "'clause_a', 'clause_b', and 'explanation' keys.",
    )
    overall_assessment: str = Field(
        default="",
        description="Overall risk assessment summary of the contract.",
    )
    recommendations: List[str] = Field(
        default_factory=list,
        description="List of recommended actions to mitigate identified risks.",
    )


class ContractObservation(BaseModel):
    """
    Observation returned to the agent.

    Contains the contract text, task instructions, and feedback after analysis.
    """

    contract_text: str = Field(
        default="",
        description="The full contract text for the agent to analyze.",
    )
    task_id: str = Field(
        default="",
        description="Identifier for the current task (task_1_easy, task_2_medium, task_3_hard).",
    )
    task_description: str = Field(
        default="",
        description="Description of what the agent should look for.",
    )
    task_difficulty: str = Field(
        default="",
        description="Difficulty level: easy, medium, or hard.",
    )
    instructions: str = Field(
        default="",
        description="Detailed instructions for the agent.",
    )
    feedback: str = Field(
        default="",
        description="Feedback from grader after agent submits analysis (empty on reset).",
    )
    score: float = Field(
        default=0.01,
        description="Score from the grader (0.01-0.99), populated after step.",
    )
    done: bool = Field(
        default=False,
        description="Whether the episode is complete.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata.",
    )


class ContractState(BaseModel):
    """
    Episode state tracking.
    """

    episode_id: str = Field(default="", description="Unique episode identifier.")
    step_count: int = Field(default=0, description="Number of steps taken.")
    current_task: str = Field(default="", description="Current task ID.")
    current_difficulty: str = Field(default="", description="Current task difficulty.")
    total_score: float = Field(default=0.01, description="Accumulated score.")
    is_done: bool = Field(default=False, description="Whether episode is complete.")
