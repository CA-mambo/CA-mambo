import requests
import os
import re
import sys

# Configuration
OWNER = "CA-mambo"
REPO = "CA-mambo"
BRANCH = "main"
README_FILE = "README.md"
TOKEN = os.environ.get("GITHUB_TOKEN")

if not TOKEN:
    print("Error: GITHUB_TOKEN environment variable is required.")
    sys.exit(1)

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def fetch_repos():
    """Fetch public, non-fork repositories for the user."""
    url = f"https://api.github.com/users/{OWNER}/repos?per_page=100&type=owner&sort=updated&direction=desc"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repos: {e}")
        return []

def generate_table(repos):
    """Generate Markdown table for public, non-fork repos."""
    # Filter: Not private AND Not fork
    public_repos = [r for r in repos if not r.get("private") and not r.get("fork")]
    
    if not public_repos:
        return "*(No public projects found)*"

    table_lines = [
        "| Project | Description | Language |",
        "| :--- | :--- | :--- |"
    ]
    
    for repo in public_repos[:10]: # Limit to top 10
        name = f"[**{repo['name']}**]({repo['html_url']})"
        desc = (repo.get("description") or "No description").replace("|", "\\|")
        lang = repo.get("language") or "Other"
        table_lines.append(f"| {name} | {desc} | {lang} |")
        
    return "\n".join(table_lines)

def update_readme(new_table):
    """Update README.md with the new table."""
    # Fetch current README content from GitHub
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{README_FILE}?ref={BRANCH}"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        content_info = response.json()
        sha = content_info["sha"]
        
        import base64
        current_content = base64.b64decode(content_info["content"]).decode("utf-8")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching README: {e}")
        return

    # Define markers for injection
    START_MARKER = "<!-- PROJECTS-LIST-START -->"
    END_MARKER = "<!-- PROJECTS-LIST-END -->"
    
    # Check if markers exist
    if START_MARKER not in current_content or END_MARKER not in current_content:
        print("Markers not found in README.md. Please add them first.")
        return

    # Replace content between markers
    regex = re.compile(rf"({START_MARKER}\n).*?(\n{END_MARKER})", re.DOTALL)
    updated_content = regex.sub(f"\\1{new_table}\\2", current_content)
    
    if updated_content == current_content:
        print("No changes detected in projects list.")
        return

    # Push update back to GitHub
    update_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{README_FILE}"
    payload = {
        "message": "chore: auto-update public projects list",
        "content": base64.b64encode(updated_content.encode("utf-8")).decode("utf-8"),
        "branch": BRANCH,
        "sha": sha
    }
    
    try:
        update_response = requests.put(update_url, headers=HEADERS, json=payload)
        update_response.raise_for_status()
        print("README.md updated successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error updating README: {e}")

if __name__ == "__main__":
    print("Fetching repositories...")
    repos = fetch_repos()
    print(f"Found {len(repos)} repositories.")
    
    print("Generating table...")
    table = generate_table(repos)
    
    print("Updating README...")
    update_readme(table)
