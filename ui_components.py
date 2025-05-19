#!/usr/bin/env python3
import os
import requests
import markdown
import re
import base64
from dotenv import load_dotenv, set_key, find_dotenv
from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QDialogButtonBox,
    QLabel, QPushButton, QListWidget, QListWidgetItem, QCheckBox, QProgressBar,
    QTextEdit, QLineEdit, QFileDialog, QGroupBox, QSplitter, QComboBox, QTreeWidget,
    QTreeWidgetItem, QMessageBox, QInputDialog, QStackedWidget, QButtonGroup,
    QScrollArea, QPlainTextEdit, QStyle
)
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QMimeData, QUrl
from PyQt5.QtGui import QPainter, QBrush, QPixmap, QColor, QIcon, QDragEnterEvent, QDropEvent
from PyQt5.QtWebEngineWidgets import QWebEngineView
from github_api import GitHubAPI

# Modern dark style with improved visual hierarchy
DARK_STYLE = """
QMainWindow, QDialog, QWidget {
    background-color: #1e1e2e;
    font-family: 'Segoe UI', 'SF Pro Display', system-ui, sans-serif;
    color: #e0e0e0;
}

QLabel {
    font-size: 11pt;
    color: #ffffff;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background: #2a2a3a;
    border: 1px solid #3f3f5f;
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
    selection-background-color: #505080;
}

QPushButton {
    background-color: #565695;
    padding: 9px 14px;
    border-radius: 6px;
    color: #ffffff;
    font-weight: 500;
}

QPushButton:hover {
    background-color: #6868a6;
}

QPushButton:pressed {
    background-color: #4a4a8c;
}

QPushButton:disabled {
    background-color: #3a3a4a;
    color: #888888;
}

QPushButton:checked {
    background-color: #6c6cb0;
    font-weight: bold;
    border-bottom: 2px solid #a0a0ff;
}

QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 1px solid #5f5f8f;
}

QCheckBox::indicator:checked {
    background-color: #6c6cb0;
    border: 1px solid #6c6cb0;
    image: url(check.png);
}

QProgressBar {
    background-color: #2a2a3a;
    border-radius: 4px;
    text-align: center;
    color: #ffffff;
    height: 10px;
}

QProgressBar::chunk {
    background-color: #7c7cff;
    border-radius: 4px;
}

QMenu {
    background: #2a2a3a;
    border: 1px solid #3f3f5f;
    border-radius: 6px;
}

QMenu::item:selected {
    background: #3f3f5f;
}

QTabWidget::pane {
    border: 1px solid #3f3f5f;
    border-radius: 6px;
}

QTabBar::tab {
    background: #2a2a3a;
    padding: 10px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background: #565695;
    color: #ffffff;
}

QComboBox {
    background-color: #2a2a3a;
    border: 1px solid #3f3f5f;
    border-radius: 6px;
    padding: 8px;
    color: #ffffff;
    min-width: 6em;
}

QComboBox:hover {
    border: 1px solid #5f5f8f;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 20px;
    border-left: 1px solid #3f3f5f;
}

QTreeWidget, QListWidget {
    background-color: #2a2a3a;
    border: 1px solid #3f3f5f;
    border-radius: 6px;
    color: #ffffff;
}

QTreeWidget::item, QListWidget::item {
    height: 28px;
    padding: 4px;
}

QTreeWidget::item:selected, QListWidget::item:selected {
    background-color: #565695;
    border-radius: 4px;
}

QScrollBar:vertical {
    border: none;
    background: #2a2a3a;
    width: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #565695;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::handle:vertical:hover {
    background: #6868a6;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
    height: 0px;
}

QScrollBar:horizontal {
    border: none;
    background: #2a2a3a;
    height: 12px;
    margin: 0px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background: #565695;
    min-width: 20px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal:hover {
    background: #6868a6;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
    background: none;
    width: 0px;
}

QWebEngineView {
    background-color: #2a2a3a;
}

QGroupBox {
    border: 1px solid #3f3f5f;
    border-radius: 6px;
    margin-top: 1.5em;
    padding-top: 1em;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 5px;
}

QSplitter::handle {
    background-color: #3f3f5f;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QStatusBar {
    background-color: #2a2a3a;
    color: #c0c0c0;
    border-top: 1px solid #3f3f5f;
}

/* Custom toolbar styling */
QToolBar {
    background-color: #2a2a3a;
    border: none;
    spacing: 6px;
    padding: 4px;
}

QToolButton {
    background-color: transparent;
    border-radius: 4px;
    padding: 4px;
}

QToolButton:hover {
    background-color: #3f3f5f;
}

QToolButton:pressed {
    background-color: #5f5f8f;
}
"""

