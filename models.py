# models.py
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

# --- ENUMERATIONS FOR STRICT VALIDATION ---
class BugCategory(str, Enum):
    SQLI = "SQLi"
    AUTH = "Auth"
    BOUNDS = "Bounds"
    NONE = "None"

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"

# --- 1. THE ACTION MODEL (Agent -> Environment) ---
class ReviewAction(BaseModel):
    has_bug: bool = Field(
        ..., description="True if a vulnerability exists in the snippet."
    )
    bug_category: BugCategory = Field(
        ..., description="The category of the flaw."
    )
    line_number: int = Field(
        ..., description="The exact integer line number where the flaw originates."
    )
    severity: Severity = Field(
        ..., description="The threat level of the vulnerability."
    )
    explanation: str = Field(
        ..., description="Diagnostic reasoning and proposed remediation instructions."
    )

# --- 2. THE OBSERVATION MODEL (Environment -> Agent) ---
class ReviewObservation(BaseModel):
    code_snippet: str = Field(
        ..., description="The target source code to be analyzed."
    )
    feedback: str = Field(
        ..., description="Feedback from the grader on the previous action."
    )
    current_score: float = Field(
        ..., description="Accumulated fractional reward (0.0 to 1.0)."
    )
    is_terminal: bool = Field(
        ..., description="True if the episode has concluded."
    )

# --- 3. THE STATE MODEL (Internal Tracking / External Orchestration) ---
class ReviewState(BaseModel):
    episode_id: str = Field(
        ..., description="Unique identifier for the current run."
    )
    step_count: int = Field(
        ..., description="Number of actions submitted in the current episode."
    )
    active_difficulty: str = Field(
        ..., description="Current difficulty tier (easy, medium, hard)."
    )

# --- 4. STEP RESULT PRIMITIVE (Aggregates the step output) ---
class StepResult(BaseModel):
    observation: ReviewObservation
    reward: float
    done: bool
    info: dict = Field(default_factory=dict)