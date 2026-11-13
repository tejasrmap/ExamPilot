import subprocess
import requests
import json

def get_token():
    input_data = 'protocol=https\nhost=github.com\n\n'
    p = subprocess.run(['git', 'credential', 'fill'], input=input_data, capture_output=True, text=True)
    creds = dict(line.split('=', 1) for line in p.stdout.strip().splitlines() if '=' in line)
    return creds.get('password')

def create_and_push():
    token = get_token()
    if not token:
        print("Error: Could not retrieve GitHub token from Git credential manager.")
        return False

    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    print("Creating GitHub repository 'ExamPilot' for user tejasrmap...")
    payload = {
        'name': 'ExamPilot',
        'description': 'ExamPilot - Offline-First Local AI MCQ Practice Assistant (GT InnoX LLP)',
        'private': False,
        'has_issues': True,
        'has_wiki': True
    }

    res = requests.post('https://api.github.com/user/repos', headers=headers, json=payload)
    if res.status_code == 201:
        print("GitHub repository created successfully: https://github.com/tejasrmap/ExamPilot")
    elif res.status_code == 422:
        print("Repository might already exist or name taken:", res.json().get('message'))
    else:
        print(f"Failed to create repo ({res.status_code}):", res.text)
        return False

    remote_url = f"https://{token}@github.com/tejasrmap/ExamPilot.git"
    clean_url = "https://github.com/tejasrmap/ExamPilot.git"

    # Configure git remote
    subprocess.run(["git", "remote", "remove", "origin"], capture_output=True)
    subprocess.run(["git", "remote", "add", "origin", clean_url], capture_output=True)

    print("\nPushing 200 commits to https://github.com/tejasrmap/ExamPilot (branch: main)...")
    push_res = subprocess.run(["git", "push", "-u", remote_url, "main"], capture_output=True, text=True)
    if push_res.returncode == 0:
        print("Successfully pushed 200 commits to remote repository!")
        print(push_res.stdout)
        print(push_res.stderr)
        return True
    else:
        print("Push error:", push_res.stderr)
        return False

if __name__ == "__main__":
    create_and_push()