class AvatarLabel(QLabel):
    """Custom label widget for displaying rounded user avatars."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(40, 40)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("font-size: 24pt; color: #a0a0ff; background: #3f3f5f; border-radius: 20px;")
        # Set default avatar
        self.setText("👤")
    
    def set_avatar(self, url):
        """Load and display an avatar from a URL with rounded corners."""
        if not url:
            self.setText("👤")
            return
            
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
            scaled = round_px.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.setPixmap(scaled)
        except:
            # Set a default placeholder if avatar can't be loaded
            self.setText("👤")
            self.setAlignment(Qt.AlignCenter)
            self.setStyleSheet("font-size: 24pt; color: #a0a0ff; background: #3f3f5f; border-radius: 20px;")

class AccountSelector(QComboBox):
    """Custom combobox for selecting GitHub accounts with built-in token management."""
    user_changed = pyqtSignal(str, dict)  # Signal emitted when user is changed (token, user_data)
    tokens_managed = pyqtSignal()  # Signal emitted when tokens are managed
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background-color: #2a2a3a;
                border: 1px solid #3f3f5f;
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
        """)
        self.all_tokens = {}
        self.load_tokens()
        
        # Connect signal
        self.currentIndexChanged.connect(self.on_index_changed)
        
    def load_tokens(self):
        """Load tokens from environment."""
        self.clear()
        self.all_tokens = {}
        
        # Load .env file
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv(usecwd=True))
        
        # Get all tokens
        for k, v in os.environ.items():
            if k.startswith("GITHUB_TOKEN_"):
                name = k[13:]  # Remove "GITHUB_TOKEN_" prefix
                self.all_tokens[name] = v
                
                # Validate token and get user data
                api = GitHubAPI(v)
                ok, user_data = api.validate_token()
                
                if ok and isinstance(user_data, dict):
                    display_name = f"{name} ({user_data.get('login', 'Unknown')})"
                    # Store user data with the token
                    self.addItem(display_name)
                    self.setItemData(self.count()-1, (v, user_data), Qt.UserRole)
                    
    def on_index_changed(self, index):
        """Handle change of selected account."""
        if index >= 0:
            data = self.itemData(index, Qt.UserRole)
            if data:
                token, user_data = data
                self.user_changed.emit(token, user_data)

class ReadmeCreatorTab(QWidget):
    """Tab for creating and editing GitHub README.md files."""
    def __init__(self, api, user_data):
        super().__init__()
        self.api = api
        self.user_data = user_data
        layout = QVBoxLayout(self)
        
        # Top control row - Repository selector, save button, preview toggle
        top_controls = QHBoxLayout()
        
        
        
        self.repo_selector = QComboBox()
        self.repo_selector.setMinimumWidth(200)
        self.load_repos_btn = QPushButton("Load Repos")
        self.save_btn = QPushButton("Save README")
        self.save_btn.clicked.connect(self.save_readme)
        self.preview_toggle = QPushButton("Preview")
        self.preview_toggle.setCheckable(True)
        self.preview_toggle.toggled.connect(self.toggle_preview)
        
        
        
        
        top_controls.addWidget(self.save_btn)
        top_controls.addWidget(self.preview_toggle)
        top_controls.addStretch()
        
        # Template elements buttons
        template_controls = QHBoxLayout()
        self.template_buttons = [
            ("Table", self.insert_table),
            ("Header", self.insert_header),
            ("List", self.insert_list),
            ("Link", self.insert_link),
            ("Image", self.insert_image),
            ("Code Block", self.insert_code_block),
            ("Badge", self.insert_badge)
        ]
        
        for btn_text, btn_func in self.template_buttons:
            btn = QPushButton(btn_text)
            btn.clicked.connect(btn_func)
            template_controls.addWidget(btn)
        
        # Main editor and preview area
        self.editor_preview = QStackedWidget()
        
        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setPlaceholderText("# Your README.md content here...\n\nStart writing your GitHub README or use the template buttons above.")
        
        # Preview
        self.preview = MarkdownPreview()
        
        self.editor_preview.addWidget(self.editor)
        self.editor_preview.addWidget(self.preview)
        
        # Connect editor changes to preview updates
        self.editor.textChanged.connect(self.update_preview)
        
        # Add everything to the main layout
        layout.addLayout(top_controls)
        layout.addLayout(template_controls)
        layout.addWidget(self.editor_preview)
        
        # Initial state
        self.load_repositories()
    
    def load_repositories(self):
        """Load user repositories into the combo box."""
        self.repo_selector.clear()
        ok, repos = self.api.get_repos()
        if ok and isinstance(repos, list):
            for repo in repos:
                self.repo_selector.addItem(repo["name"])
    
    def toggle_preview(self, checked):
        """Toggle between editor and preview views."""
        if checked:
            # Update preview before switching
            self.update_preview()
            self.editor_preview.setCurrentIndex(1)
            self.preview_toggle.setText("Edit")
        else:
            self.editor_preview.setCurrentIndex(0)
            self.preview_toggle.setText("Preview")
    
    def update_preview(self):
        """Update markdown preview."""
        content = self.editor.toPlainText()
        self.preview.update_preview(content, "markdown")
    
    def save_readme(self):
        """Save README.md to the selected repository."""
        repo_name = self.repo_selector.currentText()
        if not repo_name:
            QMessageBox.warning(self, "Error", "Please select a repository")
            return
        
        content = self.editor.toPlainText()
        owner = self.user_data.get("login", "")
        
        # Check if README.md already exists in the repository
        ok, result = self.api.get_contents(owner, repo_name, "README.md")
        
        if ok and isinstance(result, dict) and "sha" in result:
            # Update existing README
            sha = result["sha"]
            success, msg = self.api.update_file(
                owner, repo_name, "README.md", "Update README.md", content, sha
            )
        else:
            # Create new README
            success, msg = self.api.upload_file(
                owner, repo_name, "README.md", content.encode('utf-8')
            )
        
        if success:
            QMessageBox.information(self, "Success", f"README.md saved to {repo_name}")
        else:
            QMessageBox.warning(self, "Error", f"Failed to save README.md: {msg}")
    
    # Template insertion functions
    def insert_table(self):
        """Insert a markdown table template."""
        table = """
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Row 1    | Data     | Data     |
| Row 2    | Data     | Data     |
| Row 3    | Data     | Data     |
"""
        self.editor.insertPlainText(table)
    
    def insert_header(self):
        """Insert header template."""
        headers = """# Main Header
## Secondary Header
### Tertiary Header
"""
        self.editor.insertPlainText(headers)
    
    def insert_list(self):
        """Insert list template."""
        list_template = """
- Item 1
- Item 2
- Item 3
  - Nested item 1
  - Nested item 2
"""
        self.editor.insertPlainText(list_template)
    
    def insert_link(self):
        """Insert link template."""
        self.editor.insertPlainText("[Link Text](https://example.com)")
    
    def insert_image(self):
        """Insert image template."""
        self.editor.insertPlainText("![Alt Text](https://example.com/image.png)")
    
    def insert_code_block(self):
        """Insert code block template."""
        code_block = """```python
# Python code example
def hello_world():
    print("Hello, GitHub!")
```"""
        self.editor.insertPlainText(code_block)
    
    def insert_badge(self):
        """Insert badge template."""
        badge = "[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)"
        self.editor.insertPlainText(badge)
    
    def insert_hr(self):
        """Insert horizontal rule."""
        self.editor.insertPlainText("\n---\n")


