#!/usr/bin/env python3
import base64
import requests
import os

class GitHubAPI:
    """GitHub API wrapper with comprehensive functionality."""
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def validate_token(self):
        """Validate the token by fetching the user profile."""
        try:
            r = requests.get("https://api.github.com/user", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}: Token invalid"
        except Exception as e:
            return False, str(e)

    def get_user_info(self, username):
        """Get information about a GitHub user."""
        try:
            r = requests.get(f"https://api.github.com/users/{username}", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def search_users(self, query):
        """Search for GitHub users by username."""
        try:
            r = requests.get(f"https://api.github.com/search/users?q={query}", headers=self.headers)
            if r.status_code == 200:
                return True, r.json().get('items', [])
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def follow_user(self, user):
        """Follow a GitHub user."""
        try:
            r = requests.put(f"https://api.github.com/user/following/{user}", headers=self.headers)
            return (r.status_code == 204), (f"Followed {user}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def unfollow_user(self, user):
        """Unfollow a GitHub user."""
        try:
            r = requests.delete(f"https://api.github.com/user/following/{user}", headers=self.headers)
            return (r.status_code == 204), (f"Unfollowed {user}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def star_repo(self, owner, repo):
        """Star a GitHub repository."""
        try:
            r = requests.put(f"https://api.github.com/user/starred/{owner}/{repo}", headers=self.headers)
            return (r.status_code == 204), (f"Starred {owner}/{repo}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def unstar_repo(self, owner, repo):
        """Unstar a GitHub repository."""
        try:
            r = requests.delete(f"https://api.github.com/user/starred/{owner}/{repo}", headers=self.headers)
            return (r.status_code == 204), (f"Unstarred {owner}/{repo}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def get_following(self):
        """Get list of users being followed."""
        try:
            r = requests.get("https://api.github.com/user/following", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def get_repos(self):
        """Get list of user repositories."""
        try:
            r = requests.get("https://api.github.com/user/repos?per_page=100", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def create_repo(self, name, desc, private):
        """Create a new repository."""
        data = {"name": name, "description": desc, "private": private}
        try:
            r = requests.post("https://api.github.com/user/repos", headers=self.headers, json=data)
            if r.status_code == 201:
                return True, r.json()
            return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        except Exception as e:
            return False, str(e)

    def upload_file(self, owner, repo, path, content):
        """Upload a file to a repository."""
        try:
            enc = base64.b64encode(content).decode()
            fn = os.path.basename(path)
            up_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{fn}"
            data = {"message": f"Add {fn}", "content": enc}
            r = requests.put(up_url, headers=self.headers, json=data)
            if r.status_code in [200, 201]:
                return True, f"Uploaded {fn}"
            return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        except Exception as e:
            return False, str(e)

    def get_contents(self, owner, repo, path=""):
        """Get contents of path within the repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        try:
            r = requests.get(url, headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        except Exception as e:
            return False, str(e)

    def update_file(self, owner, repo, path, message, new_content, sha):
        """Update an existing file in a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        data = {
            "message": message,
            "content": base64.b64encode(new_content.encode()).decode(),
            "sha": sha
        }
        try:
            r = requests.put(url, headers=self.headers, json=data)
            if r.status_code in [200, 201]:
                return True, r.json()
            return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        except Exception as e:
            return False, str(e)

    def delete_file(self, owner, repo, path, message, sha):
        """Delete a file in a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        data = {"message": message, "sha": sha}
        try:
            r = requests.delete(url, headers=self.headers, json=data)
            if r.status_code == 200:
                return True, f"File '{path}' deleted"
            return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        except Exception as e:
            return False, str(e)

    def enable_wiki(self, owner, repo):
        """Enable wiki for a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = {"has_wiki": True}
        r = requests.patch(url, headers=self.headers, json=data)
        if r.status_code == 200:
            return True, "Wiki enabled."
        return False, f"Error {r.status_code}: {r.json().get('message', '')}"

    def disable_wiki(self, owner, repo):
        """Disable wiki for a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = {"has_wiki": False}
        r = requests.patch(url, headers=self.headers, json=data)
        if r.status_code == 200:
            return True, "Wiki disabled."
        return False, f"Error {r.status_code}: {r.json().get('message', '')}"

    def create_branch(self, owner, repo, branch_name, base_sha):
        """Create a new branch in a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        r = requests.post(url, headers=self.headers, json=data)
        if r.status_code == 201:
            return True, f"Branch '{branch_name}' created."
        return False, f"Error {r.status_code}: {r.json().get('message', '')}"

    def delete_branch(self, owner, repo, branch_name):
        """Delete a branch in a repository."""
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return True, f"Branch '{branch_name}' deleted."
        return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        
    def update_profile(self, name, bio, company, location, blog):
        """Update user profile information."""
        url = "https://api.github.com/user"
        data = {
            "name": name,
            "bio": bio,
            "company": company,
            "location": location,
            "blog": blog
        }
        try:
            r = requests.patch(url, headers=self.headers, json=data)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}: {r.json().get('message', '')}"
        except Exception as e:
            return False, str(e)