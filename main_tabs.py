#!/usr/bin/env python3#!/usr/bin/env python3
from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QProgressBar, QTextEdit, QLineEdit, QFileDialog,
    QGroupBox, QSplitter, QComboBox, QTreeWidget, QTreeWidgetItem, QMessageBox,
    QInputDialog, QStackedWidget, QButtonGroup, QScrollArea, QPlainTextEdit, QStyle,
    QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPainter, QBrush, QPixmap, QColor, QIcon
import os
import base64

from github_api import GitHubAPI
from threads import ActionThread, MultiAccountThread
from ui_components import (
    DARK_STYLE, AvatarLabel, UserWidget, TokenManagerDialog, LoginWindow,
    MultiTokenDialog, DropArea, MarkdownPreview
)

class TitleBar(QWidget):
    """Modern title bar with minimalist design."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(50)
        self.setAutoFillBackground(True)
        
        # Set the background color
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor("#191925"))
        self.setPalette(palette)
        
        # Create layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        # App title with icon
        title_layout = QHBoxLayout()
        app_icon = QLabel("🐙")
        app_icon.setStyleSheet("font-size: 20pt; color: #a0a0ff;")
        
        app_title = QLabel("GitHub Manager")
        app_title.setStyleSheet("font-size: 14pt; font-weight: bold; color: white;")
        
        title_layout.addWidget(app_icon)
        title_layout.addWidget(app_title)
        
        # Window buttons
        self.btn_minimize = QPushButton("—")
        self.btn_minimize.setFixedSize(35, 35)
        self.btn_minimize.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #3f3f5f;
            }
        """)
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(35, 35)
        self.btn_close.setStyleSheet("""
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
        
        # Connect button signals
        self.btn_minimize.clicked.connect(self.parent.showMinimized)
        self.btn_close.clicked.connect(self.parent.close)
        
        # Add widgets to layout
        layout.addLayout(title_layout)
        layout.addStretch()
        layout.addWidget(self.btn_minimize)
        layout.addWidget(self.btn_close)
        
        self.setLayout(layout)
        
    def mousePressEvent(self, event):
        """Handle mouse press events for moving the window."""
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events for dragging the window."""
        if event.buttons() == Qt.LeftButton and hasattr(self, 'drag_pos'):
            self.parent.move(event.globalPos() - self.drag_pos)
            event.accept()

class SidebarWidget(QWidget):
    """Custom sidebar with modern design and improved navigation."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove all margins
        self.layout.setSpacing(0)                   # Remove spacing
        
        # User info section at the top
        self.user_info = QWidget()
        self.user_info.setStyleSheet("background-color: #191925; border-bottom: 1px solid #3f3f5f;")
        user_layout = QVBoxLayout(self.user_info)
        user_layout.setContentsMargins(15, 15, 15, 15)
        
        # User avatar and name
        self.avatar_label = AvatarLabel()
        self.avatar_label.setFixedSize(60, 60)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        
        self.username_label = QLabel("User")
        self.username_label.setStyleSheet("font-size: 14pt; font-weight: bold; color: #a0a0ff;")
        self.username_label.setAlignment(Qt.AlignCenter)
        
        # Account selector combobox
        self.account_selector = QComboBox()
        self.account_selector.setStyleSheet("""
            QComboBox {
                background-color: #2a2a3a;
                border: 1px solid #3f3f5f;
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
        """)
        
        # Manage accounts button
        self.manage_btn = QPushButton("Manage Accounts")
        self.manage_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a2a3a;
                border: 1px solid #3f3f5f;
                border-radius: 6px;
                padding: 8px;
                color: white;
            }
            QPushButton:hover {
                background-color: #3f3f5f;
                border: 1px solid #5f5f8f;
            }
        """)
        
        user_layout.addWidget(self.avatar_label, 0, Qt.AlignCenter)
        user_layout.addWidget(self.username_label, 0, Qt.AlignCenter)
        user_layout.addWidget(self.account_selector)
        user_layout.addWidget(self.manage_btn)
        
        # Add user info section to main layout
        self.layout.addWidget(self.user_info)
        
        # Navigation buttons group
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        
        # Style for sidebar buttons
        self.button_style = """
            QPushButton {
                border: none;
                border-radius: 0;
                text-align: left;
                padding: 12px;
                padding-left: 25px;
                font-size: 12pt;
                background-color: transparent;
                color: #e0e0e0;
            }
            QPushButton:hover {
                background-color: #2a2a3a;
            }
            QPushButton:checked {
                background-color: #292940;
                border-left: 4px solid #a0a0ff;
                padding-left: 21px;
                color: #a0a0ff;
            }
        """
        
        # Create a container for the navigation buttons
        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)
        self.nav_layout.setContentsMargins(0, 15, 0, 0)
        self.nav_layout.setSpacing(5)
        
        # Add a label for the navigation section
        nav_label = QLabel("Navigation")
        nav_label.setStyleSheet("color: #787890; font-size: 10pt; padding-left: 25px; margin-bottom: 5px;")
        self.nav_layout.addWidget(nav_label)
        
        # Add buttons container to main layout
        self.layout.addWidget(self.nav_container, 1)  # 1 = stretch factor
        
        # Footer section with version info
        footer = QWidget()
        footer.setStyleSheet("background-color: #191925; border-top: 1px solid #3f3f5f;")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(15, 10, 15, 10)
        
        version_label = QLabel("GitHub Manager v1.0")
        version_label.setStyleSheet("color: #787890; font-size: 9pt;")
        version_label.setAlignment(Qt.AlignCenter)
        
        footer_layout.addWidget(version_label)
        self.layout.addWidget(footer)
        
        # Set fixed width
        self.setFixedWidth(220)
        self.setStyleSheet("""
            background-color: #1e1e2e;
            border-right: 1px solid #3f3f5f;
        """)
    
    def update_user_info(self, username, avatar_url):
        """Update the user info section with current user data."""
        self.username_label.setText(username)
        self.avatar_label.set_avatar(avatar_url)
    
    def add_button(self, text, index, icon=None):
        """Add a new button to the sidebar."""
        button = QPushButton(text)
        button.setCheckable(True)
        button.setStyleSheet(self.button_style)
        button.setProperty("tab_index", index)
        
        # Add icon if provided
        if icon:
            button.setIcon(QIcon.fromTheme(icon))
            button.setIconSize(QSize(18, 18))
        
        self.button_group.addButton(button)
        self.nav_layout.addWidget(button)
        return button
    
    def add_section_label(self, text):
        """Add a section label to the sidebar."""
        label = QLabel(text)
        label.setStyleSheet("color: #787890; font-size: 10pt; padding-left: 25px; margin-top: 15px; margin-bottom: 5px;")
        self.nav_layout.addWidget(label)
    
    def add_spacer(self):
        """Add a spacer to the sidebar."""
        self.nav_layout.addSpacing(15)
    
    def add_stretch(self):
        """Add a stretch to the bottom of the navigation area."""
        self.nav_layout.addStretch(1)