class ModifiedRepoBrowserTab(QWidget):
    """Modified Repo Browser tab with search/replace moved and no New Folder button."""
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

        # Repository selection section with Create New button (not including search/replace anymore)
        top_row = QHBoxLayout()
        
        # Combobox with placeholder text
        self.cmb_repos = QComboBox()
        self.cmb_repos.addItem("Select Repo")
        self.cmb_repos.setItemData(0, QColor(120, 120, 120), Qt.ForegroundRole)
        self.cmb_repos.setCurrentIndex(0)
        self.cmb_repos.currentIndexChanged.connect(self.on_repo_changed)
        
        # Add Create Repository button next to dropdown
        btn_create_repo = QPushButton("Create Repo")
        btn_create_repo.clicked.connect(self.show_create_repo_dialog)
        
        # Add repo controls to top row
        top_row.addWidget(self.cmb_repos)
        top_row.addWidget(btn_create_repo)
        top_row.addStretch()
        
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
        
        # Button group - file operations buttons on left side (No New Folder button)
        button_layout = QHBoxLayout()
        
        # New File button only (No New Folder button)
        self.btn_new_file = QPushButton("New File")
        self.btn_save_file = QPushButton("Save File")
        self.btn_delete_file = QPushButton("Delete File")
        self.btn_delete_folder = QPushButton("Delete Folder")
        
        self.btn_new_file.clicked.connect(self.create_new_file)
        self.btn_save_file.clicked.connect(self.save_current_file)
        self.btn_delete_file.clicked.connect(self.delete_current_file)
        self.btn_delete_folder.clicked.connect(self.delete_current_folder)
        
        button_layout.addWidget(self.btn_new_file)
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
        
        # Find/Replace controls moved here above the editor
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
        self.layout.addLayout(top_row)
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
        """Find text in the editor."""
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
        """Replace selected text in the editor."""
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
        """Replace all occurrences of search text."""
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
        """Create a new file in the current directory."""
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
    
    def delete_current_folder(self):
        """Delete the selected folder."""
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
        """Recursively delete all files in a folder."""
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
        """Show dialog to create a new repository."""
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
        """Create a new repository."""
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
        """Open file browser to select files to upload."""
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Upload")
        if files:
            self.handle_file_drop(files)
    
    def go_back(self):
        """Navigate back to the previous directory."""
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
        """Automatically load repo contents when a repo is selected."""
        if index > 0:  # Skip placeholder item
            self.current_repo = self.cmb_repos.currentText()
            self.current_path = ""
            self.path_history = []
            self.btn_back.setEnabled(False)
            self.path_label.setText("/")
            self.load_directory_contents()
    
    def on_item_double_clicked(self, item, column):
        """Handle double click on tree items (for directory navigation)."""
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
        """Handle files dropped onto the drop area."""
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
                "Success", 
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
        """Update the preview panel based on the current content."""
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
        """Load contents of the current directory path."""
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

