# main.py
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import ValidationError

from models import ReviewAction, ReviewObservation, ReviewState, StepResult
from tasks import TASKS_DB
from grader import DeterministicGrader

# --- 1. THE CORE ENVIRONMENT STATE MACHINE ---
class CodeSecurityEnv:
    def __init__(self):
        self.episode_id = None
        self.step_count = 0
        self.max_steps = 5  # Prevent infinite loops
        self.current_score = 0.0
        self.current_task_id = None
        self.current_task = None
        self.grader = None

    def reset(self, difficulty: str = "easy") -> ReviewObservation:
        """Initializes a new episode and loads the requested task."""
        if difficulty not in TASKS_DB:
            raise ValueError(f"Invalid difficulty. Choose from {list(TASKS_DB.keys())}")
            
        self.episode_id = str(uuid.uuid4())
        self.step_count = 0
        self.current_score = 0.0
        self.current_task_id = difficulty
        self.current_task = TASKS_DB[difficulty]
        self.grader = DeterministicGrader(self.current_task)

        return ReviewObservation(
            code_snippet=self.current_task["code_snippet"],
            feedback="Environment initialized. Awaiting your analysis.",
            current_score=self.current_score,
            is_terminal=False
        )

    def step(self, action: ReviewAction) -> StepResult:
        """Processes the agent's action, calculates reward, and advances state."""
        if self.episode_id is None:
            raise RuntimeError("Environment has not been reset. Call reset() first.")
            
        self.step_count += 1
        
        # Pass the rigorously validated Pydantic Action to our Grader
        reward, feedback = self.grader.evaluate(action)
        self.current_score += reward

        # Check for termination (Did they solve it, or did they run out of time?)
        done = False
        if reward >= 1.0:
            done = True
            feedback += " | 🎯 Task Complete! Maximum score achieved."
        elif self.step_count >= self.max_steps:
            done = True
            feedback += " | 🛑 Max steps reached. Episode terminated."

        # Construct the new observation
        observation = ReviewObservation(
            code_snippet=self.current_task["code_snippet"],
            feedback=feedback,
            current_score=self.current_score,
            is_terminal=done
        )

        return StepResult(
            observation=observation,
            reward=reward,
            done=done,
            info={"step_count": self.step_count, "difficulty": self.current_task_id}
        )

    def state(self) -> ReviewState:
        """Returns the internal telemetry of the environment."""
        return ReviewState(
            episode_id=self.episode_id or "Not Started",
            step_count=self.step_count,
            active_difficulty=self.current_task_id or "None"
        )


# --- 2. THE FASTAPI NETWORK WRAPPER ---
app = FastAPI(title="OpenEnv: Code Security Reviewer")
env = CodeSecurityEnv()

@app.post("/reset", response_model=ReviewObservation)
async def api_reset(difficulty: str = "easy"):
    try:
        return env.reset(difficulty=difficulty)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/step", response_model=StepResult)
async def api_step(action: ReviewAction):
    try:
        return env.step(action)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state", response_model=ReviewState)
async def api_state():
    return env.state()

# Run the server locally if this script is executed directly
if __name__ == "__main__":
    print("🚀 Booting up the OpenEnv Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)