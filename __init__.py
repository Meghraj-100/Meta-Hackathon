"""
Legal Contract Risk Reviewer — OpenEnv Environment.

An AI agent reads contract clauses and must identify risky terms,
missing standard clauses, and red flags.

Tasks:
- task_1_easy: Spot a one-sided liability clause
- task_2_medium: Identify a missing indemnification clause
- task_3_hard: Detect contradictions creating a legal loophole
"""

from models import ContractAction, ContractObservation, ContractState
from client import ContractRiskEnv

__all__ = [
    "ContractAction",
    "ContractObservation",
    "ContractState",
    "ContractRiskEnv",
]