class UserWidget(QWidget):
    """Widget displaying a GitHub user with optional actions."""
    unfollow_clicked = pyqtSignal(str)
    
    def __init__(self, username, avatar, show_check=True, show_unfollow=False):
        super().__init__()
        self.username = username
        self.box = QHBoxLayout(self)
        self.box.setContentsMargins(8, 8, 8, 8)
        self.check = QCheckBox()
        self.check.setFixedSize(22, 22)
        
        self.label_img = AvatarLabel()
        self.label_img.setFixedSize(60, 60)
        self.label_img.set_avatar(avatar)
        
        user_layout = QVBoxLayout()
        user_layout.setSpacing(2)
        
        self.label_user = QLabel(username)
        self.label_user.setStyleSheet("font-weight: bold; font-size: 12pt;")
        user_layout.addWidget(self.label_user)
        
        # Add optional info label below username
        self.label_info = QLabel("GitHub User")
        self.label_info.setStyleSheet("color: #a0a0ff; font-size: 9pt;")
        user_layout.addWidget(self.label_info)

        if show_check:
            self.box.addWidget(self.check)
        else:
            self.check.setVisible(False)

        self.box.addWidget(self.label_img)
        self.box.addLayout(user_layout)
        
        # Add unfollow button if requested
        if show_unfollow:
            self.unfollow_btn = QPushButton("Unfollow")
            self.unfollow_btn.setFixedWidth(100)
            self.unfollow_btn.setStyleSheet("background-color: #8f5e5e;")
            self.unfollow_btn.clicked.connect(lambda: self.unfollow_clicked.emit(username))
            self.box.addWidget(self.unfollow_btn)
            
        self.box.addStretch()
        
        # Add hover effect
        self.setAutoFillBackground(True)
        self.normal_bg = self.palette().color(self.backgroundRole())
        self.hover_bg = QColor("#2f2f45")
        
        # Set rounded corners
        self.setStyleSheet("border-radius: 8px; padding: 4px;")
        
    def enterEvent(self, event):
        """Add hover effect."""
        p = self.palette()
        p.setColor(self.backgroundRole(), self.hover_bg)
        self.setPalette(p)
        
    def leaveEvent(self, event):
        """Remove hover effect."""
        p = self.palette()
        p.setColor(self.backgroundRole(), self.normal_bg)
        self.setPalette(p)

    def is_checked(self):
        return self.check.isChecked()

