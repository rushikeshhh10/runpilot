import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

CONFLUENCE_EMAIL = os.getenv("JIRA_EMAIL")
CONFLUENCE_API_TOKEN = os.getenv("JIRA_API_TOKEN")
CONFLUENCE_BASE_URL = os.getenv("CONFLUENCE_BASE_URL")
CONFLUENCE_SPACE_KEY = os.getenv("CONFLUENCE_SPACE_KEY")

def get_auth_header():
    credentials = f"{CONFLUENCE_EMAIL}:{CONFLUENCE_API_TOKEN}"
    encoded = base64.b64encode(credentials.encode("ascii")).decode("ascii")
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json"
    }

def markdown_to_confluence(markdown_text: str) -> str:
    lines = markdown_text.split("\n")
    html_lines = []
    for line in lines:
        if line.startswith("### "):
            html_lines.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("## "):
            html_lines.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("# "):
            html_lines.append(f"<h1>{line[2:]}</h1>")
        elif line.startswith("- ") or line.startswith("* "):
            html_lines.append(f"<li>{line[2:]}</li>")
        elif line.startswith("```"):
            html_lines.append("<code>")
        elif line.strip() == "":
            html_lines.append("<br/>")
        else:
            cleaned = line.replace("**", "<strong>", 1)
            cleaned = cleaned.replace("**", "</strong>", 1)
            html_lines.append(f"<p>{cleaned}</p>")
    return "\n".join(html_lines)

def create_confluence_page(title: str, markdown_content: str) -> dict:
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content"
    content_html = markdown_to_confluence(markdown_content)
    body = {
        "type": "page",
        "title": title,
        "space": {"key": CONFLUENCE_SPACE_KEY},
        "body": {
            "storage": {
                "value": content_html,
                "representation": "storage"
            }
        }
    }
    response = requests.post(url, json=body, headers=get_auth_header())
    response.raise_for_status()
    result = response.json()
    page_url = f"{CONFLUENCE_BASE_URL}/wiki{result['_links']['webui']}"
    return {
        "page_id": result["id"],
        "title": result["title"],
        "url": page_url
    }

def update_confluence_page(page_id: str, title: str, markdown_content: str) -> dict:
    get_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{page_id}"
    get_response = requests.get(get_url, headers=get_auth_header())
    get_response.raise_for_status()
    current = get_response.json()
    current_version = current["version"]["number"]
    content_html = markdown_to_confluence(markdown_content)
    body = {
        "type": "page",
        "title": title,
        "version": {"number": current_version + 1},
        "body": {
            "storage": {
                "value": content_html,
                "representation": "storage"
            }
        }
    }
    put_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content/{page_id}"
    response = requests.put(put_url, json=body, headers=get_auth_header())
    response.raise_for_status()
    result = response.json()
    page_url = f"{CONFLUENCE_BASE_URL}/wiki{result['_links']['webui']}"
    return {
        "page_id": result["id"],
        "title": result["title"],
        "url": page_url
    }