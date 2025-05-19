#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv, find_dotenv
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QStackedWidget, QStatusBar, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor, QIcon

from github_api import GitHubAPI
from ui_components import (
    DARK_STYLE, AvatarLabel, UserWidget, TokenManagerDialog, LoginWindow,
    MultiTokenDialog, DropArea, MarkdownPreview, ReadmeCreatorTab, ModifiedRepoBrowserTab
)
from main_tabs import TitleBar, SidebarWidget, ProfileTab, UsersTab, StarsTab

class CustomMainWindow(QMainWindow):
    """Main application window with modern design and improved navigation."""
    def __init__(self, api, user_data, tokens):
        super().__init__()
        self.api = api
        self.user_data = user_data
        self.all_tokens = tokens
        
        
        # Remove standard window decorations
        self.setWindowFlags(Qt.FramelessWindowHint)
        
        # Set window size and title
        self.setMinimumSize(1200, 750)
        self.setWindowTitle(f"GitHub Manager - {user_data.get('login', '')}")
        
        # Set dark style
        self.setStyleSheet(DARK_STYLE)
        
        # Import the needed components directly from where they're defined
        from main_tabs import TitleBar, SidebarWidget, ProfileTab, UsersTab, StarsTab
        from ui_components import ReadmeCreatorTab, ModifiedRepoBrowserTab
        
        # Create custom title bar
        self.title_bar = TitleBar(self)
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Add title bar to the main layout
        main_layout.addWidget(self.title_bar)
        
        # Create horizontal layout for sidebar and content
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar for navigation
        self.sidebar = SidebarWidget(self)
        
        # Update sidebar with user info
        self.sidebar.update_user_info(
            self.user_data.get('login', ''), 
            self.user_data.get('avatar_url', '')
        )
        
        # Create stacked widget for content
        self.content_stack = QStackedWidget()
        
        # Add sidebar and content stack to layout
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.content_stack, 1)
        
        # Add content layout to main layout
        main_layout.addLayout(content_layout, 1)
        
        # Set central widget
        self.setCentralWidget(main_widget)
        
        # Initialize tabs and sidebar buttons
        self.init_tabs()
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage(f"Logged in as {user_data.get('login', '')}")
        self.setStatusBar(self.status_bar)
        
        # Connect sidebar account selector signals
        self.sidebar.account_selector.user_changed.connect(self.change_user)
        self.sidebar.account_selector.tokens_managed.connect(self.refresh_tokens)

        self.refresh_all_tabs()
        
        # Set app icon if available
        self.setWindowIcon(QIcon.fromTheme("github"))
    
    def refresh_all_tabs(self):
        """Refresh all tabs to ensure they have proper parent references."""
        if hasattr(self, 'users_tab'):
            # Ensure parent_window is set correctly
            self.users_tab.parent_window = self
        if hasattr(self, 'stars_tab'):
            # Ensure parent_window is set correctly
            self.stars_tab.parent_window = self

    def init_tabs(self):
        """Initialize all tabs and sidebar buttons."""
        # Import tab classes directly from their source files
        from main_tabs import ProfileTab, UsersTab, StarsTab
        from ui_components import ReadmeCreatorTab, ModifiedRepoBrowserTab
        
        # Create tabs
        self.profile_tab = ProfileTab(self.api, self.user_data, self)
        self.users_tab = UsersTab(self.api, self.user_data)
        self.stars_tab = StarsTab(self.api, self.user_data)
        self.repo_browser_tab = ModifiedRepoBrowserTab(self.api, self.user_data)
        self.readme_creator_tab = ReadmeCreatorTab(self.api, self.user_data)
        
        # Add tabs to content stack
        self.content_stack.addWidget(self.profile_tab)        # Index 0
        self.content_stack.addWidget(self.users_tab)          # Index 1
        self.content_stack.addWidget(self.stars_tab)          # Index 2
        self.content_stack.addWidget(self.repo_browser_tab)   # Index 3
        self.content_stack.addWidget(self.readme_creator_tab) # Index 4
        
        # Add section label for main navigation
        self.sidebar.add_section_label("Main")
        
        # Add buttons to sidebar with icons
        self.profile_btn = self.sidebar.add_button("Profile", 0, "user-home")
        self.find_users_btn = self.sidebar.add_button("Find Users", 1, "system-search")
        self.star_repos_btn = self.sidebar.add_button("Star Repos", 2, "emblem-favorite")
        
        # Add section label for repository tools
        self.sidebar.add_section_label("Repository Tools")
        
        self.repo_browser_btn = self.sidebar.add_button("Repo Browser", 3, "folder")
        self.readme_creator_btn = self.sidebar.add_button("README Editor", 4, "text-editor")
        
        # Add spacer and stretch
        self.sidebar.add_spacer()
        self.sidebar.add_stretch()
        
        # Connect button signals
        self.sidebar.button_group.buttonClicked.connect(self.on_sidebar_button_clicked)
        
        # Set default tab
        self.profile_btn.setChecked(True)
        self.content_stack.setCurrentIndex(0)
    
    def on_sidebar_button_clicked(self, button):
        """Handle sidebar button clicks."""
        index = button.property("tab_index")
        self.content_stack.setCurrentIndex(index)
        
        # Update status bar with current tab info
        tab_titles = [
            f"Profile - {self.user_data.get('login', '')}",
            "Find and manage GitHub users",
            "Star and unstar repositories",
            f"Browse repository: {self.repo_browser_tab.current_repo if hasattr(self.repo_browser_tab, 'current_repo') else 'None selected'}",
            "Create and edit README files"
        ]
        
        if 0 <= index < len(tab_titles):
            self.status_bar.showMessage(tab_titles[index])
    
    def change_user(self, token, user_data):
        """Change to a different GitHub user."""
        # Update the API and user data
        self.api = GitHubAPI(token)
        self.user_data = user_data
        
        # Update window title
        self.setWindowTitle(f"GitHub Manager - {user_data.get('login', '')}")
        
        # Update sidebar user info
        self.sidebar.update_user_info(
            user_data.get('login', ''),
            user_data.get('avatar_url', '')
        )
        
        # Update status bar
        self.status_bar.showMessage(f"Logged in as {user_data.get('login', '')}")
        
        # Recreate all tabs with new user data
        from main_tabs import ProfileTab, UsersTab, StarsTab
        from ui_components import ReadmeCreatorTab, ModifiedRepoBrowserTab
        
        # Store current tab index
        current_index = self.content_stack.currentIndex()
        
        # Remove existing tabs
        while self.content_stack.count() > 0:
            self.content_stack.removeWidget(self.content_stack.widget(0))
        
        # Create new tabs
        self.profile_tab = ProfileTab(self.api, self.user_data, self)
        self.users_tab = UsersTab(self.api, self.user_data, self)
        self.stars_tab = StarsTab(self.api, self.user_data, self)
        self.repo_browser_tab = ModifiedRepoBrowserTab(self.api, self.user_data)
        self.readme_creator_tab = ReadmeCreatorTab(self.api, self.user_data)
        
        # Add tabs to content stack
        self.content_stack.addWidget(self.profile_tab)
        self.content_stack.addWidget(self.users_tab)
        self.content_stack.addWidget(self.stars_tab)
        self.content_stack.addWidget(self.repo_browser_tab)
        self.content_stack.addWidget(self.readme_creator_tab)
        
        # Restore current tab
        self.content_stack.setCurrentIndex(current_index)
        
        # Show success message
        QMessageBox.information(self, "User Changed", f"Switched to user: {user_data.get('login', '')}")
    
    def refresh_tokens(self):
        """Reload available tokens."""
        self.all_tokens = {}
        load_dotenv(find_dotenv(usecwd=True))
        for k, v in os.environ.items():
            if k.startswith("GITHUB_TOKEN_"):
                self.all_tokens[k[13:]] = v


def main():
    """Main entry point for the application."""
    # Create application
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_STYLE)
    
    # Ensure .env file exists
    envf = find_dotenv(usecwd=True)
    if not envf:
        open('.env', 'w').close()
        envf = '.env'
    
    # Load environment variables
    load_dotenv(envf)
    
    # Collect all GitHub tokens
    all_tokens = {}
    for k, v in os.environ.items():
        if k.startswith("GITHUB_TOKEN_"):
            all_tokens[k[13:]] = v
    
    # Show login window
    lw = LoginWindow()
    if lw.exec_():
        if lw.selected_token and lw.selected_user:
            # Create main window
            mw = CustomMainWindow(GitHubAPI(lw.selected_token), lw.selected_user, all_tokens)
            
            # Center window on screen
            from PyQt5.QtWidgets import QDesktopWidget
            desktop = QDesktopWidget()
            screen_rect = desktop.availableGeometry()
            window_rect = mw.geometry()
            mw.move(
                (screen_rect.width() - window_rect.width()) // 2,
                (screen_rect.height() - window_rect.height()) // 2
            )
            
            # Show window and run application
            mw.show()
            return app.exec_()
    
    # If login failed or was cancelled
    return 0


if __name__ == "__main__":
    sys.exit(main())