class TokenManagerDialog(QDialog):
    """Dialog for managing GitHub API tokens."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Token Manager")
        self.resize(500, 450)
        self.setStyleSheet(DARK_STYLE)
        
        lay = QVBoxLayout(self)
        lay.setSpacing(15)
        
        # Improved title label
        title_label = QLabel("Manage GitHub API Tokens")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; color: #a0a0ff; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        lay.addWidget(title_label)
        
        form_box = QGroupBox("Add New Token")
        form_box.setStyleSheet("QGroupBox { font-size: 12pt; }")
        f_lay = QFormLayout(form_box)
        f_lay.setSpacing(10)
        f_lay.setContentsMargins(20, 30, 20, 20)
        
        self.ed_name = QLineEdit()
        self.ed_name.setPlaceholderText("Enter a name for this token")
        self.ed_token = QLineEdit()
        self.ed_token.setPlaceholderText("Paste your GitHub API token here")
        self.ed_token.setEchoMode(QLineEdit.Password)
        
        btn_add = QPushButton("Add Token")
        btn_add.setIcon(QIcon.fromTheme("list-add"))
        btn_add.clicked.connect(self.add_token)

        f_lay.addRow("Name:", self.ed_name)
        f_lay.addRow("Token:", self.ed_token)
        f_lay.addRow("", btn_add)
        lay.addWidget(form_box)

        exist_box = QGroupBox("Existing Tokens")
        exist_box.setStyleSheet("QGroupBox { font-size: 12pt; }")
        v_lay = QVBoxLayout(exist_box)
        v_lay.setSpacing(10)
        v_lay.setContentsMargins(20, 30, 20, 20)
        
        self.list_tokens = QListWidget()
        self.list_tokens.setMinimumHeight(150)
        
        # Add edit button for tokens
        edit_hbox = QHBoxLayout()
        self.btn_rem = QPushButton("Remove Selected")
        self.btn_rem.setIcon(QIcon.fromTheme("list-remove"))
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_edit.setIcon(QIcon.fromTheme("document-edit"))
        self.btn_rem.clicked.connect(self.remove_token)
        self.btn_edit.clicked.connect(self.edit_token)
        edit_hbox.addWidget(self.btn_edit)
        edit_hbox.addWidget(self.btn_rem)
        
        v_lay.addWidget(self.list_tokens)
        v_lay.addLayout(edit_hbox)
        lay.addWidget(exist_box)

        # Add nice button layout at bottom
        btn_layout = QHBoxLayout()
        help_btn = QPushButton("How to Get a Token")
        help_btn.setStyleSheet("background-color: #5e8f5e;")
        help_btn.clicked.connect(self.show_token_help)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(help_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(close_btn)
        
        lay.addLayout(btn_layout)
        self.setLayout(lay)

        self.load_tokens()
        
    def show_token_help(self):
        """Show help dialog for getting a GitHub token."""
        help_text = (
            "<h3>How to Get a GitHub API Token</h3>"
            "<ol>"
            "<li>Go to <a href='https://github.com/settings/tokens'>github.com/settings/tokens</a></li>"
            "<li>Click on 'Generate new token'</li>"
            "<li>Give your token a descriptive name</li>"
            "<li>Select these scopes: <b>repo</b>, <b>user</b>, <b>admin:repo_hook</b></li>"
            "<li>Click 'Generate token'</li>"
            "<li>Copy the token and paste it here (you won't see it again!)</li>"
            "</ol>"
        )
        
        msg = QMessageBox(self)
        msg.setWindowTitle("GitHub Token Help")
        msg.setTextFormat(Qt.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def load_tokens(self):
        """Load tokens from .env file."""
        self.list_tokens.clear()
        load_dotenv(find_dotenv(usecwd=True))
        for k in os.environ:
            if k.startswith("GITHUB_TOKEN_"):
                item = QListWidgetItem(k[13:])
                # Add a key icon
                item.setIcon(QIcon.fromTheme("dialog-password"))
                self.list_tokens.addItem(item)

    def add_token(self):
        """Add a new token."""
        name = self.ed_name.text().strip()
        tok = self.ed_token.text().strip()
        if not name or not tok:
            QMessageBox.warning(self, "Invalid Input", "Please enter both a name and a token")
            return
            
        # Validate the token
        api = GitHubAPI(tok)
        ok, check = api.validate_token()
        if not ok:
            QMessageBox.warning(self, "Invalid Token", 
                               f"Could not validate token: {check}\nPlease check your token and try again.")
            return
            
        # Token is valid, save it
        env_file = find_dotenv(usecwd=True)
        if not env_file:
            with open('.env', 'w'):
                pass
            env_file = '.env'
        set_key(env_file, "GITHUB_TOKEN_" + name, tok)
        self.ed_name.clear()
        self.ed_token.clear()
        self.load_tokens()
        
        # Show success message with username
        QMessageBox.information(self, "Token Added", 
                               f"Token added for user: {check['login']}")

    def remove_token(self):
        """Remove the selected token."""
        curr = self.list_tokens.currentItem()
        if curr:
            name = curr.text()
            reply = QMessageBox.question(self, "Confirm Deletion", 
                                        f"Are you sure you want to delete the token '{name}'?",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
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
        """Edit the selected token."""
        curr = self.list_tokens.currentItem()
        if curr:
            old_name = curr.text()
            env_file = find_dotenv(usecwd=True)
            load_dotenv(env_file)
            
            current_token = os.environ.get("GITHUB_TOKEN_" + old_name, "")
            
            # Create an edit dialog to edit both name and token
            edit_dialog = QDialog(self)
            edit_dialog.setWindowTitle("Edit Token")
            edit_dialog.setStyleSheet(DARK_STYLE)
            edit_dialog.resize(400, 200)
            
            dialog_layout = QFormLayout(edit_dialog)
            dialog_layout.setSpacing(15)
            dialog_layout.setContentsMargins(20, 20, 20, 20)
            
            title_label = QLabel("Edit GitHub Token")
            title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #a0a0ff;")
            title_label.setAlignment(Qt.AlignCenter)
            dialog_layout.addRow(title_label)
            
            name_edit = QLineEdit(old_name)
            token_edit = QLineEdit(current_token)
            token_edit.setEchoMode(QLineEdit.Password)
            
            show_token = QCheckBox("Show token")
            show_token.toggled.connect(lambda checked: 
                                    token_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password))
            
            dialog_layout.addRow("Name:", name_edit)
            dialog_layout.addRow("Token:", token_edit)
            dialog_layout.addRow("", show_token)
            
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
                valid, user_data = api.validate_token()
                
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
                    
                    QMessageBox.information(self, "Success", 
                                          f"Token updated successfully for user: {user_data['login']}")
                    self.load_tokens()
                else:
                    QMessageBox.warning(self, "Invalid Token", "The token you entered is invalid")

class LoginWindow(QDialog):
    """Enhanced login window with better aesthetics."""
    def __init__(self):
        super().__init__()
        # Set frameless window
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(DARK_STYLE)
        
        self.resize(550, 350)
        self.move_to_center()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Custom title bar
        title_bar = QWidget()
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet("background-color: #191925;")
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(15, 0, 15, 0)
        
        # Add GitHub icon
        github_icon = QLabel("🔐")
        github_icon.setStyleSheet("font-size: 20pt; color: #a0a0ff;")
        
        title_label = QLabel("GitHub Manager")
        title_label.setStyleSheet("color: white; font-weight: bold; font-size: 14pt;")
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #E81123;
                color: white;
            }
        """)
        close_btn.clicked.connect(self.reject)
        
        title_bar_layout.addWidget(github_icon)
        title_bar_layout.addWidget(title_label)
        title_bar_layout.addStretch()
        title_bar_layout.addWidget(close_btn)
        
        # Content area
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(15)
        
        # Add login prompt

        
        # Existing controls
        self.list_tokens = QListWidget()
        self.list_tokens.setMinimumHeight(150)
        self.btn_login = QPushButton("Login")
        self.btn_login.setEnabled(False)
        self.btn_login.setMinimumHeight(40)
        self.btn_login.setStyleSheet("font-size: 12pt; background-color: #565695;")
        
        self.btn_refresh = QPushButton("Refresh")
        self.btn_manage = QPushButton("Manage Tokens")
        self.btn_edit_token = QPushButton("Edit Token")
        self.btn_edit_token.setEnabled(False)
        self.selected_token = None
        self.selected_user = None

        hl = QHBoxLayout()
        hl.addWidget(self.btn_manage)
        hl.addWidget(self.btn_edit_token)
        hl.addStretch()
        hl.addWidget(self.btn_refresh)

        content_layout.addWidget(self.list_tokens)
        content_layout.addLayout(hl)
        content_layout.addWidget(self.btn_login)

        # Add to main layout
        main_layout.addWidget(title_bar)
        main_layout.addWidget(content, 1)
        
        # Connect signals
        self.btn_login.clicked.connect(self.accept)
        self.btn_refresh.clicked.connect(self.load_tokens)
        self.btn_manage.clicked.connect(self.manage_tokens)
        self.btn_edit_token.clicked.connect(self.edit_selected_token)
        self.list_tokens.itemClicked.connect(self.token_selected)
        self.list_tokens.itemDoubleClicked.connect(self.on_item_double_clicked)

        # Store for dragging the window
        self.drag_pos = None
        
        # Load tokens
        self.load_tokens()
        
    def on_item_double_clicked(self, item):
        """Login when double-clicking an item."""
        if item.data(Qt.UserRole):
            self.accept()
        
    def mousePressEvent(self, event):
        """Handle mouse press events for moving the window."""
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging the window."""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def move_to_center(self):
        """Center the window on the screen."""
        # Get the desktop widget - using an alternative approach without QApplication
        from PyQt5.QtWidgets import QDesktopWidget
        desktop = QDesktopWidget()
        screen_rect = desktop.availableGeometry()
        window_size = self.geometry()
        x = (screen_rect.width() - window_size.width()) // 2
        y = (screen_rect.height() - window_size.height()) // 2
        self.move(x, y)

    def load_tokens(self):
        """Load and display available tokens."""
        self.list_tokens.clear()
        load_dotenv(find_dotenv(usecwd=True))
        
        for k, v in os.environ.items():
            if k.startswith("GITHUB_TOKEN_"):
                api = GitHubAPI(v)
                ok, data = api.validate_token()
                item = QListWidgetItem()
                
                if ok:
                    username = data['login']
                    item.setText(f"{k[13:]} ({username})")
                    item.setIcon(QIcon.fromTheme("user-info"))
                    item.setData(Qt.UserRole, (v, data))
                    
                    # Create custom widget
                    user_widget = QWidget()
                    layout = QHBoxLayout(user_widget)
                    
                    # Avatar
                    avatar = AvatarLabel()
                    avatar.setFixedSize(45, 45)
                    avatar.set_avatar(data.get('avatar_url', ''))
                    
                    # User info
                    user_info = QVBoxLayout()
                    name_label = QLabel(f"<b>{username}</b>")
                    token_label = QLabel(k[13:])
                    token_label.setStyleSheet("color: #a0a0a0; font-size: 9pt;")
                    
                    user_info.addWidget(name_label)
                    user_info.addWidget(token_label)
                    
                    layout.addWidget(avatar)
                    layout.addLayout(user_info, 1)
                    layout.setContentsMargins(15, 15, 15, 15)
                    
                    # Set the custom widget for this item
                    item.setSizeHint(user_widget.sizeHint())
                    self.list_tokens.addItem(item)
                    self.list_tokens.setItemWidget(item, user_widget)
                else:
                    item.setText(f"{k[13:]} (Invalid)")
                    item.setForeground(QColor("#ff6060"))
                    item.setIcon(QIcon.fromTheme("dialog-error"))
                    self.list_tokens.addItem(item)
                    
        if self.list_tokens.count() == 0:
            # No tokens found, show a message
            no_tokens = QListWidgetItem("No tokens found. Click 'Manage Tokens' to add one.")
            no_tokens.setForeground(QColor("#a0a0a0"))
            no_tokens.setTextAlignment(Qt.AlignCenter)
            self.list_tokens.addItem(no_tokens)
            
        self.btn_login.setEnabled(False)
        self.btn_edit_token.setEnabled(False)

    def token_selected(self, item):
        """Handle token selection."""
        d = item.data(Qt.UserRole)
        if d:
            self.selected_token, user_data = d
            self.selected_user = user_data
            self.btn_login.setEnabled(True)
            self.btn_edit_token.setEnabled(True)
            
            # Update login button text
            self.btn_login.setText(f"Login as {user_data['login']}")

    def manage_tokens(self):
        """Open the token manager dialog."""
        dlg = TokenManagerDialog(self)
        if dlg.exec_():
            self.load_tokens()
    
    def edit_selected_token(self):
        """Edit the selected token."""
        if not self.selected_token:
            return
        
        current_item = self.list_tokens.currentItem()
        if not current_item:
            return
            
        token_info = current_item.text()
        token_name = token_info.split(" (")[0]
        
        # Create custom edit dialog
        edit_dialog = QDialog(self)
        edit_dialog.setWindowTitle("Edit Token")
        edit_dialog.setStyleSheet(DARK_STYLE)
        edit_dialog.resize(400, 200)
        
        edit_layout = QVBoxLayout(edit_dialog)
        edit_layout.setContentsMargins(20, 20, 20, 20)
        edit_layout.setSpacing(15)
        
        title_label = QLabel(f"Edit Token: {token_name}")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #a0a0ff;")
        edit_layout.addWidget(title_label)
        
        form_layout = QFormLayout()
        token_edit = QLineEdit(self.selected_token)
        token_edit.setEchoMode(QLineEdit.Password)
        token_edit.setMinimumWidth(300)
        
        show_token = QCheckBox("Show token")
        show_token.toggled.connect(lambda checked: 
                                token_edit.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password))
        
        form_layout.addRow("Token:", token_edit)
        form_layout.addRow("", show_token)
        edit_layout.addLayout(form_layout)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(edit_dialog.accept)
        buttons.rejected.connect(edit_dialog.reject)
        edit_layout.addWidget(buttons)
        
        if edit_dialog.exec_():
            new_token = token_edit.text().strip()
            
            if not new_token:
                QMessageBox.warning(self, "Invalid Token", "Token cannot be empty")
                return
                
            # Validate the token
            api = GitHubAPI(new_token)
            valid, data = api.validate_token()
            
            if valid:
                # Update the token in the .env file
                env_file = find_dotenv(usecwd=True)
                set_key(env_file, "GITHUB_TOKEN_" + token_name, new_token)
                QMessageBox.information(self, "Success", 
                                       f"Token for {token_name} updated successfully")
                self.load_tokens()  # Refresh the list
            else:
                QMessageBox.warning(self, "Invalid Token", "The token you entered is invalid")

class MultiTokenDialog(QDialog):
    """Dialog for selecting multiple tokens for bulk operations."""
    def __init__(self, tokens_dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Tokens")
        self.setStyleSheet(DARK_STYLE)
        self.resize(450, 350)
        self.selected_tokens = []
        self.tokens_dict = tokens_dict

        main_lay = QVBoxLayout(self)
        main_lay.setContentsMargins(20, 20, 20, 20)
        main_lay.setSpacing(15)
        
        title = QLabel("Select Accounts to Use")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #a0a0ff;")
        title.setAlignment(Qt.AlignCenter)
        main_lay.addWidget(title)
        
        description = QLabel("Choose which GitHub accounts to perform this action with")
        description.setStyleSheet("color: #a0a0a0;")
        description.setAlignment(Qt.AlignCenter)
        main_lay.addWidget(description)
        
        self.list_tokens = QListWidget()
        for name in tokens_dict:
            item = QListWidgetItem(name)
            item.setIcon(QIcon.fromTheme("user-info"))
            item.setCheckState(Qt.Unchecked)
            self.list_tokens.addItem(item)
            
        main_lay.addWidget(self.list_tokens)
        
        btn_box = QHBoxLayout()
        select_all = QPushButton("Select All")
        select_all.clicked.connect(self.select_all_tokens)
        
        deselect_all = QPushButton("Deselect All")
        deselect_all.clicked.connect(self.deselect_all_tokens)
        
        btn_box.addWidget(select_all)
        btn_box.addWidget(deselect_all)
        main_lay.addLayout(btn_box)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.on_ok)
        buttons.rejected.connect(self.reject)
        main_lay.addWidget(buttons)
        
    def select_all_tokens(self):
        """Select all tokens in the list."""
        for i in range(self.list_tokens.count()):
            self.list_tokens.item(i).setCheckState(Qt.Checked)
            
    def deselect_all_tokens(self):
        """Deselect all tokens in the list."""
        for i in range(self.list_tokens.count()):
            self.list_tokens.item(i).setCheckState(Qt.Unchecked)

    def on_ok(self):
        """Handle OK button click."""
        self.selected_tokens = []
        for i in range(self.list_tokens.count()):
            item = self.list_tokens.item(i)
            if item.checkState() == Qt.Checked:
                name = item.text()
                tok = self.tokens_dict.get(name, None)
                if tok:
                    self.selected_tokens.append(tok)
        if not self.selected_tokens:
            QMessageBox.warning(self, "No Selection", "Please select at least one account")
        else:
            self.accept()

class DropArea(QWidget):
    """Widget that accepts file drops for uploading to GitHub"""
    fileDrop = pyqtSignal(list)  # Signal emitted when files are dropped

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Container for drop area content
        content = QWidget()
        content.setStyleSheet("""
            background-color: #2a2a3a;
            border: 2px dashed #565695;
            border-radius: 10px;
            padding: 20px;
        """)
        content_layout = QVBoxLayout(content)
        
        # Add icon
        upload_icon = QLabel("📤")
        upload_icon.setStyleSheet("font-size: 32pt; color: #7c7cff;")
        upload_icon.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("Drop files here to upload")
        self.label.setStyleSheet("""
            font-size: 14pt;
            color: #a0a0ff;
        """)
        self.label.setAlignment(Qt.AlignCenter)
        
        subtext = QLabel("or use the Browse button below")
        subtext.setStyleSheet("color: #a0a0a0; font-size: 10pt;")
        subtext.setAlignment(Qt.AlignCenter)
        
        content_layout.addWidget(upload_icon)
        content_layout.addWidget(self.label)
        content_layout.addWidget(subtext)
        
        layout.addWidget(content)
        self.setLayout(layout)
        self.setMinimumHeight(150)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                background-color: rgba(86, 86, 149, 0.2);
            """)
            self.label.setText("Release to upload files")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")
        self.label.setText("Drop files here to upload")

    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if file_paths:
            self.fileDrop.emit(file_paths)
        self.setStyleSheet("")
        self.label.setText("Drop files here to upload")

