# 🛡️ OpenEnv: Automated Code Security Review

An OpenEnv-compliant, production-grade reinforcement learning environment that simulates a real-world cybersecurity auditing workflow. 

## 📖 Motivation
Historically, reinforcement learning agents have been benchmarked on synthetic arcade games or stateless toy problems. This environment abandons synthetic games to simulate a complex, real-world task: **Automated Code Security Review**. Agents act as cybersecurity auditors, tasked with analyzing source code, identifying exact vulnerability lines, categorizing threats, and proposing architectural remediations using a strict JSON schema.

## 🧠 The Task Curriculum
The environment features a deterministically graded, escalating curriculum consisting of three distinct tasks. The grader provides dense, fractional rewards (0.0 to 1.0) based on partial progress, eliminating the sparse-reward stagnation problem.

* **Easy (Off-by-One Error):** Tests the agent's ability to identify basic array traversal bounds errors.
* **Medium (Authentication Flaw):** Tests the agent's ability to spot logical operator flaws (`OR` vs `AND`) that bypass access controls.
* **Hard (SQL Injection):** Tests the agent's ability to detect direct f-string interpolation of unsanitized user inputs into database queries, requiring specific remediation strategies (parameterized queries).

## 🗄️ State and Action Spaces
This environment strictly adheres to the OpenEnv specification by utilizing Pydantic models for absolute type-safe boundaries.

### **Action Space (Agent -> Environment)**
Agents must submit actions conforming to the following JSON schema:
* `has_bug` (bool): Does a vulnerability exist?
* `bug_category` (str): Enum (`SQLi`, `Auth`, `Bounds`, `None`).
* `line_number` (int): The exact integer line of the flaw.
* `severity` (str): Enum (`critical`, `high`, `medium`, `low`, `none`).
* `explanation` (str): Diagnostic reasoning and remediation instructions.

### **Observation Space (Environment -> Agent)**
Upon stepping, the environment returns:
* `code_snippet` (str): The target source code.
* `feedback` (str): Constructive textual feedback from the deterministic grader.
* `current_score` (float): Accumulated fractional reward (0.0 to 1.0).
* `is_terminal` (bool): True if the agent succeeded or exhausted the step limit.

## 🚀 Setup and Usage Instructions

### **Option 1: Connect to the Live Hugging Face Space**
The environment is securely containerized and hosted live. You can connect your training scripts directly to the cloud instance:
```python
# In your inference script
ENV_URL = "https://vinayakchopra68-code-security-env.hf.space"
requests.post(f"{ENV_URL}/reset?difficulty=hard")