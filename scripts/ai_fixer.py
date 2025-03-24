import os
import json
import requests
from github import Github  # GitHub API to post comments

OLLAMA_MODEL = "mistral:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"

# Load security reports
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return None

bandit_report = load_json("bandit-report.json")
safety_report = load_json("safety-report.json")

# Extract PR number correctly
def get_pr_number():
    github_event_path = os.getenv("GITHUB_EVENT_PATH")
    if github_event_path and os.path.exists(github_event_path):
        with open(github_event_path, "r") as f:
            event_data = json.load(f)
            return event_data.get("pull_request", {}).get("number")
    return None

# Ensure required GitHub environment variables exist
github_token = os.getenv("GITHUB_TOKEN")
repo_name = os.getenv("GITHUB_REPOSITORY")

if not github_token or not repo_name:
    print("❌ Error: Missing GitHub environment variables (GITHUB_TOKEN or GITHUB_REPOSITORY).")
    exit(1)

pr_number = get_pr_number()
if pr_number is None:
    print("❌ Error: Unable to extract PR number.")
    exit(1)

# Function to get AI-powered fix suggestions
def get_fix_suggestion(issue_description):
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": f"Security Issue: {issue_description}\nSuggest a secure fix for this vulnerability.",
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()  # Raise an error for bad responses
        return response.json().get("response", "No suggestion generated.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error contacting Ollama: {e}")
        return "Failed to get a response from AI."

# Generate Fix Suggestions
fix_suggestions = []
seen_issues = set()  # Avoid duplicate suggestions

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

# Post Fix Suggestions as GitHub Comments
if fix_suggestions:
    try:
        g = Github(github_token)
        repo = g.get_repo(repo_name)
        pr = repo.get_pull(pr_number)

        comment_body = "**🔒 Automated Security Fix Suggestions**\n\n" + "\n\n".join(fix_suggestions)
        pr.create_issue_comment(comment_body)

        print("✅ Fix suggestions have been posted to the PR.")
    except Exception as e:
        print(f"❌ Error posting to GitHub PR: {e}")
else:
    print("✅ No security issues detected. No comment posted.")