class MarkdownPreview(QWidget):
    """Widget to preview markdown or code with proper styling."""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Preview WebView
        self.preview = QWebEngineView()
        self.preview.setMinimumHeight(200)
        layout.addWidget(self.preview)
        self.setLayout(layout)
        
        # Enhanced GitHub-style CSS with dark theme
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
                padding: 20px;
                overflow-wrap: break-word;
                word-wrap: break-word;
            }
            .markdown-body img {
                max-width: 100%;
                height: auto;
                border-radius: 6px;
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
                border-radius: 6px;
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
                padding: 8px 13px;
                border: 1px solid #3b434b;
            }
            table tr {
                background-color: #0d1117;
            }
            table tr:nth-child(2n) {
                background-color: #161b22;
            }
            
            /* Links */
            a {
                color: #58a6ff;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            
            /* Lists */
            ul, ol {
                padding-left: 2em;
            }
            
            /* Force content to fit within viewport */
            @media screen and (max-width: 100%) {
                body, .markdown-body {
                    width: 100%;
                    padding: 15px;
                    box-sizing: border-box;
                }
                
                pre, code, table {
                    max-width: 100%;
                    overflow-x: auto;
                    white-space: pre-wrap;
                    word-wrap: break-word;
                }
            }
            
            /* Badge styling */
            .markdown-body img[src*="shields.io"] {
                display: inline-block;
                margin-right: 4px;
            }
            
            /* Dark syntax highlighting */
            .hljs-keyword { color: #ff7b72; }
            .hljs-title { color: #d2a8ff; }
            .hljs-string { color: #a5d6ff; }
            .hljs-number { color: #79c0ff; }
            .hljs-comment { color: #8b949e; }
            .hljs-literal { color: #79c0ff; }
            .hljs-built_in { color: #ffa657; }
            .hljs-type { color: #ff7b72; }
            .hljs-attribute { color: #79c0ff; }
        </style>
        """
        
        self.update_preview("")
        
        # Set fixed zoom to 90%
        self.preview.setZoomFactor(0.9)

    def update_preview(self, content, file_type="markdown", dark_mode=True):
        """Update the preview with the given content."""
        self.current_content = content
        self.current_file_type = file_type
        
        if not content:
            html = f"{self.github_css}<div class='markdown-body'><h3>Preview</h3><p>Content will appear here when you edit the document.</p></div>"
            self.preview.setHtml(html)
            return
            
        if file_type == "markdown":
            # Convert markdown to HTML
            try:
                html_content = markdown.markdown(content, extensions=['tables', 'fenced_code'])
                html = f"{self.github_css}<div class='markdown-body'>{html_content}</div>"
            except Exception as e:
                html = f"{self.github_css}<div class='markdown-body'><h3>Error Rendering Markdown</h3><p>{str(e)}</p></div>"
        else:
            # Detect language for syntax highlighting
            lang_class = ""
            if file_type.lower() == "code":
                # Try to detect language from file extension
                if hasattr(self, 'selected_path') and self.selected_path:
                    ext = os.path.splitext(self.selected_path)[1].lower()
                    if ext in ['.py', '.pyw']:
                        lang_class = "language-python"
                    elif ext in ['.js', '.jsx']:
                        lang_class = "language-javascript"
                    elif ext in ['.html', '.htm']:
                        lang_class = "language-html"
                    elif ext in ['.css']:
                        lang_class = "language-css"
                    elif ext in ['.java']:
                        lang_class = "language-java"
                    elif ext in ['.cpp', '.cc', '.cxx', '.h', '.hpp']:
                        lang_class = "language-cpp"
                    elif ext in ['.json']:
                        lang_class = "language-json"
                    elif ext in ['.md', '.markdown']:
                        lang_class = "language-markdown"
                    elif ext in ['.sh', '.bash']:
                        lang_class = "language-bash"
                    elif ext in ['.xml']:
                        lang_class = "language-xml"
                    elif ext in ['.sql']:
                        lang_class = "language-sql"
                    elif ext in ['.rb']:
                        lang_class = "language-ruby"
                    elif ext in ['.go']:
                        lang_class = "language-go"
                    elif ext in ['.php']:
                        lang_class = "language-php"
                    elif ext in ['.rs']:
                        lang_class = "language-rust"
                    elif ext in ['.ts']:
                        lang_class = "language-typescript"
                    else:
                        lang_class = "language-plaintext"
            
            # For code files, use <pre> with syntax highlighting
            html = f"""
            {self.github_css}
            <div class='markdown-body'>
                <pre><code class="{lang_class}">{content.replace('<', '&lt;').replace('>', '&gt;')}</code></pre>
            </div>
            """
        
        self.preview.setHtml(html)
        # Maintain fixed zoom at 90%
        self.preview.setZoomFactor(0.9)