class ProfileTab(QWidget):
    """Enhanced profile tab with better layout and visual appeal."""
    def __init__(self, api, user_data, parent=None):
        super().__init__(parent)
        self.api = api
        self.user_data = user_data
        self.parent = parent
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Create a scroll area for the entire tab
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Container for all content
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(25)
        
        # Profile card with user info and editable fields
        profile_card = QGroupBox("Profile Information")
        profile_card.setStyleSheet("""
            QGroupBox {
                background-color: #292940;
                border-radius: 10px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #a0a0ff;
                padding: 0 10px;
                background-color: #292940;
            }
        """)
        
        profile_layout = QVBoxLayout(profile_card)
        profile_layout.setSpacing(20)
        
        # Username and avatar row
        header_row = QHBoxLayout()
        
        self.lbl_avatar = AvatarLabel()
        self.lbl_avatar.setFixedSize(80, 80)
        if self.user_data.get('avatar_url'):
            self.lbl_avatar.set_avatar(self.user_data['avatar_url'])
            
        header_info = QVBoxLayout()
        
        # Username (not editable)
        self.username_value = QLabel(self.user_data.get('login', ''))
        self.username_value.setStyleSheet("font-weight: bold; font-size: 18pt; color: white;")
        
        # User type and created date
        user_type = QLabel(f"Type: {self.user_data.get('type', 'User')}")
        user_type.setStyleSheet("color: #a0a0a0; font-size: 10pt;")
        
        if 'created_at' in self.user_data:
            created_date = self.user_data['created_at'].split('T')[0]
            joined = QLabel(f"Joined: {created_date}")
            joined.setStyleSheet("color: #a0a0a0; font-size: 10pt;")
            header_info.addWidget(joined)
        
        header_info.addWidget(self.username_value)
        header_info.addWidget(user_type)
        
        header_row.addWidget(self.lbl_avatar)
        header_row.addLayout(header_info)
        header_row.addStretch()
        
        profile_layout.addLayout(header_row)
        
        # Editable fields in a form layout
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(15)
        
        # Name field
        self.name_edit = QLineEdit(self.user_data.get('name', ''))
        self.name_edit.setPlaceholderText("Your full name")
        form_layout.addRow("Name:", self.name_edit)
        
        # Bio field with character counter
        bio_container = QVBoxLayout()
        self.bio_edit = QTextEdit()
        self.bio_edit.setText(self.user_data.get('bio', ''))
        self.bio_edit.setPlaceholderText("Write a short bio about yourself")
        self.bio_edit.setMaximumHeight(120)
        
        # Character counter for bio
        self.bio_counter = QLabel("0/160 characters")
        self.bio_counter.setStyleSheet("color: #a0a0a0; font-size: 9pt; text-align: right;")
        self.bio_counter.setAlignment(Qt.AlignRight)
        
        # Connect text change to counter update
        self.bio_edit.textChanged.connect(self.update_bio_counter)
        
        bio_container.addWidget(self.bio_edit)
        bio_container.addWidget(self.bio_counter)
        form_layout.addRow("Bio:", bio_container)
        
        # Update counter initially
        self.update_bio_counter()
        
        # Location field with improved styling
        self.location_edit = QLineEdit(self.user_data.get('location', ''))
        self.location_edit.setPlaceholderText("Your location (e.g., San Francisco, CA)")
        form_layout.addRow("Location:", self.location_edit)
        
        # Website field with validation
        self.website_edit = QLineEdit(self.user_data.get('blog', ''))
        self.website_edit.setPlaceholderText("https://example.com")
        form_layout.addRow("Website:", self.website_edit)
        
        # Company field
        self.company_edit = QLineEdit(self.user_data.get('company', ''))
        self.company_edit.setPlaceholderText("Where you work")
        form_layout.addRow("Company:", self.company_edit)
        
        profile_layout.addLayout(form_layout)
        
        # Save button with better styling
        save_button = QPushButton("Save Profile")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #4c8c4a;
                border-radius: 6px;
                padding: 10px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5ca65a;
            }
        """)
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self.save_profile)
        
        profile_layout.addWidget(save_button)
        
        # Add profile card to container
        container_layout.addWidget(profile_card)
        
        # Following section
        following_card = QGroupBox(f"Users You Follow ({self.user_data.get('following', 0)})")
        following_card.setObjectName("following_card")
        following_card.setStyleSheet("""
            QGroupBox {
                background-color: #292940;
                border-radius: 10px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #a0a0ff;
                padding: 0 10px;
                background-color: #292940;
            }
        """)
        
        following_layout = QVBoxLayout(following_card)
        
        # Use a scroll area for the following list
        following_scroll = QScrollArea()
        following_scroll.setWidgetResizable(True)
        following_scroll.setMinimumHeight(300)
        following_scroll.setFrameShape(QScrollArea.NoFrame)
        
        # Container for the user widgets
        self.following_container = QWidget()
        self.following_list_layout = QVBoxLayout(self.following_container)
        self.following_list_layout.setAlignment(Qt.AlignTop)
        self.following_list_layout.setSpacing(10)
        
        following_scroll.setWidget(self.following_container)
        following_layout.addWidget(following_scroll)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Following List")
        refresh_btn.clicked.connect(self.fetch_following)
        following_layout.addWidget(refresh_btn)
        
        container_layout.addWidget(following_card)
        
        # Add container to scroll area
        scroll.setWidget(container)
        self.layout.addWidget(scroll)
        
        # Load following list automatically
        self.fetch_following()

    def update_bio_counter(self):
        """Update the bio character counter."""
        count = len(self.bio_edit.toPlainText())
        limit = 160
        color = "#a0a0a0" if count <= limit else "#ff6060"
        
        self.bio_counter.setText(f"{count}/{limit} characters")
        self.bio_counter.setStyleSheet(f"color: {color}; font-size: 9pt; text-align: right;")
        
    def save_profile(self):
        """Save the profile changes."""
        # Validate website URL
        website = self.website_edit.text().strip()
        if website and not (website.startswith('http://') or website.startswith('https://')):
            website = 'https://' + website
            self.website_edit.setText(website)
        
        # Check bio length
        bio = self.bio_edit.toPlainText()
        if len(bio) > 160:
            QMessageBox.warning(self, "Bio Too Long", 
                               "Your bio exceeds 160 characters. Please shorten it.")
            return
        
        # Save profile
        ok, result = self.api.update_profile(
            name=self.name_edit.text(),
            bio=bio,
            company=self.company_edit.text(),
            location=self.location_edit.text(),
            blog=website
        )
        
        if ok:
            # Update internal user data
            self.user_data.update({
                'name': self.name_edit.text(),
                'bio': bio,
                'company': self.company_edit.text(),
                'location': self.location_edit.text(),
                'blog': website
            })
            
            # Show success message
            msg = QMessageBox(self)
            msg.setWindowTitle("Profile Updated")
            msg.setText("Your GitHub profile has been updated successfully!")
            msg.setIcon(QMessageBox.Information)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            QMessageBox.warning(self, "Error", f"Failed to update profile: {result}")
            
    def unfollow_user(self, username):
        """Unfollow the specified user."""
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
        """Fetch and display the list of users being followed."""
        # Clear existing widgets
        while self.following_list_layout.count():
            child = self.following_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Add loading indicator
        loading = QLabel("Loading following list...")
        loading.setAlignment(Qt.AlignCenter)
        self.following_list_layout.addWidget(loading)
        
        # Fetch following list
        ok, data = self.api.get_following()
        
        # Remove loading indicator
        if self.following_list_layout.count() > 0:
            child = self.following_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        if ok:
            if len(data) == 0:
                # No users being followed
                empty = QLabel("You're not following anyone yet.")
                empty.setAlignment(Qt.AlignCenter)
                empty.setStyleSheet("color: #a0a0a0; padding: 20px;")
                self.following_list_layout.addWidget(empty)
            else:
                # Add user widgets for each followed user
                for u in data:
                    user_widget = UserWidget(
                        u["login"], 
                        u["avatar_url"], 
                        show_check=False,
                        show_unfollow=True
                    )
                    user_widget.unfollow_clicked.connect(self.unfollow_user)
                    user_widget.label_info.setText(f"GitHub User • {u.get('type', 'User')}")
                    self.following_list_layout.addWidget(user_widget)
                
            # Update following count in groupbox title
            following_card = self.findChild(QGroupBox, "following_card")
            if following_card:
                following_card.setTitle(f"Users You Follow ({len(data)})")
        else:
            error_label = QLabel("Failed to fetch following list")
            error_label.setStyleSheet("color: #ff6060; padding: 20px;")
            error_label.setAlignment(Qt.AlignCenter)
            self.following_list_layout.addWidget(error_label)
            
            retry_btn = QPushButton("Retry")
            retry_btn.clicked.connect(self.fetch_following)
            self.following_list_layout.addWidget(retry_btn, 0, Qt.AlignCenter)

class UsersTab(QWidget):
    """Tab for finding and managing GitHub users."""
    def __init__(self, api, user_data):
        super().__init__()
        self.api = api
        self.user_data = user_data
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Search section with improved design
        search_card = QGroupBox("Search Users")
        search_card.setStyleSheet("""
            QGroupBox {
                background-color: #292940;
                border-radius: 10px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #a0a0ff;
                padding: 0 10px;
                background-color: #292940;
            }
        """)
        
        search_layout = QVBoxLayout(search_card)
        search_layout.setSpacing(15)
        
        # Search description
        search_desc = QLabel("Search for GitHub users by username or other criteria")
        search_desc.setStyleSheet("color: #a0a0a0; margin-bottom: 10px;")
        search_layout.addWidget(search_desc)
        
        # Search bar with button
        search_box = QHBoxLayout()
        
        self.ed_search = QLineEdit()
        self.ed_search.setPlaceholderText("Search GitHub users (e.g., 'john' or 'location:london')")
        self.ed_search.setMinimumHeight(40)
        self.ed_search.returnPressed.connect(self.search_users)
        
        btn_search = QPushButton("Search")
        btn_search.setMinimumHeight(40)
        btn_search.setMinimumWidth(100)
        btn_search.clicked.connect(self.search_users)
        
        search_box.addWidget(self.ed_search)
        search_box.addWidget(btn_search)
        
        search_layout.addLayout(search_box)
        
        # Add search tips
        tips_label = QLabel("Tips: Use 'language:python' to find users who code in Python, 'location:london' for location, etc.")
        tips_label.setStyleSheet("color: #a0a0a0; font-size: 9pt; font-style: italic; margin-top: 5px;")
        search_layout.addWidget(tips_label)
        
        layout.addWidget(search_card)
        
        # Results section
        results_card = QGroupBox("Search Results")
        results_card.setStyleSheet("""
            QGroupBox {
                background-color: #292940;
                border-radius: 10px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #a0a0ff;
                padding: 0 10px;
                background-color: #292940;
            }
        """)
        
        results_layout = QVBoxLayout(results_card)
        
        self.list_users = QListWidget()
        self.list_users.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #2a2a45;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #3a3a5f;
                border-radius: 8px;
            }
        """)
        self.list_users.setMinimumHeight(300)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        # First row: selection buttons
        selection_layout = QHBoxLayout()
        btn_all = QPushButton("Select All")
        btn_none = QPushButton("Deselect All")
        
        btn_all.clicked.connect(self.select_all_users)
        btn_none.clicked.connect(self.deselect_all_users)
        
        selection_layout.addWidget(btn_all)
        selection_layout.addWidget(btn_none)
        selection_layout.addStretch()
        
        # Second row: action buttons
        action_layout = QHBoxLayout()
        btn_follow = QPushButton("Follow Selected")
        btn_unfollow = QPushButton("Unfollow Selected")
        btn_multi_follow = QPushButton("Multi-Account Follow")
        btn_multi_unfollow = QPushButton("Multi-Account Unfollow")
        
        btn_follow.setStyleSheet("background-color: #4c8c4a;")
        btn_unfollow.setStyleSheet("background-color: #8c4c4a;")
        btn_multi_follow.setStyleSheet("background-color: #4c648c;")
        btn_multi_unfollow.setStyleSheet("background-color: #8c4c8c;")
        
        btn_follow.clicked.connect(self.follow_selected)
        btn_unfollow.clicked.connect(self.unfollow_selected)
        btn_multi_follow.clicked.connect(self.multi_follow)
        btn_multi_unfollow.clicked.connect(self.multi_unfollow)
        
        action_layout.addWidget(btn_follow)
        action_layout.addWidget(btn_unfollow)
        action_layout.addWidget(btn_multi_follow)
        action_layout.addWidget(btn_multi_unfollow)
        
        # Progress bar with better styling
        self.user_bar = QProgressBar()
        self.user_bar.setMaximumHeight(10)
        self.user_bar.setTextVisible(False)
        
        # Log area
        self.user_log = QTextEdit()
        self.user_log.setReadOnly(True)
        self.user_log.setMaximumHeight(120)
        self.user_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border-radius: 8px;
                padding: 10px;
                color: #a0a0a0;
            }
        """)
        
        results_layout.addWidget(self.list_users)
        results_layout.addLayout(selection_layout)
        results_layout.addLayout(action_layout)
        results_layout.addWidget(self.user_bar)
        results_layout.addWidget(self.user_log)
        
        layout.addWidget(results_card)

    def select_all_users(self):
        """Select all users in the list."""
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w:
                w.check.setChecked(True)

    def deselect_all_users(self):
        """Deselect all users in the list."""
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w:
                w.check.setChecked(False)

    def follow_selected(self):
        """Follow selected users."""
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one user to follow")
            return
            
        self.user_log.clear()
        self.user_bar.setValue(0)
        self.user_log.append(f"Following {len(selected)} users...")
        
        self.follow_thread = ActionThread(self.api, 'follow', selected)
        self.follow_thread.progress.connect(self.update_progress)
        self.follow_thread.done.connect(self.operation_completed)
        self.follow_thread.start()

    def unfollow_selected(self):
        """Unfollow selected users."""
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one user to unfollow")
            return
            
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Confirm Unfollow",
            f"Are you sure you want to unfollow {len(selected)} users?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
            
        self.user_log.clear()
        self.user_bar.setValue(0)
        self.user_log.append(f"Unfollowing {len(selected)} users...")
        
        self.unfollow_thread = ActionThread(self.api, 'unfollow', selected)
        self.unfollow_thread.progress.connect(self.update_progress)
        self.unfollow_thread.done.connect(self.operation_completed)
        self.unfollow_thread.start()

    def multi_follow(self):
        """Follow selected users with multiple accounts."""
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
        
        # Get tokens from parent
        all_tokens = {}
        if hasattr(self.parent(), 'all_tokens'):
            all_tokens = self.parent().all_tokens
        
        if len(all_tokens) <= 1:
            QMessageBox.warning(self, "Not Enough Accounts", 
                               "You need multiple GitHub accounts to use this feature")
            return
            
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one user to follow")
            return
        
        dlg = MultiTokenDialog(all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.user_log.clear()
            self.user_bar.setValue(0)
            self.user_log.append(f"Following {len(selected)} users with {len(tokens)} accounts...")
            
            self.mf_thread = MultiAccountThread(tokens, 'follow', selected)
            self.mf_thread.progress.connect(self.update_progress)
            self.mf_thread.done.connect(self.operation_completed)
            self.mf_thread.start()

    def multi_unfollow(self):
        """Unfollow selected users with multiple accounts."""
        selected = []
        for i in range(self.list_users.count()):
            w = self.list_users.itemWidget(self.list_users.item(i))
            if w and w.is_checked():
                selected.append(w.username)
                
        # Get tokens from parent
        all_tokens = {}
        if hasattr(self.parent(), 'all_tokens'):
            all_tokens = self.parent().all_tokens
            
        if len(all_tokens) <= 1:
            QMessageBox.warning(self, "Not Enough Accounts", 
                               "You need multiple GitHub accounts to use this feature")
            return
            
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select at least one user to unfollow")
            return
            
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Confirm Multi-Account Unfollow",
            f"Are you sure you want to unfollow {len(selected)} users with multiple accounts?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
            
        dlg = MultiTokenDialog(all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.user_log.clear()
            self.user_bar.setValue(0)
            self.user_log.append(f"Unfollowing {len(selected)} users with {len(tokens)} accounts...")
            
            self.muf_thread = MultiAccountThread(tokens, 'unfollow', selected)
            self.muf_thread.progress.connect(self.update_progress)
            self.muf_thread.done.connect(self.operation_completed)
            self.muf_thread.start()
    
    def update_progress(self, progress, message):
        """Update progress bar and log."""
        self.user_bar.setValue(progress)
        self.user_log.append(message)
    
    def operation_completed(self, success, message):
        """Handle completion of an operation."""
        self.user_log.append(message)
        QMessageBox.information(self, "Operation Complete", message)

    def search_users(self):
        """Search for GitHub users."""
        q = self.ed_search.text().strip()
        if not q:
            QMessageBox.warning(self, "Empty Search", "Please enter a search query")
            return
            
        self.list_users.clear()
        self.user_log.clear()
        self.user_log.append(f"Searching for '{q}'...")
        
        # Add loading indicator
        loading_item = QListWidgetItem("Searching...")
        loading_item.setTextAlignment(Qt.AlignCenter)
        self.list_users.addItem(loading_item)

        ok, res = self.api.search_users(q)
        
        # Remove loading indicator
        self.list_users.clear()
        
        if ok:
            if len(res) == 0:
                # No results
                no_results = QListWidgetItem("No users found matching your search")
                no_results.setTextAlignment(Qt.AlignCenter)
                self.list_users.addItem(no_results)
                self.user_log.append("No users found")
            else:
                for user in res:
                    s_ok, ud = self.api.get_user_info(user["login"])
                    av = ud["avatar_url"] if s_ok else user["avatar_url"]
                    item = QListWidgetItem()
                    uw = UserWidget(user["login"], av, show_check=True)
                    
                    # Add additional user info if available
                    if s_ok:
                        location = ud.get("location", "")
                        company = ud.get("company", "")
                        info_text = user["login"]
                        if location and company:
                            info_text = f"{user['type']} • {location} • {company}"
                        elif location:
                            info_text = f"{user['type']} • {location}"
                        elif company:
                            info_text = f"{user['type']} • {company}"
                        else:
                            info_text = f"{user['type']}"
                        uw.label_info.setText(info_text)
                    
                    item.setSizeHint(uw.sizeHint())
                    self.list_users.addItem(item)
                    self.list_users.setItemWidget(item, uw)
                self.user_log.append(f"Found {len(res)} users")
        else:
            self.user_log.append(f"Error: {res}")
            QMessageBox.warning(self, "Search Error", f"Failed to search for users: {res}")

class StarsTab(QWidget):
    """Tab for starring GitHub repositories."""
    def __init__(self, api, user_data):
        super().__init__()
        self.api = api
        self.user_data = user_data
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Repository entry section
        repo_card = QGroupBox("Repository URLs")
        repo_card.setStyleSheet("""
            QGroupBox {
                background-color: #292940;
                border-radius: 10px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #a0a0ff;
                padding: 0 10px;
                background-color: #292940;
            }
        """)
        
        repo_layout = QVBoxLayout(repo_card)
        repo_layout.setSpacing(15)
        
        # Instructions
        instructions = QLabel("Enter GitHub repository URLs, one per line")
        instructions.setStyleSheet("color: #a0a0a0; margin-bottom: 10px;")
        repo_layout.addWidget(instructions)
        
        # Repository text area
        self.ed_repos = QTextEdit()
        self.ed_repos.setPlaceholderText("Example:\nhttps://github.com/user1/repo1\nhttps://github.com/user2/repo2")
        self.ed_repos.setMinimumHeight(150)
        repo_layout.addWidget(self.ed_repos)
        
        # Examples and tips
        examples = QLabel(
            "Format: https://github.com/username/repository or username/repository\n"
            "You can also paste URLs directly from your browser"
        )
        examples.setStyleSheet("color: #a0a0a0; font-size: 9pt; font-style: italic;")
        repo_layout.addWidget(examples)
        
        # Button row
        btn_row = QHBoxLayout()
        
        # Action buttons
        star_btn = QPushButton("Star Repos")
        star_btn.setStyleSheet("background-color: #4c8c4a;")
        star_btn.setIcon(QIcon.fromTheme("bookmark-new"))
        
        unstar_btn = QPushButton("Unstar Repos")
        unstar_btn.setStyleSheet("background-color: #8c4c4a;")
        unstar_btn.setIcon(QIcon.fromTheme("bookmark-remove"))
        
        multi_star_btn = QPushButton("Multi-Account Star")
        multi_star_btn.setStyleSheet("background-color: #4c648c;")
        multi_star_btn.setIcon(QIcon.fromTheme("bookmark-new"))
        
        multi_unstar_btn = QPushButton("Multi-Account Unstar")
        multi_unstar_btn.setStyleSheet("background-color: #8c4c8c;")
        multi_unstar_btn.setIcon(QIcon.fromTheme("bookmark-remove"))
        
        clr_btn = QPushButton("Clear")
        clr_btn.setIcon(QIcon.fromTheme("edit-clear"))

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

        repo_layout.addLayout(btn_row)
        layout.addWidget(repo_card)
        
        # Progress and log section
        log_card = QGroupBox("Operation Log")
        log_card.setStyleSheet("""
            QGroupBox {
                background-color: #292940;
                border-radius: 10px;
                padding: 20px;
                font-size: 14pt;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                color: #a0a0ff;
                padding: 0 10px;
                background-color: #292940;
            }
        """)
        
        log_layout = QVBoxLayout(log_card)
        log_layout.setSpacing(15)
        
        # Progress bar
        self.repo_bar = QProgressBar()
        self.repo_bar.setMaximumHeight(10)
        self.repo_bar.setTextVisible(False)
        log_layout.addWidget(self.repo_bar)
        
        # Log area
        self.repo_log = QTextEdit()
        self.repo_log.setReadOnly(True)
        self.repo_log.setPlaceholderText("Operation logs will appear here")
        self.repo_log.setMinimumHeight(200)
        self.repo_log.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e2e;
                border-radius: 8px;
                padding: 10px;
                color: #a0a0a0;
            }
        """)
        log_layout.addWidget(self.repo_log)
        
        layout.addWidget(log_card)
        
    def update_progress(self, progress, message):
        """Update progress bar and log."""
        self.repo_bar.setValue(progress)
        self.repo_log.append(message)
    
    def operation_completed(self, success, message):
        """Handle completion of an operation."""
        self.repo_log.append(message)
        QMessageBox.information(self, "Operation Complete", message)
        
    def extract_repo_urls(self):
        """Extract and normalize repository URLs from the text area."""
        lines = [l.strip() for l in self.ed_repos.toPlainText().split('\n') if l.strip()]
        if not lines:
            QMessageBox.warning(self, "No Repositories", "Please enter repository URLs")
            return []
            
        # Normalize URLs
        normalized_urls = []
        for line in lines:
            # If it's a GitHub URL, extract the username/repo part
            if "github.com/" in line:
                parts = line.split("github.com/")
                if len(parts) >= 2:
                    user_repo = parts[1].strip('/')
                    if '/' in user_repo:
                        normalized_urls.append(user_repo)
            # If it just looks like username/repo
            elif '/' in line and not line.startswith('http'):
                normalized_urls.append(line)
            # If it's already normalized
            else:
                normalized_urls.append(line)
                
        return normalized_urls
        
    def star_repos(self):
        """Star the repositories listed in the text area."""
        lines = self.extract_repo_urls()
        if not lines:
            return
            
        self.repo_log.clear()
        self.repo_bar.setValue(0)
        self.repo_log.append(f"Starring {len(lines)} repositories...")
        
        self.star_thread = ActionThread(self.api, 'star', lines)
        self.star_thread.progress.connect(self.update_progress)
        self.star_thread.done.connect(self.operation_completed)
        self.star_thread.start()

    def unstar_repos(self):
        """Unstar the repositories listed in the text area."""
        lines = self.extract_repo_urls()
        if not lines:
            return
            
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Confirm Unstar",
            f"Are you sure you want to unstar {len(lines)} repositories?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
            
        self.repo_log.clear()
        self.repo_bar.setValue(0)
        self.repo_log.append(f"Unstarring {len(lines)} repositories...")
        
        self.unstar_thread = ActionThread(self.api, 'unstar', lines)
        self.unstar_thread.progress.connect(self.update_progress)
        self.unstar_thread.done.connect(self.operation_completed)
        self.unstar_thread.start()

    def multi_star(self):
        """Star repositories with multiple accounts."""
        lines = self.extract_repo_urls()
        
        # Get tokens from parent
        all_tokens = {}
        if hasattr(self.parent(), 'all_tokens'):
            all_tokens = self.parent().all_tokens
            
        if len(all_tokens) <= 1:
            QMessageBox.warning(self, "Not Enough Accounts", 
                               "You need multiple GitHub accounts to use this feature")
            return
            
        if not lines:
            return
            
        dlg = MultiTokenDialog(all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.repo_log.clear()
            self.repo_bar.setValue(0)
            self.repo_log.append(f"Starring {len(lines)} repositories with {len(tokens)} accounts...")
            
            self.ms_thread = MultiAccountThread(tokens, 'star', lines)
            self.ms_thread.progress.connect(self.update_progress)
            self.ms_thread.done.connect(self.operation_completed)
            self.ms_thread.start()

    def multi_unstar(self):
        """Unstar repositories with multiple accounts."""
        lines = self.extract_repo_urls()
        
        # Get tokens from parent
        all_tokens = {}
        if hasattr(self.parent(), 'all_tokens'):
            all_tokens = self.parent().all_tokens
            
        if len(all_tokens) <= 1:
            QMessageBox.warning(self, "Not Enough Accounts", 
                               "You need multiple GitHub accounts to use this feature")
            return
            
        if not lines:
            return
            
        # Ask for confirmation
        confirm = QMessageBox.question(
            self,
            "Confirm Multi-Account Unstar",
            f"Are you sure you want to unstar {len(lines)} repositories with multiple accounts?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirm == QMessageBox.No:
            return
            
        dlg = MultiTokenDialog(all_tokens, self)
        if dlg.exec_():
            tokens = dlg.selected_tokens
            self.repo_log.clear()
            self.repo_bar.setValue(0)
            self.repo_log.append(f"Unstarring {len(lines)} repositories with {len(tokens)} accounts...")
            
            self.mus_thread = MultiAccountThread(tokens, 'unstar', lines)
            self.mus_thread.progress.connect(self.update_progress)
            self.mus_thread.done.connect(self.operation_completed)
            self.mus_thread.start()

# Export all tabs for use in main.py
__all__ = [
    'TitleBar', 'SidebarWidget', 'ProfileTab', 'UsersTab', 
    'StarsTab', 'ReadmeCreatorTab', 'ModifiedRepoBrowserTab'
]