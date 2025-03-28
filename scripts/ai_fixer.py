import os
import json
import requests

OLLAMA_MODEL = "mistral:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Load JSON report
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None

bandit_report = load_json("bandit-report.json")
safety_report = load_json("safety-report.json")

# Function to get AI-powered fix suggestions
def get_fix_suggestion(issue_description):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Security Issue: {issue_description}\nSuggest a secure fix for this vulnerability.",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        return response.json().get("response", "No suggestion generated.")
    except requests.exceptions.RequestException as e:
        print(f"Error contacting Ollama: {e}")
        return "Failed to get a response from AI."

# Generate Fix Suggestions
fix_suggestions = []
seen_issues = set()

# Process Bandit Issues
if bandit_report:
    for issue in bandit_report.get("results", []):
        issue_text = issue.get("issue_text", "Unknown issue")
        if issue_text not in seen_issues:
            fix_suggestion = get_fix_suggestion(issue_text)
            fix_suggestions.append(f"**Issue:** {issue_text}\n**Fix:** {fix_suggestion}")
            seen_issues.add(issue_text)

# Process Safety Issues
if safety_report:
    for vuln in safety_report.get("vulnerabilities", []):
        vuln_text = vuln.get("vulnerability", "Unknown vulnerability")
        if vuln_text not in seen_issues:
            fix_suggestion = get_fix_suggestion(vuln_text)
            fix_suggestions.append(f"**Package Issue:** {vuln_text}\n**Fix:** {fix_suggestion}")
            seen_issues.add(vuln_text)

# Save fix suggestions to file
if fix_suggestions:
    comment_body = "**Automated Security Fix Suggestions**\n\n" + "\n\n".join(fix_suggestions)
    with open("fix_suggestions.txt", "w") as f:
        f.write(comment_body)
    
    print("Fix suggestions saved to fix_suggestions.txt")
else:
    print("No security issues detected.")
