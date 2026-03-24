import anthropic
import os
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_runbook(ticket: dict) -> str:
    prompt = f"""You are RunPilot, an expert DevOps documentation assistant.

Based on this resolved Jira incident, generate a structured runbook:

Incident ID:  {ticket['key']}
Title:        {ticket['summary']}
Status:       {ticket['status']}
Description:  {ticket['description'] or 'No description provided'}

Generate a runbook with these exact sections:
1. Incident Summary
2. Symptoms to watch for
3. Likely Root Causes
4. Step-by-step Resolution Steps
5. Prevention / Follow-up actions

Be specific, actionable, and format in clean markdown."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text


def generate_all_runbooks(tickets: list) -> list:
    runbooks = []
    for ticket in tickets:
        print(f"Generating runbook for {ticket['key']}...")
        runbook_text = generate_runbook(ticket)
        runbooks.append({
            "ticket_key":   ticket["key"],
            "ticket_title": ticket["summary"],
            "runbook":      runbook_text
        })
    return runbooks