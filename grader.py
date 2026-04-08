# grader.py
import re
from pydantic import BaseModel
from typing import Dict, Tuple
from models import ReviewAction

class DeterministicGrader:
    def __init__(self, task_data: Dict):
        self.truth = task_data["ground_truth"]

    def evaluate(self, action: ReviewAction) -> Tuple[float, str]:
        """
        Evaluates the agent's action and returns a tuple: (fractional_reward, feedback_string)
        Maximum score is 1.0.
        """
        score = 0.0
        feedback_notes = []

        # 1. Bug Presence Identification (Max 0.20)
        if action.has_bug == self.truth["has_bug"]:
            score += 0.20
            feedback_notes.append("✅ Correctly identified bug presence.")
        else:
            feedback_notes.append("❌ Failed to identify if a bug exists.")

        # 2. Vulnerability Categorization (Max 0.20)
        if action.bug_category.lower() == self.truth["bug_category"].lower():
            score += 0.20
            feedback_notes.append(f"✅ Correctly categorized as {self.truth['bug_category']}.")
        else:
            feedback_notes.append(f"❌ Incorrect category. Expected {self.truth['bug_category']}.")

        # 3. Spatial Localization (Max 0.10)
        if action.line_number == self.truth["line_number"]:
            score += 0.10
            feedback_notes.append("✅ Correctly pinpointed the exact line number.")
        else:
            feedback_notes.append("❌ Incorrect line number identified.")

        # 4. Severity Assessment (Max 0.10)
        if action.severity.lower() == self.truth["severity"].lower():
            score += 0.10
            feedback_notes.append("✅ Correctly assessed severity.")
        else:
            feedback_notes.append("❌ Incorrect severity assessment.")

        # 5. Diagnostic Quality (Max 0.25 - specific to 'hard' task or tasks with diagnostic_keywords)
        diagnostic_score = 0.0
        if "diagnostic_keywords" in self.truth:
            explanation_lower = action.explanation.lower()
            matched_diag = sum(1 for kw in self.truth["diagnostic_keywords"] if kw in explanation_lower)
            if matched_diag > 0:
                # Give partial credit based on keyword density, capped at 0.25
                diagnostic_score = min(0.25, matched_diag * 0.125) 
                score += diagnostic_score
                feedback_notes.append(f"✅ Diagnostic reasoning matched keywords (+{diagnostic_score:.2f}).")
            else:
                feedback_notes.append("❌ Explanation lacked necessary diagnostic terminology.")
        else:
            # If no specific diagnostic keywords, grant the points if explanation is sufficiently long
            if len(action.explanation.split()) > 10:
                score += 0.25
                feedback_notes.append("✅ Provided sufficient explanation.")

        # 6. Remediation Quality (Max 0.15)
        explanation_lower = action.explanation.lower()
        matched_rem = sum(1 for kw in self.truth["remediation_keywords"] if kw in explanation_lower)
        if matched_rem > 0:
            score += 0.15
            feedback_notes.append("✅ Remediation plan included correct architectural fixes.")
        else:
            feedback_notes.append("❌ Remediation plan lacked correct fix strategies.")

        # Aggregate Feedback
        final_feedback = " | ".join(feedback_notes)
        
        # Ensure score strictly bounded between 0.0 and 1.0 (floating point rounding safety)
        return round(min(max(score, 0.0), 1.0), 2), final_feedback


# --- EXECUTION TEST ---
if __name__ == "__main__":
    from tasks import TASKS_DB # Assuming the dict above is in tasks.py
    
    # 1. Load the hard task (SQL Injection)
    hard_task_data = TASKS_DB["hard"]
    grader = DeterministicGrader(hard_task_data)

    # 2. Simulate a perfectly correct Agent Action
    perfect_agent_action = ReviewAction(
        has_bug=True,
        bug_category="SQLi",
        line_number=7,
        severity="critical",
        explanation="The f-string directly injects untrusted user input without sanitization. Use a parameterized query instead."
    )
    
    # 3. Simulate a partially correct Agent Action (Credit Assignment test)
    flawed_agent_action = ReviewAction(
        has_bug=True,
        bug_category="Auth", # Wrong category
        line_number=7,       # Correct line
        severity="high",     # Wrong severity
        explanation="There is a bug here, we should fix the interpolation." # Missing strong remediation keywords
    )

    # 4. Execute the Evaluator
    perfect_score, perfect_feedback = grader.evaluate(perfect_agent_action)
    flawed_score, flawed_feedback = grader.evaluate(flawed_agent_action)

    print("--- PERFECT AGENT SIMULATION ---")
    print(f"Score: {perfect_score}\nFeedback: {perfect_feedback}\n")
    
    print("--- FLAWED AGENT SIMULATION ---")
    print(f"Score: {flawed_score}\nFeedback: {flawed_feedback}")