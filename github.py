#!/usr/bin/env python3
import sys
import os
import base64
import requests
import markdown
import re
from dotenv import load_dotenv, set_key, find_dotenv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QDialog, QVBoxLayout, QHBoxLayout,
    QFormLayout, QDialogButtonBox, QWidget, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QCheckBox, QProgressBar, QTextEdit,
    QLineEdit, QFileDialog, QTabWidget, QGroupBox, QSplitter, QToolBar,
    QComboBox, QStatusBar, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QInputDialog, QScrollArea, QPlainTextEdit, QStyle, QSlider
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QRect, QPoint, QMimeData, QUrl
from PyQt5.QtGui import QPainter, QBrush, QPixmap, QColor, QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView

DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #2c2c2c;
    font-family: 'Segoe UI', sans-serif;
    color: #f0f0f0;
}
QLabel {
    font-size: 11pt;
    color: #ffffff;
}
QLineEdit, QTextEdit, QPlainTextEdit {
    background: #3a3a3a;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 6px;
    color: #ffffff;
}
QPushButton {
    background-color: #565656;
    padding: 7px 12px;
    border-radius: 4px;
    color: #ffffff;
}
QPushButton:hover {
    background-color: #666666;
}
QPushButton:pressed {
    background-color: #4e4e4e;
}
QPushButton:disabled {
    background-color: #3a3a3a;
    color: #888888;
}
QCheckBox {
    spacing: 6px;
    color: #dddddd;
}
QProgressBar {
    background-color: #444;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
}
QProgressBar::chunk {
    background-color: #77b300;
}
QMenu {
    background: #3a3a3a;
    border: 1px solid #444;
}
QMenu::item:selected {
    background: #495057;
}
QTabWidget::pane {
    border: 1px solid #444;
}
QTabBar::tab {
    background: #3a3a3a;
    padding: 8px;
}
QTabBar::tab:selected {
    background: #565656;
}
QComboBox {
    background-color: #3a3a3a;
    border: 1px solid #444;
    border-radius: 4px;
    padding: 5px;
    color: #ffffff;
    min-width: 6em;
}
QComboBox:hover {
    border: 1px solid #666;
}
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 15px;
    border-left: 1px solid #444;
}
QTreeWidget {
    background-color: #3a3a3a;
    border: 1px solid #444;
    color: #ffffff;
}
QTreeWidget::item {
    height: 25px;
}
QTreeWidget::item:selected {
    background-color: #565656;
}
QScrollBar:vertical {
    border: none;
    background: #3a3a3a;
    width: 10px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background: #565656;
    min-height: 20px;
    border-radius: 5px;
}
QScrollBar::handle:vertical:hover {
    background: #666666;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
QWebEngineView {
    background-color: #3a3a3a;
}
"""

class GitHubAPI:
    """GitHub API wrapper."""
    def __init__(self, token):
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }

    def validate_token(self):
        try:
            r = requests.get("https://api.github.com/user", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}: Token invalid"
        except Exception as e:
            return False, str(e)

    def get_user_info(self, username):
        try:
            r = requests.get(f"https://api.github.com/users/{username}", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def search_users(self, query):
        try:
            r = requests.get(f"https://api.github.com/search/users?q={query}", headers=self.headers)
            if r.status_code == 200:
                return True, r.json().get('items', [])
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def follow_user(self, user):
        try:
            r = requests.put(f"https://api.github.com/user/following/{user}", headers=self.headers)
            return (r.status_code == 204), (f"Followed {user}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def unfollow_user(self, user):
        try:
            r = requests.delete(f"https://api.github.com/user/following/{user}", headers=self.headers)
            return (r.status_code == 204), (f"Unfollowed {user}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def star_repo(self, owner, repo):
        try:
            r = requests.put(f"https://api.github.com/user/starred/{owner}/{repo}", headers=self.headers)
            return (r.status_code == 204), (f"Starred {owner}/{repo}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def unstar_repo(self, owner, repo):
        try:
            r = requests.delete(f"https://api.github.com/user/starred/{owner}/{repo}", headers=self.headers)
            return (r.status_code == 204), (f"Unstarred {owner}/{repo}" if r.status_code == 204 else f"Error {r.status_code}")
        except Exception as e:
            return False, str(e)

    def get_following(self):
        try:
            r = requests.get("https://api.github.com/user/following", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def get_repos(self):
        try:
            r = requests.get("https://api.github.com/user/repos?per_page=100", headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def create_repo(self, name, desc, private):
        data = {"name": name, "description": desc, "private": private}
        try:
            r = requests.post("https://api.github.com/user/repos", headers=self.headers, json=data)
            if r.status_code == 201:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def upload_file(self, owner, repo, path, content):
        try:
            enc = base64.b64encode(content).decode()
            fn = os.path.basename(path)
            up_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{fn}"
            data = {"message": f"Add {fn}", "content": enc}
            r = requests.put(up_url, headers=self.headers, json=data)
            if r.status_code in [200, 201]:
                return True, f"Uploaded {fn}"
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def get_contents(self, owner, repo, path=""):
        """Get contents of path within the repository. path can be a file or directory."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        try:
            r = requests.get(url, headers=self.headers)
            if r.status_code == 200:
                return True, r.json()
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def update_file(self, owner, repo, path, message, new_content, sha):
        """Update an existing file in a repo."""
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
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def delete_file(self, owner, repo, path, message, sha):
        """Delete a file in a repo."""
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        data = {"message": message, "sha": sha}
        try:
            r = requests.delete(url, headers=self.headers, json=data)
            if r.status_code == 200:
                return True, f"File '{path}' deleted"
            return False, f"Error {r.status_code}"
        except Exception as e:
            return False, str(e)

    def enable_wiki(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = {"has_wiki": True}
        r = requests.patch(url, headers=self.headers, json=data)
        if r.status_code == 200:
            return True, "Wiki enabled."
        return False, f"Error {r.status_code}"

    def disable_wiki(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        data = {"has_wiki": False}
        r = requests.patch(url, headers=self.headers, json=data)
        if r.status_code == 200:
            return True, "Wiki disabled."
        return False, f"Error {r.status_code}"

    def create_branch(self, owner, repo, branch_name, base_sha):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        data = {
            "ref": f"refs/heads/{branch_name}",
            "sha": base_sha
        }
        r = requests.post(url, headers=self.headers, json=data)
        if r.status_code == 201:
            return True, f"Branch '{branch_name}' created."
        return False, f"Error {r.status_code}"

    def delete_branch(self, owner, repo, branch_name):
        url = f"https://api.github.com/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
        r = requests.delete(url, headers=self.headers)
        if r.status_code == 204:
            return True, f"Branch '{branch_name}' deleted."
        return False, f"Error {r.status_code}"
        
    def update_profile(self, name, bio, company, location, blog):
        """Update user profile information"""
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

class ActionThread(QThread):
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

class AvatarLabel(QLabel):
    def set_avatar(self, url):
        try:
            px = QPixmap()
            px.loadFromData(requests.get(url).content)
            round_px = QPixmap(px.size())
            round_px.fill(Qt.transparent)
            painter = QPainter(round_px)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(px))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, px.width(), px.height())
            painter.end()
            scaled = round_px.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
        except:
            pass

class UserWidget(QWidget):
    """Generic user display widget with optional checkbox."""
    unfollow_clicked = pyqtSignal(str)
    
    def __init__(self, username, avatar, show_check=True, show_unfollow=False):
        super().__init__()
        self.username = username
        self.box = QHBoxLayout(self)
        self.box.setContentsMargins(4, 4, 4, 4)
        self.check = QCheckBox()
        self.label_img = AvatarLabel()
        self.label_img.setFixedSize(60, 60)
        self.label_img.set_avatar(avatar)
        self.label_user = QLabel(username)
        self.label_user.setStyleSheet("font-weight: bold;")

        if show_check:
            self.box.addWidget(self.check)
        else:
            self.check.setVisible(False)

        self.box.addWidget(self.label_img)
        self.box.addWidget(self.label_user)
        
        # Add unfollow button if requested
        if show_unfollow:
            self.unfollow_btn = QPushButton("Unfollow")
            self.unfollow_btn.setFixedWidth(80)
            self.unfollow_btn.clicked.connect(lambda: self.unfollow_clicked.emit(username))
            self.box.addWidget(self.unfollow_btn)
            
        self.box.addStretch()
        self.setLayout(self.box)

    def is_checked(self):
        return self.check.isChecked()

class TokenManagerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Token Manager")
        self.resize(450, 400)
        lay = QVBoxLayout(self)
        form_box = QGroupBox("Add New")
        f_lay = QFormLayout(form_box)
        self.ed_name = QLineEdit()
        self.ed_token = QLineEdit()
        self.ed_token.setEchoMode(QLineEdit.Password)
        btn_add = QPushButton("Add Token")
        btn_add.clicked.connect(self.add_token)

        f_lay.addRow("Name:", self.ed_name)
        f_lay.addRow("Token:", self.ed_token)
        f_lay.addRow("", btn_add)
        lay.addWidget(form_box)

        exist_box = QGroupBox("Existing")
        v_lay = QVBoxLayout(exist_box)
        self.list_tokens = QListWidget()
        
        # Add edit button for tokens
        edit_hbox = QHBoxLayout()
        self.btn_rem = QPushButton("Remove Selected")
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_rem.clicked.connect(self.remove_token)
        self.btn_edit.clicked.connect(self.edit_token)
        edit_hbox.addWidget(self.btn_edit)
        edit_hbox.addWidget(self.btn_rem)
        
        v_lay.addWidget(self.list_tokens)
        v_lay.addLayout(edit_hbox)
        lay.addWidget(exist_box)

        close_btn = QDialogButtonBox(QDialogButtonBox.Close)
        close_btn.rejected.connect(self.close)
        lay.addWidget(close_btn)
        self.setLayout(lay)

        self.load_tokens()

    def load_tokens(self):
        self.list_tokens.clear()
        load_dotenv(find_dotenv(usecwd=True))
        for k in os.environ:
            if k.startswith("GITHUB_TOKEN_"):
                self.list_tokens.addItem(k[13:])

    def add_token(self):
        name = self.ed_name.text().strip()
        tok = self.ed_token.text().strip()
        if not name or not tok:
            return
        api = GitHubAPI(tok)
        ok, check = api.validate_token()
        if not ok:
            return
        env_file = find_dotenv(usecwd=True)
        if not env_file:
            with open('.env', 'w'):
                pass
            env_file = '.env'
        set_key(env_file, "GITHUB_TOKEN_" + name, tok)
        self.ed_name.clear()
        self.ed_token.clear()
        self.load_tokens()

    def remove_token(self):
        curr = self.list_tokens.currentItem()
        if curr:
            name = curr.text()
            env_file = find_dotenv(usecwd=True)
            if env_file and os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                with open(env_file, 'w') as f:
                    for ln in lines:
                        if not ln.startswith("GITHUB_TOKEN_"+name+"="):
                            f.write(ln)
            self.load_tokens()
    
    def edit_token(self):
        curr = self.list_tokens.currentItem()
        if curr:
            old_name = curr.text()
            env_file = find_dotenv(usecwd=True)
            load_dotenv(env_file)
            
            current_token = os.environ.get("GITHUB_TOKEN_" + old_name, "")
            
            # Create an edit dialog to edit both name and token
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("Edit Token")
            dialog_layout = QFormLayout(edit_dialog)
            
            name_edit = QLineEdit(old_name)
            token_edit = QLineEdit(current_token)
            token_edit.setEchoMode(QLineEdit.Password)
            
            dialog_layout.addRow("Name:", name_edit)
            dialog_layout.addRow("Token:", token_edit)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(edit_dialog.accept)
            button_box.rejected.connect(edit_dialog.reject)
            dialog_layout.addRow(button_box)
            
            if edit_dialog.exec_():
                new_name = name_edit.text().strip()
                new_token = token_edit.text().strip()
                
                if not new_name or not new_token:
                    QMessageBox.warning(self, "Invalid Input", "Name and token cannot be empty")
                    return
                    
                # First validate the token
                api = GitHubAPI(new_token)
                valid, _ = api.validate_token()
                
                if valid:
                    # Remove old token
                    with open(env_file, 'r') as f:
                        lines = f.readlines()
                    with open(env_file, 'w') as f:
                        for ln in lines:
                            if not ln.startswith("GITHUB_TOKEN_"+old_name+"="):
                                f.write(ln)
                    
                    # Add new token with new name
                    set_key(env_file, "GITHUB_TOKEN_" + new_name, new_token)
                    
                    QMessageBox.information(self, "Success", "Token updated successfully")
                    self.load_tokens()
                else:
                    QMessageBox.warning(self, "Invalid Token", "The token you entered is invalid")


class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GitHub Login")
        self.resize(500, 300)
        self.move_to_center()
        lay = QVBoxLayout(self)
        self.list_tokens = QListWidget()
        self.btn_login = QPushButton("Login")
        self.btn_login.setEnabled(False)
        self.btn_refresh = QPushButton("Refresh")
        self.btn_manage = QPushButton("Manage Tokens")
        self.btn_edit_token = QPushButton("Edit Token")
        self.btn_edit_token.setEnabled(False)
        self.selected_token = None
        self.selected_user = None

        info_label = QLabel("Select a GitHub account from your tokens:")
        info_label.setStyleSheet("font-weight: bold; font-size: 13pt;")

        hl = QHBoxLayout()
        hl.addWidget(self.btn_manage)
        hl.addWidget(self.btn_edit_token)
        hl.addStretch()
        hl.addWidget(self.btn_refresh)
        hl.addWidget(self.btn_login)

        lay.addWidget(info_label)
        lay.addWidget(self.list_tokens)
        lay.addLayout(hl)

        self.btn_login.clicked.connect(self.accept)
        self.btn_refresh.clicked.connect(self.load_tokens)
        self.btn_manage.clicked.connect(self.manage_tokens)
        self.btn_edit_token.clicked.connect(self.edit_selected_token)
        self.list_tokens.itemClicked.connect(self.token_selected)

        self.load_tokens()

    def move_to_center(self):
        screen_rect = QApplication.desktop().screenGeometry()
        window_size = self.geometry()
        x = (screen_rect.width() - window_size.width()) // 2
        y = (screen_rect.height() - window_size.height()) // 2
        self.move(x, y)

    def load_tokens(self):
        self.list_tokens.clear()
        load_dotenv(find_dotenv(usecwd=True))
        for k, v in os.environ.items():
            if k.startswith("GITHUB_TOKEN_"):
                api = GitHubAPI(v)
                ok, data = api.validate_token()
                if ok:
                    item = QListWidgetItem(k[13:] + f" ({data['login']})")
                    item.setData(Qt.UserRole, (v, data))
                else:
                    item = QListWidgetItem(k[13:] + " (Invalid)")
                    item.setForeground(QColor("red"))
                self.list_tokens.addItem(item)
        self.btn_login.setEnabled(False)
        self.btn_edit_token.setEnabled(False)

    def token_selected(self, item):
        d = item.data(Qt.UserRole)
        if d:
            self.selected_token, user_data = d
            self.selected_user = user_data
            self.btn_login.setEnabled(True)
            self.btn_edit_token.setEnabled(True)

    def manage_tokens(self):
        dlg = TokenManagerDialog(self)
        if dlg.exec_():
            self.load_tokens()
    
    def edit_selected_token(self):
        if not self.selected_token:
            return
        
        current_item = self.list_tokens.currentItem()
        if not current_item:
            return
            
        token_name = current_item.text().split(" (")[0]
        
        new_token, ok = QInputDialog.getText(
            self, 
            "Edit Token", 
            f"Update token for {token_name}:", 
            QLineEdit.Password, 
            self.selected_token
        )
        
        if ok and new_token:
            # Validate the token
            api = GitHubAPI(new_token)
            valid, data = api.validate_token()
            
            if valid:
                # Update the token in the .env file
                env_file = find_dotenv(usecwd=True)
                set_key(env_file, "GITHUB_TOKEN_" + token_name, new_token)
                QMessageBox.information(self, "Success", f"Token for {token_name} updated successfully")
                self.load_tokens()  # Refresh the list
            else:
                QMessageBox.warning(self, "Invalid Token", "The token you entered is invalid")



class MultiTokenDialog(QDialog):
    def __init__(self, tokens_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tokens")
        self.resize(400, 300)
        self.selected_tokens = []
        self.tokens_dict = tokens_dict

        main_lay = QVBoxLayout(self)
        self.list_tokens = QListWidget()
        for name in tokens_dict:
            item = QListWidgetItem(name)
            item.setCheckState(Qt.Unchecked)
            self.list_tokens.addItem(item)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.on_ok)
        btn_box.rejected.connect(self.reject)
        main_lay.addWidget(self.list_tokens)
        main_lay.addWidget(btn_box)

    def on_ok(self):
        self.selected_tokens = []
        for i in range(self.list_tokens.count()):
            item = self.list_tokens.item(i)
            if item.checkState() == Qt.Checked:
                name = item.text()
                tok = self.tokens_dict.get(name, None)
                if tok:
                    self.selected_tokens.append(tok)
        if not self.selected_tokens:
            self.reject()
        else:
            self.accept()

class ExtendedToolBar(QToolBar):
    """Custom toolbar that shows user switching and token management"""
    def __init__(self, parent=None, change_user_func=None, manage_func=None):
        super().__init__(parent)
        self.setMovable(False)
        self.setFloatable(False)
        self.change_user_func = change_user_func
        self.manage_func = manage_func
        self.parent = parent
        
        # User selector dropdown
        self.user_selector = QComboBox()
        self.user_selector.setMinimumWidth(150)
        self.user_selector.currentIndexChanged.connect(self.on_user_changed)
        self.load_users()
        
        self.addWidget(QLabel("User: "))
        self.addWidget(self.user_selector)
        
        # Manage tokens action
        self.add_manage_action()
        
    def load_users(self):
        """Load available GitHub users from tokens"""
        self.user_selector.clear()
        self.users_data = {}
        
        load_dotenv(find_dotenv(usecwd=True))
        for k, v in os.environ.items():
            if k.startswith("GITHUB_TOKEN_"):
                api = GitHubAPI(v)
                ok, data = api.validate_token()
                if ok:
                    username = data['login']
                    self.user_selector.addItem(username)
                    self.users_data[username] = (k[13:], v, data)  # Store token name, token value, and user data
        
        # Set current user
        if hasattr(self.parent, 'user_data') and self.parent.user_data:
            current_login = self.parent.user_data.get('login', '')
            index = self.user_selector.findText(current_login)
            if index >= 0:
                self.user_selector.setCurrentIndex(index)

    def add_manage_action(self):
        act = self.addAction(QIcon(), "Manage Tokens", self.on_manage)
        act.setToolTip("Manage saved tokens")

    def on_user_changed(self, index):
        """Handle user selection change"""
        if index < 0 or not self.change_user_func:
            return
            
        username = self.user_selector.currentText()
        if username in self.users_data:
            token_name, token, user_data = self.users_data[username]
            self.change_user_func(token, user_data)

    def on_manage(self):
        if self.manage_func:
            self.manage_func()

class DropArea(QWidget):
    """Widget that accepts file drops for uploading to GitHub"""
    fileDrop = pyqtSignal(list)  # Signal emitted when files are dropped

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        self.label = QLabel("Drop files here to upload")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            border: 2px dashed #565656;
            padding: 20px;
            border-radius: 8px;
            font-size: 14pt;
        """)
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setMinimumHeight(100)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.label.setStyleSheet("""
                border: 2px dashed #77b300;
                padding: 20px;
                border-radius: 8px;
                font-size: 14pt;
                background-color: rgba(119, 179, 0, 0.1);
            """)

    def dragLeaveEvent(self, event):
        self.label.setStyleSheet("""
            border: 2px dashed #565656;
            padding: 20px;
            border-radius: 8px;
            font-size: 14pt;
        """)

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if file_paths:
            self.fileDrop.emit(file_paths)
        self.label.setStyleSheet("""
            border: 2px dashed #565656;
            padding: 20px;
            border-radius: 8px;
            font-size: 14pt;
        """)

class MarkdownPreview(QWidget):
    """Widget to preview markdown or code with proper styling"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview WebView
        self.preview = QWebEngineView()
        self.preview.setMinimumHeight(200)
        layout.addWidget(self.preview)
        self.setLayout(layout)
        
        # Default GitHub-style CSS
        self.github_css = """
        <style>
            html, body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                font-size: 16px;
                line-height: 1.5;
                color: #e6edf3;
                background-color: #0d1117;
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow-x: hidden;
                box-sizing: border-box;
            }
            .markdown-body {
                box-sizing: border-box;
                width: 100%;
                max-width: 100%;
                margin: 0;
                padding: 16px;
                overflow-wrap: break-word;
                word-wrap: break-word;
            }
            .markdown-body img {
                max-width: 100%;
                height: auto;
            }
            h1, h2, h3, h4, h5, h6 {
                margin-top: 24px;
                margin-bottom: 16px;
                font-weight: 600;
                line-height: 1.25;
                color: #e6edf3;
            }
            h1 { font-size: 2em; padding-bottom: 0.3em; border-bottom: 1px solid #3b434b; }
            h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #3b434b; }
            h3 { font-size: 1.25em; }
            h4 { font-size: 1em; }
            p, blockquote, ul, ol, dl, table, pre { margin-top: 0; margin-bottom: 16px; }
            code, pre {
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace;
            }
            pre {
                padding: 16px;
                overflow: auto;
                font-size: 85%;
                line-height: 1.45;
                background-color: #161b22;
                border-radius: 3px;
                white-space: pre-wrap;
                word-wrap: break-word;
                max-width: 100%;
            }
            code {
                padding: 0.2em 0.4em;
                margin: 0;
                font-size: 85%;
                background-color: rgba(240,246,252,0.15);
                border-radius: 3px;
            }
            pre code {
                background-color: transparent;
                padding: 0;
                margin: 0;
                font-size: 100%;
                word-break: normal;
                white-space: pre-wrap;
                border: 0;
            }
            blockquote {
                padding: 0 1em;
                color: #8b949e;
                border-left: 0.25em solid #3b434b;
            }
            table {
                border-spacing: 0;
                border-collapse: collapse;
                width: 100%;
                max-width: 100%;
                overflow-x: auto;
                display: block;
            }
            table th, table td {
                padding: 6px 13px;
                border: 1px solid #3b434b;
            }
            table tr:nth-child(2n) {
                background-color: #161b22;
            }
            
            /* Force content to fit within viewport */
            @media screen and (max-width: 100%) {
                body, .markdown-body {
                    width: 100%;
                    padding: 10px;
                    box-sizing: border-box;
                }
                
                pre, code, table {
                    max-width: 100%;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
            }
        </style>
        """
        
        self.update_preview("")
        
        # Set fixed zoom to 75%
        self.preview.setZoomFactor(0.75)

    def update_preview(self, content, file_type="markdown", dark_mode=True):
        """Update the preview with the given content"""
        self.current_content = content
        self.current_file_type = file_type
        
        if not content:
            html = f"{self.github_css}<div class='markdown-body'>Preview will appear here</div>"
            self.preview.setHtml(html)
            return
            
        if file_type == "markdown":
            # Convert markdown to HTML
            try:
                html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
                html = f"{self.github_css}<div class='markdown-body'>{html_content}</div>"
            except Exception as e:
                html = f"{self.github_css}<div class='markdown-body'>Error rendering markdown: {str(e)}</div>"
        else:
            # For code files, use <pre> with syntax highlighting
            # We'd normally use a syntax highlighter here, but for simplicity just wrapping in pre
            html = f"""
            {self.github_css}
            <div class='markdown-body'>
                <pre><code>{content.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>
            </div>
            """
        
        self.preview.setHtml(html)
        # Maintain fixed zoom at 75%
        self.preview.setZoomFactor(0.75)

class RepoBrowserTab(QWidget):
    """A tab to display the user's repositories, navigate files, edit, save, upload, delete."""
    def __init__(self, api, user_data):
        super().__init__()
        self.api = api
        self.user_data = user_data
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        # Current navigation path
        self.current_path = ""
        self.current_repo = ""
        self.path_history = []

        # Repository selection section with Create New button
        repo_selection = QHBoxLayout()
        
        # Combobox with placeholder text
        self.cmb_repos = QComboBox()
        self.cmb_repos.addItem("Select Repo")
        self.cmb_repos.setItemData(0, QColor(120, 120, 120), Qt.ForegroundRole)
        self.cmb_repos.setCurrentIndex(0)
        self.cmb_repos.currentIndexChanged.connect(self.on_repo_changed)
        
        # Add Create Repository button next to dropdown
        btn_create_repo = QPushButton("Create Repo")
        btn_create_repo.clicked.connect(self.show_create_repo_dialog)
        
        repo_selection.addWidget(self.cmb_repos)
        repo_selection.addWidget(btn_create_repo)
        repo_selection.addStretch()
        
        # Main content area
        content_layout = QVBoxLayout()
        
        # Tree view header with back button
        tree_header = QHBoxLayout()
        self.btn_back = QPushButton("⬅ Back")
        self.btn_back.clicked.connect(self.go_back)
        self.btn_back.setEnabled(False)
        self.path_label = QLabel("/")
        self.path_label.setStyleSheet("color: #ffffff;")
        
        tree_header.addWidget(self.btn_back)
        tree_header.addWidget(self.path_label)
        tree_header.addStretch()
        
        # Files and editor
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left side - tree and drop area
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.addLayout(tree_header)
        
        self.tree_files = QTreeWidget()
        self.tree_files.setColumnCount(1)
        # Change the header from "Files" to empty - we're showing it in the path_label now
        self.tree_files.setHeaderLabels([""])
        self.tree_files.setStyleSheet("""
            QTreeWidget {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QTreeWidget::item {
                height: 24px;
            }
            QTreeWidget::item:selected {
                background-color: #565656;
            }
            QHeaderView::section {
                background-color: #3a3a3a;
                color: #e0e0e0;
                padding: 5px;
                border: 1px solid #444;
            }
        """)
        self.tree_files.itemClicked.connect(self.on_item_clicked)
        self.tree_files.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # Button group - file operations buttons on left side
        button_layout = QHBoxLayout()
        
        # New File/Folder buttons
        self.btn_new_file = QPushButton("New File")
        self.btn_new_folder = QPushButton("New Folder")
        self.btn_save_file = QPushButton("Save File")
        self.btn_delete_file = QPushButton("Delete File")
        self.btn_delete_folder = QPushButton("Delete Folder")
        
        self.btn_new_file.clicked.connect(self.create_new_file)
        self.btn_new_folder.clicked.connect(self.create_new_folder)
        self.btn_save_file.clicked.connect(self.save_current_file)
        self.btn_delete_file.clicked.connect(self.delete_current_file)
        self.btn_delete_folder.clicked.connect(self.delete_current_folder)
        
        button_layout.addWidget(self.btn_new_file)
        button_layout.addWidget(self.btn_new_folder)
        button_layout.addWidget(self.btn_save_file)
        button_layout.addWidget(self.btn_delete_file)
        button_layout.addWidget(self.btn_delete_folder)
        button_layout.addStretch()
        
        # Drop and select area
        self.drop_area = DropArea()
        self.drop_area.fileDrop.connect(self.handle_file_drop)
        
        # Add browse button to drop area
        browse_btn = QPushButton("Browse Files")
        browse_btn.clicked.connect(self.browse_files)
        
        left_layout.addWidget(self.tree_files)
        left_layout.addLayout(button_layout)
        left_layout.addWidget(self.drop_area)
        left_layout.addWidget(browse_btn)
        
        # Right side - editor and preview
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Add search and replace functionality
        search_replace_layout = QHBoxLayout()
        search_label = QLabel("Find:")
        self.search_edit = QLineEdit()
        self.search_edit.returnPressed.connect(self.find_text)
        
        replace_label = QLabel("Replace:")
        self.replace_edit = QLineEdit()
        
        self.find_btn = QPushButton("Find")
        self.replace_btn = QPushButton("Replace")
        self.replace_all_btn = QPushButton("Replace All")
        
        self.find_btn.clicked.connect(self.find_text)
        self.replace_btn.clicked.connect(self.replace_text)
        self.replace_all_btn.clicked.connect(self.replace_all_text)
        
        search_replace_layout.addWidget(search_label)
        search_replace_layout.addWidget(self.search_edit)
        search_replace_layout.addWidget(replace_label)
        search_replace_layout.addWidget(self.replace_edit)
        search_replace_layout.addWidget(self.find_btn)
        search_replace_layout.addWidget(self.replace_btn)
        search_replace_layout.addWidget(self.replace_all_btn)
        
        right_layout.addLayout(search_replace_layout)
        
        # Text editor with live preview in a vertical splitter
        self.editor_preview_splitter = QSplitter(Qt.Vertical)
        
        # Text editor for code/markdown
        self.text_content = QPlainTextEdit()
        self.text_content.setPlaceholderText("File content here...")
        self.text_content.setReadOnly(True)
        self.text_content.textChanged.connect(self.update_preview)
        
        # Make text content scrollbar match preview scrollbar style
        self.text_content.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2c2c2c;
                color: #e0e0e0;
                border: 1px solid #444;
            }
            QScrollBar:vertical {
                border: none;
                background: #2c2c2c;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #565656;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)
        
        # Markdown/code preview panel
        self.preview = MarkdownPreview()
        
        self.editor_preview_splitter.addWidget(self.text_content)
        self.editor_preview_splitter.addWidget(self.preview)
        
        # Set split sizes (40% editor, 60% preview)
        self.editor_preview_splitter.setSizes([400, 600])
        
        right_layout.addWidget(self.editor_preview_splitter)
        
        # Add widgets to main splitter
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)
        main_splitter.setSizes([300, 700])  # Proportional sizes
        
        content_layout.addWidget(main_splitter)
        
        # Add to main layout
        self.layout.addLayout(repo_selection)
        self.layout.addLayout(content_layout)
        
        # Initialize
        self.selected_file = None
        self.selected_sha = None
        self.selected_path = ""
        self.current_file_type = "text"
        self.selected_folder = None
        
        # Load repos
        self.load_user_repos()
    
    def find_text(self):
        """Find text in the editor"""
        search_text = self.search_edit.text()
        if not search_text:
            return
            
        # Start search from current cursor position
        cursor = self.text_content.textCursor()
        # If nothing is selected, start from beginning
        if not cursor.hasSelection():
            cursor.setPosition(0)
            self.text_content.setTextCursor(cursor)
            
        # Find next occurrence
        found = self.text_content.find(search_text)
        if not found:
            # Try from the beginning
            cursor.setPosition(0)
            self.text_content.setTextCursor(cursor)
            found = self.text_content.find(search_text)
            
        if not found:
            QMessageBox.information(self, "Search", f"No occurrences of '{search_text}' found")
    
    def replace_text(self):
        """Replace selected text in the editor"""
        search_text = self.search_edit.text()
        replace_text = self.replace_edit.text()
        
        if not search_text:
            return
            
        # Replace selected text if it matches search text
        cursor = self.text_content.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == search_text:
            cursor.insertText(replace_text)
            
        # Find next occurrence
        self.find_text()
    
    def replace_all_text(self):
        """Replace all occurrences of search text"""
        search_text = self.search_edit.text()
        replace_text = self.replace_edit.text()
        
        if not search_text:
            return
            
        content = self.text_content.toPlainText()
        if search_text in content:
            new_content = content.replace(search_text, replace_text)
            self.text_content.setPlainText(new_content)
            count = content.count(search_text)
            QMessageBox.information(self, "Replace All", f"Replaced {count} occurrences")
        else:
            QMessageBox.information(self, "Replace All", f"No occurrences of '{search_text}' found")
    
    def create_new_file(self):
        """Create a new file in the current directory"""
        if not self.current_repo:
            QMessageBox.warning(self, "Error", "Please select a repository first")
            return
            
        filename, ok = QInputDialog.getText(
            self,
            "Create New File",
            "Enter file name:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and filename:
            # Create empty file
            owner = self.user_data.get("login", "")
            repo_name = self.current_repo
            
            # Build path
            path = self.current_path
            if path:
                path += "/"
            path += filename
            
            # Empty content
            content = ""
            
            # Upload file
            success, msg = self.api.upload_file(owner, repo_name, path, content.encode('utf-8'))
            if success:
                QMessageBox.information(self, "Success", f"File '{filename}' created successfully")
                self.load_directory_contents()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create file: {msg}")
    
    def create_new_folder(self):
        """Create a new folder in the current directory"""
        if not self.current_repo:
            QMessageBox.warning(self, "Error", "Please select a repository first")
            return
            
        foldername, ok = QInputDialog.getText(
            self,
            "Create New Folder",
            "Enter folder name:",
            QLineEdit.Normal,
            ""
        )
        
        if ok and foldername:
            # GitHub doesn't have direct folder creation - create a .gitkeep file instead
            owner = self.user_data.get("login", "")
            repo_name = self.current_repo
            
            # Build path
            path = self.current_path
            if path:
                path += "/"
            path += foldername + "/.gitkeep"
            
            # Empty content for the .gitkeep file
            content = ""
            
            # Upload file to create the directory
            success, msg = self.api.upload_file(owner, repo_name, path, content.encode('utf-8'))
            if success:
                QMessageBox.information(self, "Success", f"Folder '{foldername}' created successfully")
                self.load_directory_contents()
            else:
                QMessageBox.warning(self, "Error", f"Failed to create folder: {msg}")
    
    def delete_current_folder(self):
        """Delete the selected folder"""
        if not self.selected_folder:
            QMessageBox.warning(self, "Error", "Please select a folder first")
            return
            
        folder_path = self.selected_folder["path"]
        folder_name = self.selected_folder["name"]
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Really delete folder '{folder_name}' and all its contents?\nThis action cannot be undone!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # GitHub API doesn't directly support folder deletion
            # We need to recursively delete all files in the folder
            self.recursive_delete_folder(folder_path)
    
    def recursive_delete_folder(self, folder_path):
        """Recursively delete all files in a folder"""
        owner = self.user_data.get("login", "")
        repo_name = self.current_repo
        
        # Get all files in the folder
        ok, contents = self.api.get_contents(owner, repo_name, folder_path)
        if not ok:
            QMessageBox.warning(self, "Error", f"Failed to list folder contents: {contents}")
            return
        
        if not isinstance(contents, list):
            contents = [contents]
        
        # Track success and failure counts
        success_count = 0
        failure_count = 0
        
        # Process all items
        for item in contents:
            if item["type"] == "dir":
                # Recursively delete subfolder
                self.recursive_delete_folder(item["path"])
            else:
                # Delete file
                message = f"Delete file {item['path']}"
                ok, res = self.api.delete_file(owner, repo_name, item["path"], message, item["sha"])
                if ok:
                    success_count += 1
                else:
                    failure_count += 1
        
        # Show results
        if failure_count == 0:
            QMessageBox.information(self, "Success", f"Folder deleted successfully")
        else:
            QMessageBox.warning(self, "Partial Success", 
                               f"Deleted {success_count} files, but failed to delete {failure_count} files")
        
        # Refresh directory listing
        self.load_directory_contents()
        self.selected_folder = None
    
    def show_create_repo_dialog(self):
        """Show dialog to create a new repository"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Repository")
        layout = QFormLayout(dialog)
        
        name_edit = QLineEdit()
        desc_edit = QLineEdit()
        private_check = QCheckBox()
        
        layout.addRow("Name:", name_edit)
        layout.addRow("Description:", desc_edit)
        layout.addRow("Private:", private_check)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_():
            name = name_edit.text().strip()
            desc = desc_edit.text().strip()
            private = private_check.isChecked()
            
            if not name:
                QMessageBox.warning(self, "Error", "Repository name is required")
                return
                
            self.create_repo(name, desc, private)
    
    def create_repo(self, name, desc, private):
        """Create a new repository"""
        ok, r = self.api.create_repo(name, desc, private)
        if ok:
            QMessageBox.information(
                self, 
                "Success", 
                f"Repository '{name}' created successfully"
            )
            # Refresh repos
            self.load_user_repos()
            
            # Select the newly created repo
            index = self.cmb_repos.findText(name)
            if index >= 0:
                self.cmb_repos.setCurrentIndex(index)
        else:
            QMessageBox.warning(self, "Error", f"Failed to create repository: {r}")
    
    def browse_files(self):
        """Open file browser to select files to upload"""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload")
        if files:
            self.handle_file_drop(files)
    
    def go_back(self):
        """Navigate back to the previous directory"""
        if self.path_history:
            # Get previous path
            prev_path = self.path_history.pop()
            self.current_path = prev_path
            
            # Update UI
            self.path_label.setText(f"/{self.current_path}")
            self.btn_back.setEnabled(bool(self.path_history))
            
            # Load directory contents
            self.load_directory_contents()
    
    def on_repo_changed(self, index):
        """Automatically load repo contents when a repo is selected"""
        if index > 0:  # Skip placeholder item
            self.current_repo = self.cmb_repos.currentText()
            self.current_path = ""
            self.path_history = []
            self.btn_back.setEnabled(False)
            self.path_label.setText("/")
            self.load_directory_contents()
    
    def on_item_double_clicked(self, item, column):
        """Handle double click on tree items (for directory navigation)"""
        data = item.data(0, Qt.UserRole)
        if not data:
            return
            
        if data["type"] == "dir":
            # Save selected folder (for delete operation)
            self.selected_folder = data
            
            # Navigate into directory
            self.path_history.append(self.current_path)
            self.current_path = data["path"]
            self.path_label.setText(f"/{self.current_path}")
            self.btn_back.setEnabled(True)
            self.load_directory_contents()
    
    def handle_file_drop(self, file_paths):
        """Handle files dropped onto the drop area"""
        owner = self.user_data.get("login", "")
        repo_name = self.current_repo
        
        if not owner or not repo_name:
            QMessageBox.warning(self, "Error", "Please select a repository first")
            return
            
        upload_count = 0
        failed_count = 0
        
        for path in file_paths:
            try:
                target_path = self.current_path
                if target_path:
                    target_path += "/"
                target_path += os.path.basename(path)
                
                with open(path, 'rb') as fp:
                    content = fp.read()
                success, msg = self.api.upload_file(owner, repo_name, target_path, content)
                if success:
                    upload_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                failed_count += 1
        
        # Show results and refresh the repo structure
        if upload_count > 0:
            QMessageBox.information(
                self, 
                "Upload Complete", 
                f"Successfully uploaded {upload_count} file(s)" + 
                (f"\nFailed to upload {failed_count} file(s)" if failed_count > 0 else "")
            )
            self.load_directory_contents()  # Refresh to show the new files
        elif failed_count > 0:
            QMessageBox.warning(
                self, 
                "Upload Failed", 
                f"Failed to upload {failed_count} file(s)"
            )

    def update_preview(self):
        """Update the preview panel based on the current content"""
        content = self.text_content.toPlainText()
        
        # Determine file type based on extension or content
        file_type = "markdown"
        if self.selected_path:
            if self.selected_path.lower().endswith(('.md', '.markdown')):
                file_type = "markdown"
            else:
                file_type = "code"
        
        self.preview.update_preview(content, file_type)

    def load_user_repos(self):
        ok, data = self.api.get_repos()
        if not ok or not isinstance(data, list):
            return
        # Clear but keep the placeholder
        self.cmb_repos.clear()
        self.cmb_repos.addItem("Select Repo")
        self.cmb_repos.setItemData(0, QColor(120, 120, 120), Qt.ForegroundRole)
        
        for r in data:
            self.cmb_repos.addItem(r["name"])
        self.cmb_repos.setCurrentIndex(0)

    def load_directory_contents(self):
        """Load contents of the current directory path"""
        self.tree_files.clear()
        if not self.current_repo:
            return
            
        owner = self.user_data.get("login", "")
        if not owner:
            return
            
        ok, content = self.api.get_contents(owner, self.current_repo, self.current_path)
        if not ok:
            QMessageBox.warning(self, "Error", f"Failed to load repository contents: {content}")
            return
            
        if not isinstance(content, list):
            # If it's a single file, handle it differently
            content = [content]
            
        # First add folders
        for item in sorted(content, key=lambda x: (x["type"] != "dir", x["name"].lower())):
            node = QTreeWidgetItem([item["name"]])
            node.setData(0, Qt.UserRole, item)
            
            # Set folder icon or file icon based on type
            if item["type"] == "dir":
                node.setIcon(0, self.style().standardIcon(QStyle.SP_DirIcon))
            else:
                node.setIcon(0, self.style().standardIcon(QStyle.SP_FileIcon))
                
            self.tree_files.addTopLevelItem(node)

    def on_item_clicked(self, item, col):
        data = item.data(0, Qt.UserRole)
        if not data:
            return
            
        if data["type"] == "dir":
            # Store selected folder for delete operation
            self.selected_folder = data
            self.selected_file = None
            self.selected_sha = None
            self.selected_path = ""
            self.text_content.clear()
            self.text_content.setReadOnly(True)
            self.preview.update_preview("", "text")
        elif data["type"] == "file":
            # Clear selected folder
            self.selected_folder = None
            
            # Load file content
            owner = self.user_data.get("login", "")
            repo_name = self.current_repo
            path = data["path"]
            ok, res = self.api.get_contents(owner, repo_name, path)
            if ok and isinstance(res, dict):
                if "content" in res:
                    content_bytes = base64.b64decode(res["content"])
                    self.text_content.setPlainText(content_bytes.decode('utf-8', errors='replace'))
                    self.text_content.setReadOnly(False)
                    self.selected_file = data
                    self.selected_sha = res["sha"]
                    self.selected_path = path
                    
                    # Update preview based on file type
                    if path.lower().endswith(('.md', '.markdown')):
                        self.current_file_type = "markdown"
                    else:
                        self.current_file_type = "code"
                    
                    self.update_preview()
                else:
                    self.text_content.setPlainText("")
                    self.text_content.setReadOnly(True)
                    self.preview.update_preview("", "text")
            else:
                self.text_content.setPlainText("")
                self.text_content.setReadOnly(True)
                self.preview.update_preview("", "text")

    def save_current_file(self):
        if not self.selected_file or not self.selected_sha:
            return
        owner = self.user_data.get("login", "")
        repo_name = self.current_repo
        path = self.selected_path
        new_content = self.text_content.toPlainText()
        message = f"Update file {path}"
        ok, res = self.api.update_file(owner, repo_name, path, message, new_content, self.selected_sha)
        if ok:
            QMessageBox.information(self, "Success", f"File '{path}' updated successfully.")
            # Re-fetch the file to get new SHA
            ok2, refreshed = self.api.get_contents(owner, repo_name, path)
            if ok2 and isinstance(refreshed, dict):
                self.selected_sha = refreshed.get("sha", "")
        else:
            QMessageBox.warning(self, "Error", str(res))

    def delete_current_file(self):
        if not self.selected_file or not self.selected_sha:
            return
        owner = self.user_data.get("login", "")
        repo_name = self.current_repo
        path = self.selected_path
        message = f"Delete file {path}"
        reply = QMessageBox.question(self, "Confirm", f"Really delete '{path}'?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            ok, res = self.api.delete_file(owner, repo_name, path, message, self.selected_sha)
            if ok:
                QMessageBox.information(self, "Success", f"File '{path}' deleted successfully.")
                self.text_content.clear()
                self.text_content.setReadOnly(True)
                self.selected_file = None
                self.selected_sha = None
                self.selected_path = ""
                self.preview.update_preview("", "text")
                self.load_directory_contents()
            else:
                QMessageBox.warning(self, "Error", str(res))

# Remove the ProfileEditDialog class as it's no longer needed
# The profile editing functionality is now directly integrated in the ProfileTab

class ProfileTab(QWidget):
    """Enhanced Profile tab with additional features"""
    def __init__(self, api, user_data, parent=None):
        super().__init__(parent)
        self.api = api
        self.user_data = user_data
        self.parent = parent
        self.layout = QVBoxLayout(self)
        
        # User info section with editable fields
        user_info_layout = QVBoxLayout()
        
        # Username and avatar row
        username_row = QHBoxLayout()
        self.lbl_avatar = AvatarLabel()
        self.lbl_avatar.setFixedSize(60, 60)
        if self.user_data.get('avatar_url'):
            self.lbl_avatar.set_avatar(self.user_data['avatar_url'])
            
        # Username (not editable)
        username_label = QLabel("User:")
        username_label.setStyleSheet("font-weight: bold;")
        self.username_value = QLabel(self.user_data.get('login', ''))
        self.username_value.setStyleSheet("font-weight: bold; font-size: 14pt;")
        
        username_row.addWidget(self.lbl_avatar)
        username_row.addWidget(username_label)
        username_row.addWidget(self.username_value)
        username_row.addStretch()
        
        user_info_layout.addLayout(username_row)
        
        # Editable fields
        form_layout = QFormLayout()
        
        # Name field
        self.name_edit = QLineEdit(self.user_data.get('name', ''))
        form_layout.addRow("Name:", self.name_edit)
        
        # Bio field
        self.bio_edit = QTextEdit()
        self.bio_edit.setText(self.user_data.get('bio', ''))
        self.bio_edit.setMaximumHeight(100)
        form_layout.addRow("Bio:", self.bio_edit)
        
        # Location field
        self.location_edit = QLineEdit(self.user_data.get('location', ''))
        form_layout.addRow("Location:", self.location_edit)
        
        # Website field
        self.website_edit = QLineEdit(self.user_data.get('blog', ''))
        form_layout.addRow("Website:", self.website_edit)
        
        # Company field
        self.company_edit = QLineEdit(self.user_data.get('company', ''))
        form_layout.addRow("Company:", self.company_edit)
        
        # Save button
        save_button = QPushButton("Save Profile")
        save_button.clicked.connect(self.save_profile)
        
        user_info_layout.addLayout(form_layout)
        user_info_layout.addWidget(save_button)
        
        self.layout.addLayout(user_info_layout)
        
        # Following section
        following_group = QGroupBox("Users You Follow")
        following_layout = QVBoxLayout(following_group)
        
        # Use a scroll area for the following list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        # Container for the user widgets
        self.following_container = QWidget()
        self.following_list_layout = QVBoxLayout(self.following_container)
        self.following_list_layout.setAlignment(Qt.AlignTop)
        
        scroll_area.setWidget(self.following_container)
        following_layout.addWidget(scroll_area)
        
        self.layout.addWidget(following_group)
        
        # Load following list automatically
        self.fetch_following()
        
    def save_profile(self):
        """Save the profile changes"""
        ok, result = self.api.update_profile(
            name=self.name_edit.text(),
            bio=self.bio_edit.toPlainText(),
            company=self.company_edit.text(),
            location=self.location_edit.text(),
            blog=self.website_edit.text()
        )
        
        if ok:
            # Update internal user data
            self.user_data.update({
                'name': self.name_edit.text(),
                'bio': self.bio_edit.toPlainText(),
                'company': self.company_edit.text(),
                'location': self.location_edit.text(),
                'blog': self.website_edit.text()
            })
            QMessageBox.information(self, "Success", "Profile updated successfully")
        else:
            QMessageBox.warning(self, "Error", f"Failed to update profile: {result}")
            
    def unfollow_user(self, username):
        """Unfollow the specified user"""
        reply = QMessageBox.question(
            self,
            "Confirm Unfollow",
            f"Are you sure you want to unfollow {username}?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            ok, msg = self.api.unfollow_user(username)
            if ok:
                QMessageBox.information(self, "Success", f"Successfully unfollowed {username}")
                self.fetch_following()  # Refresh the following list
            else:
                QMessageBox.warning(self, "Error", f"Failed to unfollow: {msg}")

    def fetch_following(self):
        """Fetch and display the list of users being followed"""
        # Clear existing widgets
        while self.following_list_layout.count():
            child = self.following_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        ok, data = self.api.get_following()
        if ok:
            for u in data:
                user_widget = UserWidget(
                    u["login"], 
                    u["avatar_url"], 
                    show_check=False,
                    show_unfollow=True
                )
                user_widget.unfollow_clicked.connect(self.unfollow_user)
                self.following_list_layout.addWidget(user_widget)
                
            # Add a spacer at the end
            self.following_list_layout.addStretch()
        else:
            error_label = QLabel("Failed to fetch following list")
            error_label.setStyleSheet("color: red;")
            self.following_list_layout.addWidget(error_label)

class MainWindow(QMainWindow):
    def __init__(self, api, user_data, tokens):
        super().__init__()
        self.api = api
        self.user_data = user_data
        self.all_tokens = tokens
        self.setWindowTitle(f"GitHub Management - {user_data.get('login', '')}")
        self.resize(1150, 650)
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Replace menubar with no items or no menubar-based account items
        # We'll rely on the ExtendedToolBar instead
        self.toolbar = ExtendedToolBar(
            parent=self,
            change_user_func=self.change_user,
            manage_func=self.manage_tokens
        )
        self.addToolBar(self.toolbar)
        
        # Set dark style
        self.setStyleSheet(DARK_STYLE)

        self.build_users_tab()
        self.build_star_tab()
        self.build_profile_tab()  # Renamed from "Profile/Following" to "Profile"

        # Add a new tab for repository browsing
        self.build_repo_browser_tab()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"Logged in as {user_data.get('login', '')}")

    def build_users_tab(self):
        w = QWidget()
        ly = QVBoxLayout(w)
        h1 = QHBoxLayout()
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("Search GitHub users...")
        self.ed_search.returnPressed.connect(self.search_users)  # Add Enter key support
        btn_search = QPushButton("Search")
        btn_search.clicked.connect(self.search_users)
        h1.addWidget(self.ed_search)
        h1.addWidget(btn_search)
        ly.addLayout(h1)

        self.list_users = QListWidget()
        # Add hover styling
        self.list_users.setStyleSheet("""
            QListWidget::item:hover {
                background-color: #3a3a3a;
                border-radius: 4px;
            }
        """)
        ly.addWidget(self.list_users)

        h2 = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_none = QPushButton("Deselect All")
        btn_follow = QPushButton("Follow")
        btn_unfollow = QPushButton("Unfollow")
        btn_multi_follow = QPushButton("Multi-Acc Follow")
        btn_multi_unfollow = QPushButton("Multi-Acc Unfollow")

        btn_all.clicked.connect(self.select_all_users)
        btn_none.clicked.connect(self.deselect_all_users)
        btn_follow.clicked.connect(self.follow_selected)
        btn_unfollow.clicked.connect(self.unfollow_selected)
        btn_multi_follow.clicked.connect(self.multi_follow)
        btn_multi_unfollow.clicked.connect(self.multi_unfollow)

        h2.addWidget(btn_all)
        h2.addWidget(btn_none)
        h2.addWidget(btn_follow)
        h2.addWidget(btn_unfollow)
        h2.addWidget(btn_multi_follow)
        h2.addWidget(btn_multi_unfollow)
        ly.addLayout(h2)

        self.user_bar = QProgressBar()
        self.user_log = QTextEdit()
        self.user_log.setReadOnly(True)
        self.user_log.setMaximumHeight(120)

        ly.addWidget(self.user_bar)
        ly.addWidget(self.user_log)

        self.tabs.addTab(w, "Users")

    def build_star_tab(self):
        w = QWidget()
        ly = QVBoxLayout(w)
        top_h = QHBoxLayout()
        self.ed_repos = QTextEdit()
        self.ed_repos.setPlaceholderText("Enter repo URLs like https://github.com/owner/repo ...")
        top_h.addWidget(self.ed_repos)
        ly.addLayout(top_h)

        btn_row = QHBoxLayout()
        star_btn = QPushButton("Star")
        unstar_btn = QPushButton("Unstar")
        multi_star_btn = QPushButton("Multi-Acc Star")
        multi_unstar_btn = QPushButton("Multi-Acc Unstar")
        clr_btn = QPushButton("Clear")

        star_btn.clicked.connect(self.star_repos)
        unstar_btn.clicked.connect(self.unstar_repos)
        multi_star_btn.clicked.connect(self.multi_star)
        multi_unstar_btn.clicked.connect(self.multi_unstar)
        clr_btn.clicked.connect(lambda: self.ed_repos.clear())

        btn_row.addWidget(star_btn)
        btn_row.addWidget(unstar_btn)
        btn_row.addWidget(multi_star_btn)
        btn_row.addWidget(multi_unstar_btn)
        btn_row.addWidget(clr_btn)

        ly.addLayout(btn_row)

        self.repo_bar = QProgressBar()
        self.repo_log = QTextEdit()
        self.repo_log.setReadOnly(True)
        self.repo_log.setMaximumHeight(120)
        ly.addWidget(self.repo_bar)
        ly.addWidget(self.repo_log)

        self.tabs.addTab(w, "Star Repos")

    def build_profile_tab(self):
        """Build the enhanced Profile tab"""
        self.profile_tab = ProfileTab(self.api, self.user_data, self)
        self.tabs.addTab(self.profile_tab, "Profile")

    def build_repo_browser_tab(self):
        """New tab for browsing and editing files in the user's repos."""
        self.repo_browser_tab = RepoBrowserTab(self.api, self.user_data)
        self.tabs.addTab(self.repo_browser_tab, "Repo Browser")

    ################################
    #    Users Tab Methods         #
    ################################

    def change_user(self, token, user_data):
        """Change to a different GitHub user"""
        # Update the API and user data
        self.api = GitHubAPI(token)
        self.user_data = user_data
        
        # Update window title
        self.setWindowTitle(f"GitHub Management - {user_data.get('login', '')}")
        
        # Update status bar
        self.status_bar.showMessage(f"Logged in as {user_data.get('login', '')}")
        
        # Update UI with new user data
        self.profile_tab = ProfileTab(self.api, self.user_data, self)
        self.tabs.removeTab(2)  # Remove old profile tab
        self.tabs.insertTab(2, self.profile_tab, "Profile")
        
        # Refresh repo browser
        self.repo_browser_tab = RepoBrowserTab(self.api, self.user_data)
        self.tabs.removeTab(3)  # Remove old repo browser tab
        self.tabs.insertTab(3, self.repo_browser_tab, "Repo Browser")
        
        # Set focus on profile tab to show the change
        self.tabs.setCurrentIndex(2)
        
        QMessageBox.information(self, "User Changed", f"Switched to user: {user_data.get('login', '')}")
    
    def select_all_users(self):
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w:
                w.check.setChecked(True)

    def deselect_all_users(self):
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w:
                w.check.setChecked(False)

    def follow_selected(self):
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        if not selected:
            return
        self.user_log.clear()
        self.user_bar.setValue(0)
        self.follow_thread = ActionThread(self.api, 'follow', selected)
        self.follow_thread.progress.connect(lambda p, m: [self.user_bar.setValue(p), self.user_log.append(m)])
        self.follow_thread.done.connect(lambda s, msg: self.user_log.append(msg))
        self.follow_thread.start()

    def unfollow_selected(self):
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        if not selected:
            return
        self.user_log.clear()
        self.user_bar.setValue(0)
        self.unfollow_thread = ActionThread(self.api, 'unfollow', selected)
        self.unfollow_thread.progress.connect(lambda p, m: [self.user_bar.setValue(p), self.user_log.append(m)])
        self.unfollow_thread.done.connect(lambda s, msg: self.user_log.append(msg))
        self.unfollow_thread.start()

    def multi_follow(self):
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        if len(self.all_tokens) <= 1 or not selected:
            return
        dlg = MultiTokenDialog(self.all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.user_log.clear()
            self.user_bar.setValue(0)
            self.mf_thread = MultiAccountThread(tokens, 'follow', selected)
            self.mf_thread.progress.connect(lambda p, m: [self.user_bar.setValue(p), self.user_log.append(m)])
            self.mf_thread.done.connect(lambda s, msg: self.user_log.append(msg))
            self.mf_thread.start()

    def multi_unfollow(self):
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        if len(self.all_tokens) <= 1 or not selected:
            return
        dlg = MultiTokenDialog(self.all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.user_log.clear()
            self.user_bar.setValue(0)
            self.muf_thread = MultiAccountThread(tokens, 'unfollow', selected)
            self.muf_thread.progress.connect(lambda p, m: [self.user_bar.setValue(p), self.user_log.append(m)])
            self.muf_thread.done.connect(lambda s, msg: self.user_log.append(msg))
            self.muf_thread.start()

    def search_users(self):
        q = self.ed_search.text().strip()
        if not q:
            return
        self.list_users.clear()
        self.user_log.clear()
        self.user_log.append(f"Searching '{q}' ...")

        ok, res = self.api.search_users(q)
        if ok:
            for user in res:
                s_ok, ud = self.api.get_user_info(user["login"])
                av = ud["avatar_url"] if s_ok else user["avatar_url"]
                item = QListWidgetItem()
                uw = UserWidget(user["login"], av, show_check=True)
                item.setSizeHint(uw.sizeHint())
                self.list_users.addItem(item)
                self.list_users.setItemWidget(item, uw)
            self.user_log.append(f"Found {len(res)} users.")
        else:
            self.user_log.append(str(res))
            QMessageBox.warning(self, "Search Error", f"Failed to search for users: {res}")

    ################################
    #  Star / Unstar Repos Methods #
    ################################

    def star_repos(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines:
            return
        self.repo_log.clear()
        self.repo_bar.setValue(0)
        self.star_thread = ActionThread(self.api, 'star', lines)
        self.star_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
        self.star_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
        self.star_thread.start()

    def unstar_repos(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines:
            return
        self.repo_log.clear()
        self.repo_bar.setValue(0)
        self.unstar_thread = ActionThread(self.api, 'unstar', lines)
        self.unstar_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
        self.unstar_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
        self.unstar_thread.start()

    def multi_star(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines or len(self.all_tokens) <= 1:
            return
        dlg = MultiTokenDialog(self.all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.repo_log.clear()
            self.repo_bar.setValue(0)
            self.ms_thread = MultiAccountThread(tokens, 'star', lines)
            self.ms_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
            self.ms_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
            self.ms_thread.start()

    def multi_unstar(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines or len(self.all_tokens) <= 1:
            return
        dlg = MultiTokenDialog(self.all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.repo_log.clear()
            self.repo_bar.setValue(0)
            self.mus_thread = MultiAccountThread(tokens, 'unstar', lines)
            self.mus_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
            self.mus_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
            self.mus_thread.start()
            
    ################################
    #   Toolbar Actions Handlers   #
    ################################

    def manage_tokens(self):
        dlg = TokenManagerDialog(self)
        dlg.exec_()

    def search_users(self):
        q = self.ed_search.text().strip()
        if not q:
            return
        self.list_users.clear()
        self.user_log.clear()
        self.user_log.append(f"Searching '{q}' ...")

        ok, res = self.api.search_users(q)
        if ok:
            for user in res:
                s_ok, ud = self.api.get_user_info(user["login"])
                av = ud["avatar_url"] if s_ok else user["avatar_url"]
                item = QListWidgetItem()
                uw = UserWidget(user["login"], av, show_check=True)
                item.setSizeHint(uw.sizeHint())
                self.list_users.addItem(item)
                self.list_users.setItemWidget(item, uw)
            self.user_log.append(f"Found {len(res)} users.")
        else:
            self.user_log.append(str(res))
            QMessageBox.warning(self, "Search Error", f"Failed to search for users: {res}")

    ################################
    #  Star / Unstar Repos Methods #
    ################################

    def star_repos(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines:
            return
        self.repo_log.clear()
        self.repo_bar.setValue(0)
        self.star_thread = ActionThread(self.api, 'star', lines)
        self.star_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
        self.star_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
        self.star_thread.start()

    def unstar_repos(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines:
            return
        self.repo_log.clear()
        self.repo_bar.setValue(0)
        self.unstar_thread = ActionThread(self.api, 'unstar', lines)
        self.unstar_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
        self.unstar_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
        self.unstar_thread.start()

    def multi_star(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines or len(self.all_tokens) <= 1:
            return
        dlg = MultiTokenDialog(self.all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.repo_log.clear()
            self.repo_bar.setValue(0)
            self.ms_thread = MultiAccountThread(tokens, 'star', lines)
            self.ms_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
            self.ms_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
            self.ms_thread.start()

    def multi_unstar(self):
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines or len(self.all_tokens) <= 1:
            return
        dlg = MultiTokenDialog(self.all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.repo_log.clear()
            self.repo_bar.setValue(0)
            self.mus_thread = MultiAccountThread(tokens, 'unstar', lines)
            self.mus_thread.progress.connect(lambda p, m: [self.repo_bar.setValue(p), self.repo_log.append(m)])
            self.mus_thread.done.connect(lambda s, msg: self.repo_log.append(msg))
            self.mus_thread.start()
            
    ################################
    #   Toolbar Actions Handlers   #
    ################################

    def manage_tokens(self):
        dlg = TokenManagerDialog(self)
        dlg.exec_()

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    envf = find_dotenv(usecwd=True)
    if not envf:
        open('.env', 'w').close()
    load_dotenv(envf)
    all_tokens = {}
    for k, v in os.environ.items():
        if k.startswith("GITHUB_TOKEN_"):
            all_tokens[k[13:]] = v

    lw = LoginWindow()
    if lw.exec_():
        if lw.selected_token and lw.selected_user:
            mw = MainWindow(GitHubAPI(lw.selected_token), lw.selected_user, all_tokens)
            mw.show()
            return app.exec_()
    return 0

if __name__ == "__main__":
    sys.exit(main())
