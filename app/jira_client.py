import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")

def get_auth_header():
    credentials = f"{JIRA_EMAIL}:{JIRA_API_TOKEN}"
    encoded = base64.b64encode(credentials.encode("ascii")).decode("ascii")
    return {"Authorization": f"Basic {encoded}", "Content-Type": "application/json"}

def fetch_done_tickets(project_key: str, max_results: int = 10):
    url = f"{JIRA_BASE_URL}/rest/api/3/search/jql"
    body = {
        "jql": f"project = {project_key} AND status = Done ORDER BY updated DESC",
        "maxResults": max_results,
        "fields": ["summary", "status", "description", "comment"]
    }
    response = requests.post(url, json=body, headers=get_auth_header())
    response.raise_for_status()
    issues = response.json().get("issues", [])
    tickets = []
    for issue in issues:
        fields = issue.get("fields", {})
        desc = fields.get("description")
        description_text = ""
        if desc and isinstance(desc, dict):
            for block in desc.get("content", []):
                for inline in block.get("content", []):
                    if inline.get("type") == "text":
                        description_text += inline.get("text", "")
        tickets.append({
            "key": issue["key"],
            "summary": fields.get("summary", ""),
            "status": fields.get("status", {}).get("name", ""),
            "description": description_text
        })
    return tickets