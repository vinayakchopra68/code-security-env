# tasks.py

TASKS_DB = {
    "easy": {
        "difficulty": "easy",
        "description": "Off-by-one Error in array traversal.",
        "code_snippet": """
def get_last_n_items(items, n):
    result = []
    # Bug: Iterating out of bounds
    for i in range(len(items) - n, len(items) + 1): 
        result.append(items[i])
    return result
        """,
        "ground_truth": {
            "has_bug": True,
            "bug_category": "Bounds",
            "line_number": 5,
            "severity": "medium",
            "remediation_keywords": ["len(items)", "remove + 1", "out of bounds", "indexerror"]
        }
    },
    "medium": {
        "difficulty": "medium",
        "description": "Authentication Logic Flaw bypassing access controls.",
        "code_snippet": """
def verify_admin_access(user):
    # Bug: Uses 'or' instead of 'and'
    if user.is_authenticated or user.role == 'admin':
        return True
    return False
        """,
        "ground_truth": {
            "has_bug": True,
            "bug_category": "Auth",
            "line_number": 3,
            "severity": "high",
            "remediation_keywords": ["and", "replace or", "both conditions"]
        }
    },
    "hard": {
        "difficulty": "hard",
        "description": "SQL Injection via String Interpolation.",
        "code_snippet": """
import sqlite3

def get_user_data(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Bug: Direct f-string interpolation exposes SQLi
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchall()
        """,
        "ground_truth": {
            "has_bug": True,
            "bug_category": "SQLi",
            "line_number": 7,
            "severity": "critical",
            "diagnostic_keywords": ["sanitize", "interpolate", "injection", "f-string", "untrusted"],
            "remediation_keywords": ["parameterized query", "prepared statement", "execute(query, (username,))"]
        }
    }
}