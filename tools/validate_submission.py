"""Read GitHub PR metadata; never run code from a submission."""
import base64
import json
import os
import re
import urllib.parse
import urllib.request


def validate_paths(files):
    if not files:
        raise ValueError("No changed files found.")
    teams = set()
    for item in files:
        path = item["filename"]
        match = re.match(r"^teams/(team-(?:0[1-9]|1[0-9]|2[0-4]))/.+", path)
        if not match:
            raise ValueError(f"Change is outside an assigned team folder: {path}")
        teams.add(match.group(1))
        previous = item.get("previous_filename")
        if previous and not previous.startswith(f"teams/{match.group(1)}/"):
            raise ValueError(f"Rename crosses team/root boundaries: {previous} -> {path}")
    if len(teams) != 1:
        raise ValueError("Change only ONE assigned team folder per pull request.")
    team = next(iter(teams))
    readme = f"teams/{team}/README.md"
    if not any(x["filename"] == readme and x.get("status") != "removed" for x in files):
        raise ValueError(f"Include your completed {readme} in this pull request.")
    return team, readme


def api(path):
    request = urllib.request.Request(
        "https://api.github.com/" + path,
        headers={
            "Authorization": "Bearer " + os.environ["GH_TOKEN"],
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "NLP-Hub-Submission-Check",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    number = int(os.environ["PR_NUMBER"])
    pr = api(f"repos/{repo}/pulls/{number}")
    if pr["changed_files"] >= 3000:
        raise ValueError("Too many files to validate safely. Remove dependencies/caches and contact organisers.")
    files = []
    page = 1
    while True:
        batch = api(f"repos/{repo}/pulls/{number}/files?per_page=100&page={page}")
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    team, readme = validate_paths(files)
    head_repo = pr["head"]["repo"]["full_name"]
    sha = pr["head"]["sha"]
    ref = urllib.parse.quote(sha, safe="")
    file = api(f"repos/{head_repo}/contents/{readme}?ref={ref}")
    if file.get("type") != "file" or file.get("encoding") != "base64":
        raise ValueError("The team README must be a regular Markdown file.")
    text = base64.b64decode(file["content"]).decode("utf-8")
    if "PENDING SUBMISSION" in text:
        raise ValueError("Replace the placeholder README with your completed team README.")
    if not re.search(r"https://[^\s)<>]+", text):
        raise ValueError("Add accessible evidence links, including your presentation/demo video, to the README.")
    for item in files:
        if item.get("status") == "removed":
            continue
        metadata = api(f"repos/{head_repo}/contents/{urllib.parse.quote(item['filename'], safe='/')}?ref={ref}")
        if metadata.get("type") != "file":
            raise ValueError(f"Use ordinary files, not symlinks/submodules: {item['filename']}")
        if metadata.get("size", 0) > 50 * 1024 * 1024:
            raise ValueError(f"Use an external artefact link for files larger than 50 MiB: {item['filename']}")
    print(f"Folder and README checks passed for {team}. Organisers must still review identity, required materials, video access and quality.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        raise SystemExit(str(exc)) from None
