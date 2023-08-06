import requests

def fetch_pulls(repo, headers):
    pulls = []
    page = 1
    while True:
        response = requests.get(f"https://api.github.com/repos/{repo}/pulls?state=closed&page={page}&per_page=100", headers=headers)
        data = response.json()
        if not data:
            break
        pulls.extend(data)
        page += 1
    return pulls

