***** GIT TRACKER APP******
APPS FUNCTION: will monitor error in code from the github name and the token 
- added an authentication page with a database 
-debuggin still on progress 


**requirement**
-github token
-gitub account to access the token
-github API
-github repository for the tracking to take place



































































































import requests

# getting  the github requrements
GITHUB_TOKEN = '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'
GITHUB_OWNER = 'networkchaos'
GITHUB_REPO = 'git-tracker'

def get_repository_issues(owner, repo, token):
    url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    headers = {
        'Authorization': f'token {token}'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# main function 
def main():
    issues = get_repository_issues(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN)
    if issues:
        print(f"Issues for {GITHUB_OWNER}/{GITHUB_REPO}:\n")
        for issue in issues:
            print(f"Title: {issue['title']}")
            print(f"URL: {issue['html_url']}\n")
    else:
        print("Failed to fetch issues sir.")

if __name__ == "__main__":
    main()