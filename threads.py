#!/usr/bin/env python3
from PyQt5.QtCore import QThread, pyqtSignal
from github_api import GitHubAPI

class ActionThread(QThread):
    """Thread for performing GitHub API actions on multiple items."""
    progress = pyqtSignal(int, str)
    done = pyqtSignal(bool, str)

    def __init__(self, api, operation, items):
        super().__init__()
        self.api = api
        self.operation = operation
        self.items = items

    def run(self):
        total = len(self.items)
        success = 0
        for i, elem in enumerate(self.items, start=1):
            msg = ""
            ok = False
            if self.operation == 'follow':
                ok, msg = self.api.follow_user(elem)
            elif self.operation == 'unfollow':
                ok, msg = self.api.unfollow_user(elem)
            elif self.operation == 'star':
                parts = elem.split('/')
                if len(parts) >= 2:
                    owner, repo = parts[-2], parts[-1]
                    ok, msg = self.api.star_repo(owner, repo)
            elif self.operation == 'unstar':
                parts = elem.split('/')
                if len(parts) >= 2:
                    owner, repo = parts[-2], parts[-1]
                    ok, msg = self.api.unstar_repo(owner, repo)
            self.progress.emit(int(i / total * 100), msg)
            if ok:
                success += 1
        self.done.emit(True, f"Completed {success}/{total} operations")


class MultiAccountThread(QThread):
    """Thread for performing GitHub API actions on multiple items with multiple accounts."""
    progress = pyqtSignal(int, str)
    done = pyqtSignal(bool, str)

    def __init__(self, tokens, operation, items):
        super().__init__()
        self.tokens = tokens
        self.operation = operation
        self.items = items

    def run(self):
        total_ops = len(self.tokens) * len(self.items)
        done_count = 0
        success = 0
        for token in self.tokens:
            api = GitHubAPI(token)
            for elem in self.items:
                msg = ""
                ok = False
                if self.operation == 'follow':
                    ok, msg = api.follow_user(elem)
                elif self.operation == 'unfollow':
                    ok, msg = api.unfollow_user(elem)
                elif self.operation == 'star':
                    parts = elem.split('/')
                    if len(parts) >= 2:
                        owner, repo = parts[-2], parts[-1]
                        ok, msg = api.star_repo(owner, repo)
                elif self.operation == 'unstar':
                    parts = elem.split('/')
                    if len(parts) >= 2:
                        owner, repo = parts[-2], parts[-1]
                        ok, msg = api.unstar_repo(owner, repo)
                done_count += 1
                self.progress.emit(int(done_count / total_ops * 100), msg)
                if ok:
                    success += 1
        self.done.emit(True, f"Completed {success}/{total_ops} operations")