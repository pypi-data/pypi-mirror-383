"""Dual-panel file manager using prompt_toolkit."""

import os
import asyncio
import hashlib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Optional, Tuple

from prompt_toolkit import Application
from prompt_toolkit.layout import Layout, HSplit, VSplit, DynamicContainer, ScrollOffsets
from prompt_toolkit.widgets import Frame, Label, Box
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.containers import Window, WindowAlign
from prompt_toolkit.styles import Style

from kitech_repository.core.client import KitechClient
from kitech_repository.core.exceptions import AuthenticationError
from kitech_repository.models.repository import Repository
from kitech_repository.models.file import File

# Constants
REPOSITORIES_PER_PAGE = 50


class FilePanel:
    """Base class for file panels."""

    def __init__(self, title: str):
        self.title = title
        self.files: List[File] = []
        self.selected_index = 0
        self.buffer = Buffer()
        self._update_display()

    def _update_display(self, active=False):
        """Update the display content."""
        lines = []

        for i, file in enumerate(self.files):
            marker = "▶" if i == self.selected_index else " "
            icon = "📁" if file.is_directory else "📄"
            lines.append(f"{marker} {icon} {file.name}")

        if not self.files:
            lines.append("No files")

        self.buffer.text = "\n".join(lines)

        # Always update cursor position to match selection
        self._update_cursor_position()

    def _update_cursor_position(self):
        """Update cursor position to match current selection."""
        if not self.files:
            self.buffer.cursor_position = 0
            return

        lines = self.buffer.text.split('\n')
        if 0 <= self.selected_index < len(lines):
            # Calculate cursor position at the beginning of the selected line
            cursor_position = sum(len(line) + 1 for line in lines[:self.selected_index])
            self.buffer.cursor_position = cursor_position
        else:
            self.buffer.cursor_position = 0

    def move_selection(self, direction: int):
        """Move selection up or down."""
        if not self.files:
            return

        old_index = self.selected_index
        self.selected_index = max(0, min(len(self.files) - 1, self.selected_index + direction))

        if old_index != self.selected_index:
            self._update_display()  # This now includes cursor position update

    def get_selected_file(self) -> Optional[File]:
        """Get currently selected file."""
        if 0 <= self.selected_index < len(self.files):
            return self.files[self.selected_index]
        return None


class RemotePanel(FilePanel):
    """Remote repository file panel."""

    def __init__(self, client: KitechClient):
        super().__init__("Remote Files")
        self.client = client
        self.repository: Optional[Repository] = None
        self.current_path = ""
        self.path_history = []
        self.repo_page = 0  # Current repository page
        self.repo_total_count = 0  # Total repository count
        self.has_more_repos = False  # Whether there are more repositories to load
        self.file_page = 0  # Current file page (not implemented yet, files use hasMore)
        self.has_more_files = False  # Whether there are more files to load
        self.all_files = []  # Store all loaded files
        # Test: Set initial text
        self.buffer.text = "Initializing remote panel..."

    async def load_repositories(self, reset_page=False):
        """Load repository list with pagination."""
        try:
            if reset_page:
                self.repo_page = 0

            # Run synchronous client call in thread pool
            with ThreadPoolExecutor() as executor:
                result = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.list_repositories(page=self.repo_page, limit=REPOSITORIES_PER_PAGE)
                )

            repositories = result["repositories"]
            self.repo_total_count = result.get("total_count", 0)

            # Check if there are more repositories
            self.has_more_repos = len(repositories) == REPOSITORIES_PER_PAGE and ((self.repo_page + 1) * REPOSITORIES_PER_PAGE) < self.repo_total_count

            if not repositories:
                self.files = []
                if self.repo_page == 0:
                    self.buffer.text = "No repositories found"
                else:
                    self.buffer.text = "No more repositories"
                return

            # Convert repositories to File objects for display
            repo_files = [
                File(
                    name=repo.name,
                    path=repo.name,
                    size=0,
                    type="folder",
                    last_modified=None
                ) for repo in repositories
            ]

            # Add "Load more..." option if there are more repositories
            if self.has_more_repos:
                repo_files.append(File(
                    name="[Load more repositories...]",
                    path="__LOAD_MORE__",  # Special marker
                    logical_path="__LOAD_MORE__",  # Set logical_path as well
                    size=0,
                    type="folder",
                    last_modified=None
                ))

            self.files = repo_files
            self._repositories = repositories  # Keep original objects
            self.selected_index = 0  # Reset selection when loading repositories
            self._update_display()

        except Exception as e:
            self.files = []
            self.buffer.text = f"Error: {str(e)}\nType: {type(e).__name__}"

    async def enter_repository(self):
        """Enter selected repository."""
        selected = self.get_selected_file()
        if not selected:
            return

        # Ignore ".." in repository list
        if selected.name == "..":
            return

        # Check for special "Load more" option
        if selected.actual_path == "__LOAD_MORE__":
            # Load next page of repositories
            self.repo_page += 1
            await self.load_more_repositories()
            return

        if not hasattr(self, '_repositories') or not self._repositories:
            return

        # Check if "Load more" is selected (it's at the end)
        if self.has_more_repos and self.selected_index == len(self.files) - 1:
            return  # Load more is handled above

        # Adjust index if there's a "Load more" entry at the end
        repo_index = self.selected_index
        if self.has_more_repos and self.selected_index < len(self.files) - 1:
            repo_index = self.selected_index  # Normal index
        elif not self.has_more_repos:
            repo_index = self.selected_index  # Normal index
        else:
            return  # Invalid selection

        if 0 <= repo_index < len(self._repositories):
            self.repository = self._repositories[repo_index]
            self.current_path = ""
            self.path_history = []
            await self.load_files()

    async def load_more_repositories(self):
        """Load more repositories and append to current list."""
        try:
            # Run synchronous client call in thread pool
            with ThreadPoolExecutor() as executor:
                result = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.list_repositories(page=self.repo_page, limit=REPOSITORIES_PER_PAGE)
                )

            new_repositories = result["repositories"]

            if not new_repositories:
                # Remove "Load more..." entry
                if self.files and self.files[-1].name == "[Load more repositories...]":
                    self.files.pop()
                    self._update_display()
                return

            # Remove old "Load more..." entry if it exists
            if self.files and self.files[-1].name == "[Load more repositories...]":
                self.files.pop()

            # Add new repositories
            for repo in new_repositories:
                self.files.append(File(
                    name=repo.name,
                    path=repo.name,
                    size=0,
                    type="folder",
                    last_modified=None
                ))

            # Update repositories list
            self._repositories.extend(new_repositories)

            # Check if there are more repositories
            self.has_more_repos = len(new_repositories) == REPOSITORIES_PER_PAGE and ((self.repo_page + 1) * REPOSITORIES_PER_PAGE) < self.repo_total_count

            # Add "Load more..." if there are more repositories
            if self.has_more_repos:
                self.files.append(File(
                    name="[Load more repositories...]",
                    path="__LOAD_MORE__",
                    logical_path="__LOAD_MORE__",  # Set logical_path as well
                    size=0,
                    type="folder",
                    last_modified=None
                ))

            self._update_display()

        except Exception as e:
            pass  # Error handling will be done in the main manager

    async def load_files(self, reset_files=True):
        """Load files in current path."""
        if not self.repository:
            return

        try:
            # Run synchronous client call in thread pool
            with ThreadPoolExecutor() as executor:
                result = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.list_files(self.repository.id, prefix=self.current_path, limit=100)
                )

            files = result["files"]
            self.has_more_files = result.get("has_more", False)

            # Filter out files with relative paths like ".." that came from API
            filtered_files = []
            for file in files:
                # Skip files that have relative paths as their main identifier
                if file.logical_path in (".", "..") or file.object_name in (".", "..") or file.name in (".", ".."):
                    continue
                filtered_files.append(file)

            if reset_files:
                self.all_files = filtered_files.copy()
            else:
                self.all_files.extend(filtered_files)

            # Always add parent directory (..) at the top
            # If we're in a subdirectory, go to parent directory
            # If we're at repository root, go back to repository list
            display_files = self.all_files.copy()
            if self.current_path:  # If we're in a subdirectory
                # Fix: Split by "/" and remove empty parts, then join back
                path_parts = [p for p in self.current_path.split("/") if p]
                if len(path_parts) > 1:
                    parent_path = "/".join(path_parts[:-1])
                else:
                    parent_path = ""  # Going back to repository root
                display_files.insert(0, File(
                    name="..",
                    path=parent_path,
                    logical_path=parent_path,  # Set logical_path as well
                    size=0,
                    type="folder",
                    last_modified=None
                ))
            else:  # If we're at repository root, add ".." to go back to repository list
                display_files.insert(0, File(
                    name="..",
                    path="__REPOSITORY_LIST__",  # Special marker for repository list
                    logical_path="__REPOSITORY_LIST__",  # Set logical_path as well
                    size=0,
                    type="folder",
                    last_modified=None
                ))

            # Add "Load more..." option if there are more files
            if self.has_more_files:
                display_files.append(File(
                    name="Load more...",
                    path="__LOAD_MORE_FILES__",
                    logical_path="__LOAD_MORE_FILES__",  # Set logical_path as well
                    size=0,
                    type="folder",
                    last_modified=None
                ))

            self.files = display_files
            # Reset selection index when loading new files
            if reset_files:
                self.selected_index = 0
            self._update_display()
        except Exception as e:
            import traceback
            self.files = []
            self.selected_index = 0
            error_msg = f"Error loading files: {str(e)}\n"
            error_msg += f"Type: {type(e).__name__}\n"
            error_msg += f"Repo ID: {self.repository.id if self.repository else 'None'}\n"
            error_msg += f"Path: {self.current_path}\n"
            error_msg += f"Traceback:\n{traceback.format_exc()}"
            self.buffer.text = error_msg

    async def enter_directory(self):
        """Enter selected directory."""
        selected = self.get_selected_file()
        if selected and selected.is_directory:
            if selected.name == "..":
                # Check if this is the special repository list marker
                if selected.actual_path == "__REPOSITORY_LIST__":
                    # Go back to repository list
                    self.repository = None
                    self.current_path = ""
                    self.path_history = []
                    await self.load_repositories(reset_page=True)
                else:
                    # Go to parent directory
                    self.current_path = selected.actual_path
                    await self.load_files()
            else:
                # Enter subdirectory
                self.path_history.append(self.current_path)
                self.current_path = selected.actual_path
                await self.load_files()

    async def load_more_files(self):
        """Load more files in current directory."""
        if not self.repository or not self.has_more_files:
            return

        try:
            # This is a placeholder - the current API doesn't support pagination with offset
            # For now, we'll just reload all files
            await self.load_files(reset_files=True)
        except Exception as e:
            self.buffer.text = f"Error loading more files: {e}"

    async def go_back(self):
        """Go back to parent directory."""
        if self.path_history:
            self.current_path = self.path_history.pop()
            await self.load_files()
        elif self.repository:
            # Go back to repository list
            self.repository = None
            self.current_path = ""
            self.path_history = []
            await self.load_repositories(reset_page=True)


class LocalPanel(FilePanel):
    """Local file system panel."""

    def __init__(self):
        super().__init__("Local Files")
        self.current_path = os.getcwd()
        self.load_files()

    def load_files(self):
        """Load files in current directory."""
        try:
            entries = []

            # Add parent directory entry if not at root (or not at top level on macOS)
            parent_dir = os.path.dirname(self.current_path)
            if parent_dir != self.current_path:  # More robust check than just "/"
                entries.append(File(
                    name="..",
                    path=parent_dir,
                    size=0,
                    is_dir=True,
                    last_modified=None
                ))

            # Add directory contents
            for entry in sorted(os.listdir(self.current_path)):
                full_path = os.path.join(self.current_path, entry)
                try:
                    stat = os.stat(full_path)
                    # Calculate hash for files
                    file_hash = None
                    if os.path.isfile(full_path):
                        file_hash = self._calculate_file_hash(full_path)

                    entries.append(File(
                        name=entry,
                        path=full_path,
                        size=stat.st_size,
                        is_dir=os.path.isdir(full_path),
                        last_modified=None,
                        hash=file_hash
                    ))
                except (OSError, PermissionError):
                    continue

            self.files = entries
            # Reset selection index when loading new files
            if self.selected_index >= len(self.files):
                self.selected_index = 0 if self.files else 0
            self._update_display()
        except Exception as e:
            self.files = []
            self.selected_index = 0
            self.buffer.text = f"Error loading directory: {e}"

    def enter_directory(self):
        """Enter selected directory."""
        selected = self.get_selected_file()
        if selected and selected.is_directory:
            self.current_path = selected.actual_path
            self.load_files()

    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception:
            return None


class DualPanelManager:
    """Main dual-panel file manager application."""

    def __init__(self, repository=None):
        self.client = None
        self.remote_panel = None
        self.local_panel = LocalPanel()
        self.active_panel = "local"  # "local" or "remote"
        self.status_text = "Ready"
        self.selected_repository = repository
        self._pending_download = None  # Store file pending download confirmation
        self._pending_download_all = False  # Store full repository download confirmation
        self._pending_upload = None  # Store file pending upload confirmation
        self._pending_upload_all = False  # Store full directory upload confirmation

        # Create buffers
        self.local_buffer_control = BufferControl(buffer=self.local_panel.buffer)
        self.remote_buffer = Buffer()
        self.remote_buffer.text = "Initializing..."
        self.remote_buffer_control = BufferControl(buffer=self.remote_buffer)

        # Status bar (now supports multiple lines)
        self.status_buffer = Buffer()
        self.status_buffer.text = "Ready"
        self.status_buffer_control = BufferControl(buffer=self.status_buffer)
        self.progress_info = None  # Store progress information (current, total, description)

        # Help bar (two lines)
        self.help_text = "Tab: 패널 전환  Enter: 열기  Q: 종료  F5: 새로고침\nF1: 전체 다운로드  F2: 선택 다운로드  F3: 전체 업로드  F4: 선택 업로드"
        self.help_buffer = Buffer()
        self.help_buffer.text = self.help_text
        self.help_buffer_control = BufferControl(buffer=self.help_buffer)

        # Create styles for active/inactive panels
        self.style = Style.from_dict({
            'active-frame': 'bg:#000000 #00ff00',  # Green border for active
            'inactive-frame': 'bg:#000000 #888888',  # Gray border for inactive
            'cursorline': 'bg:#333333 nounderline',  # Background only, explicitly no underline
            'status': 'bg:#ffffff #000000 bold',  # Bold black text on white background
            'help': 'bg:#ffffff #000000 bold',  # Bold black text on white background for help
            'progress': 'bg:#ffffff #00ff00',  # Green progress bar on white background
        })

        # Create dynamic containers for frames
        self.local_container = DynamicContainer(lambda: self._get_local_frame())
        self.remote_container = DynamicContainer(lambda: self._get_remote_frame())

        self.layout = Layout(
            HSplit([
                Window(height=1, char=' '),  # Top padding (empty line)
                Window(height=2, content=self.help_buffer_control, style="class:help"),  # Help (2 lines)
                Window(height=1, char=' '),  # Bottom padding after help
                VSplit([
                    self.local_container,
                    self.remote_container,
                ]),
                Window(height=1, char=' '),  # Top padding before status
                DynamicContainer(lambda: Window(
                    height=self._get_status_height(),
                    content=self.status_buffer_control,
                    style="class:status"
                )),  # Status at bottom
                Window(height=1, char=' '),  # Bottom padding
            ])
        )

        # Create key bindings
        self.kb = KeyBindings()
        self._setup_key_bindings()

        # Create application
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            full_screen=True,
            style=self.style,
            mouse_support=False,  # Disable mouse to avoid focus issues
            enable_page_navigation_bindings=False,  # Disable default page navigation
        )

    def _get_local_frame(self):
        """Get local panel frame with appropriate style."""
        style_class = "class:active-frame" if self.active_panel == "local" else "class:inactive-frame"
        return Frame(
            Window(
                content=self.local_buffer_control,
                wrap_lines=False,
                scroll_offsets=ScrollOffsets(top=5, bottom=5),  # Keep 5 lines of context when scrolling
            ),
            title="Local Files",
            style=style_class
        )

    def _get_remote_frame(self):
        """Get remote panel frame with appropriate style."""
        style_class = "class:active-frame" if self.active_panel == "remote" else "class:inactive-frame"

        # Use repository name as title if available, otherwise "전체 리포지토리"
        if self.remote_panel and self.remote_panel.repository:
            repo_name = self.remote_panel.repository.name
            # Truncate to 10 characters if too long
            if len(repo_name) > 10:
                title = repo_name[:10] + "..."
            else:
                title = repo_name
        else:
            title = "전체 리포지토리"

        return Frame(
            Window(
                content=self.remote_buffer_control,
                wrap_lines=False,
                scroll_offsets=ScrollOffsets(top=5, bottom=5),  # Keep 5 lines of context when scrolling
            ),
            title=title,
            style=style_class
        )

    def _get_status_height(self):
        """Calculate dynamic status bar height."""
        if self.progress_info:
            return 2  # Status message + progress bar
        else:
            # Count lines in status text
            lines = self.status_buffer.text.count('\n') + 1
            return max(1, min(3, lines))  # Between 1-3 lines

    def update_status(self, message: str):
        """Update status message and display."""
        self.status_text = message
        if self.progress_info:
            # Show status + progress bar
            progress_bar = self._create_progress_bar()
            self.status_buffer.text = f"{message}\n{progress_bar}"
        else:
            self.status_buffer.text = message

    def update_progress(self, current: int, total: int, description: str = ""):
        """Update progress bar display."""
        self.progress_info = (current, total, description)
        progress_bar = self._create_progress_bar()
        if description:
            self.status_buffer.text = f"{description}\n{progress_bar}"
        else:
            self.status_buffer.text = progress_bar
        # Force app to redraw
        self.app.invalidate()

    def clear_progress(self):
        """Clear progress bar and return to normal status."""
        self.progress_info = None
        self.status_buffer.text = self.status_text
        # Force app to redraw
        self.app.invalidate()

    def _create_progress_bar(self) -> str:
        """Create text progress bar."""
        if not self.progress_info:
            return ""

        current, total, description = self.progress_info
        if total == 0:
            return f"Processing... {current}"

        percentage = (current / total) * 100
        bar_width = 40
        filled_width = int((current / total) * bar_width)

        bar = "█" * filled_width + "░" * (bar_width - filled_width)
        return f"[{bar}] {current}/{total} ({percentage:.1f}%)"

    def _setup_key_bindings(self):
        """Setup keyboard shortcuts."""

        @self.kb.add('q')
        def quit_app(event):
            """Quit application."""
            event.app.exit()

        @self.kb.add('s-tab')  # Shift+Tab
        @self.kb.add('c-i')    # Tab key
        @self.kb.add('c-t')    # Ctrl+T (alternative)
        def switch_panel(event):
            """Switch between panels."""
            # Block panel switching if waiting for confirmation
            if self._pending_download or self._pending_download_all or self._pending_upload:
                return
            if self.remote_panel:
                self.active_panel = "remote" if self.active_panel == "local" else "local"
                # Update display to show active state
                self.local_panel._update_display(active=(self.active_panel == "local"))
                self.remote_panel._update_display(active=(self.active_panel == "remote"))

        @self.kb.add('up')
        def move_up(event):
            """Move selection up."""
            # Block navigation if waiting for confirmation
            if self._pending_download or self._pending_download_all or self._pending_upload:
                return
            if self.active_panel == "local":
                self.local_panel.move_selection(-1)
            elif self.remote_panel:
                self.remote_panel.move_selection(-1)

        @self.kb.add('down')
        def move_down(event):
            """Move selection down."""
            # Block navigation if waiting for confirmation
            if self._pending_download or self._pending_download_all or self._pending_upload:
                return
            if self.active_panel == "local":
                self.local_panel.move_selection(1)
            elif self.remote_panel:
                self.remote_panel.move_selection(1)

        @self.kb.add('pageup')
        def page_up(event):
            """Scroll page up."""
            if self.active_panel == "local":
                for _ in range(10):
                    self.local_panel.move_selection(-1)
            elif self.remote_panel:
                for _ in range(10):
                    self.remote_panel.move_selection(-1)

        @self.kb.add('pagedown')
        def page_down(event):
            """Scroll page down."""
            if self.active_panel == "local":
                for _ in range(10):
                    self.local_panel.move_selection(1)
            elif self.remote_panel:
                for _ in range(10):
                    self.remote_panel.move_selection(1)

        @self.kb.add('home')
        def go_to_top(event):
            """Go to first file."""
            if self.active_panel == "local":
                self.local_panel.selected_index = 0
                self.local_panel._update_display()
            elif self.remote_panel:
                self.remote_panel.selected_index = 0
                self.remote_panel._update_display()

        @self.kb.add('end')
        def go_to_bottom(event):
            """Go to last file."""
            if self.active_panel == "local":
                if self.local_panel.files:
                    self.local_panel.selected_index = len(self.local_panel.files) - 1
                    self.local_panel._update_display()
            elif self.remote_panel:
                if self.remote_panel.files:
                    self.remote_panel.selected_index = len(self.remote_panel.files) - 1
                    self.remote_panel._update_display()

        @self.kb.add('enter')
        def enter_item(event):
            """Enter directory or perform action."""
            asyncio.create_task(self._handle_enter())

        @self.kb.add('backspace')
        def go_back(event):
            """Go back to parent directory."""
            if self.active_panel == "remote" and self.remote_panel:
                asyncio.create_task(self.remote_panel.go_back())

        @self.kb.add('f1')
        def download_all(event):
            """Download entire repository."""
            if not self.remote_panel or not self.remote_panel.repository:
                self.update_status("No repository selected")
                return

            # Check if repository has any files (excluding ..)
            files_count = len([f for f in self.remote_panel.files if f.name != ".."])
            if files_count == 0:
                self.update_status("Repository is empty - nothing to download")
                return

            # Show confirmation for entire repository download
            repo_name = self.remote_panel.repository.name
            self.update_status(f"Download entire repository '{repo_name}'? Press 'y' to confirm, 'n' to cancel")
            self._pending_download_all = True

        @self.kb.add('f2')
        def download_file(event):
            """Download selected file from remote to local."""
            if self.active_panel != "remote":
                self.update_status("Switch to remote panel first")
                return
            if not self.remote_panel:
                self.update_status("Remote panel not available")
                return

            selected = self.remote_panel.get_selected_file() if self.remote_panel else None
            if not selected:
                self.update_status("No file selected in remote panel")
                return
            if selected.name == "..":
                self.update_status("Cannot download parent directory marker")
                return

            asyncio.create_task(self._handle_download())

        @self.kb.add('f3')
        def upload_all(event):
            """Upload all files from current local directory to remote."""
            if self.active_panel != "local":
                self.update_status("Switch to local panel first")
                return

            # Get count of items to upload
            files_count = len([f for f in self.local_panel.files if f.name != ".." and not f.is_directory])
            folders_count = len([f for f in self.local_panel.files if f.name != ".." and f.is_directory])

            if files_count == 0 and folders_count == 0:
                self.update_status("No files to upload in current directory")
                return

            # Show confirmation
            total_count = files_count + folders_count
            self.update_status(f"Upload all {total_count} items from current directory? Press 'y' to confirm, 'n' to cancel")
            self._pending_upload_all = True

        @self.kb.add('f4')
        def upload_file(event):
            """Upload selected file from local to remote."""
            if self.active_panel != "local":
                self.update_status("Switch to local panel first")
                return
            asyncio.create_task(self._handle_upload())

        # @self.kb.add('f4')
        # def delete_file(event):
        #     """Delete selected file."""
        #     asyncio.create_task(self._handle_delete())

        @self.kb.add('f5')
        def refresh(event):
            """Refresh current panel."""
            if self.active_panel == "local":
                self.local_panel.load_files()
                self.local_panel._update_display(active=True)
                self.update_status("Local files refreshed")
            elif self.active_panel == "remote" and self.remote_panel:
                asyncio.create_task(self._handle_refresh_remote())

        @self.kb.add('y')
        def confirm_yes(event):
            """Confirm overwrite (yes)."""
            if self._pending_download:
                asyncio.create_task(self._proceed_download())
            elif self._pending_download_all:
                asyncio.create_task(self._proceed_download_all())
            elif self._pending_upload:
                asyncio.create_task(self._proceed_upload())
            elif self._pending_upload_all:
                asyncio.create_task(self._proceed_upload_all())
            else:
                # No pending confirmation - ignore y key
                pass

        @self.kb.add('n')
        def confirm_no(event):
            """Cancel overwrite (no)."""
            if self._pending_download:
                self.update_status("Download cancelled")
                self._pending_download = None
            elif self._pending_download_all:
                self.update_status("Repository download cancelled")
                self._pending_download_all = False
            elif self._pending_upload:
                self.update_status("Upload cancelled")
                self._pending_upload = None
            else:
                # No pending confirmation - ignore n key
                pass

    async def _handle_refresh_remote(self):
        """Handle refresh for remote panel."""
        if self.remote_panel:
            self.update_status("Refreshing remote files...")
            if self.remote_panel.repository:
                await self.remote_panel.load_files()
            else:
                await self.remote_panel.load_repositories()
            self.update_status("Remote files refreshed")

    async def _handle_enter(self):
        """Handle enter key press."""
        if self.active_panel == "local":
            self.local_panel.enter_directory()
        elif self.active_panel == "remote" and self.remote_panel:
            if not self.remote_panel.repository:
                await self.remote_panel.enter_repository()
            else:
                await self.remote_panel.enter_directory()

    async def _handle_delete(self):
        """Handle delete operation."""
        if self.active_panel == "local":
            selected = self.local_panel.get_selected_file()
            if selected and selected.name != "..":
                # Local file deletion
                try:
                    import shutil
                    if selected.is_directory:
                        shutil.rmtree(selected.actual_path)
                        self.update_status(f"Deleted directory: {selected.name}")
                    else:
                        os.remove(selected.actual_path)
                        self.update_status(f"Deleted file: {selected.name}")
                    self.local_panel.load_files()
                    self.local_panel._update_display(active=True)
                except Exception as e:
                    self.update_status(f"Delete failed: {e}")

        elif self.active_panel == "remote" and self.remote_panel:
            selected = self.remote_panel.get_selected_file()
            if selected and selected.name != "..":
                # Remote file deletion - would need API support
                self.update_status("Remote delete not implemented yet")

    async def _handle_sync(self):
        """Handle sync operation between local and remote."""
        if not self.remote_panel or not self.remote_panel.repository:
            return

        self.update_status("Loading files with hash values for sync...")
        try:
            # Reload remote files with hash values for accurate comparison
            with ThreadPoolExecutor() as executor:
                result = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.list_files(
                        self.remote_panel.repository.id,
                        prefix=self.remote_panel.current_path,
                        include_hash=True  # Include hash for sync
                    )
                )

            remote_files_with_hash = result["files"]

            # Reload local files (already have hash calculated)
            self.local_panel.load_files()

            self.update_status("Comparing files...")

            # Compare local and remote files
            local_files = {f.name: f for f in self.local_panel.files if f.name != ".."}
            remote_files = {f.name: f for f in remote_files_with_hash}

            # Files to download
            to_download = []

            # Check files only in remote (need to download)
            for name, file in remote_files.items():
                if name not in local_files and not file.is_directory:
                    to_download.append(file)

            # Check files in both (compare hash)
            for name, remote_file in remote_files.items():
                if name in local_files and not remote_file.is_directory:
                    local_file = local_files[name]
                    # Compare by hash if both have hash values
                    if local_file.hash and remote_file.hash:
                        if local_file.hash != remote_file.hash:
                            # Different hash - download from remote
                            to_download.append(remote_file)

            if len(to_download) == 0:
                self.update_status("Already in sync")
                return

            # Show sync summary
            summary = f"Sync: {len(to_download)} files to download"
            self.update_status(summary)

            # Perform download operations
            for i, file in enumerate(to_download, 1):
                self.update_status(f"Downloading {i}/{len(to_download)}: {file.name}...")
                await self._download_file(file)

            # Refresh both panels
            self.local_panel.load_files()
            self.local_panel._update_display()
            await self.remote_panel.load_files()

            self.update_status("Sync completed")

        except Exception as e:
            self.update_status(f"Sync failed: {e}")

    async def _handle_download_all(self):
        """Download all files from current remote directory (only if hash differs)."""
        if not self.remote_panel or not self.remote_panel.repository:
            return

        self.update_status("Loading files with hash values for comparison...")
        try:
            # Get remote files with hash values
            with ThreadPoolExecutor() as executor:
                result = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.list_files(
                        self.remote_panel.repository.id,
                        prefix=self.remote_panel.current_path,
                        include_hash=True  # Include hash for comparison
                    )
                )

            remote_files_with_hash = result["files"]

            # Reload local files to get current hash values
            self.local_panel.load_files()

            # Compare files
            local_files = {f.name: f for f in self.local_panel.files if f.name != ".." and not f.is_directory}
            files_to_download = []

            for remote_file in remote_files_with_hash:
                if remote_file.is_directory:
                    continue

                # Check if file needs to be downloaded
                if remote_file.name not in local_files:
                    # File doesn't exist locally
                    files_to_download.append(remote_file)
                elif remote_file.hash and local_files[remote_file.name].hash:
                    # Both have hash, compare them
                    if remote_file.hash != local_files[remote_file.name].hash:
                        files_to_download.append(remote_file)

                # Original logic (commented for testing)
                # if remote_file.name not in local_files:
                #     # File doesn't exist locally
                #     print(f"[TUI DEBUG] {remote_file.name} not in local - will download")
                #     files_to_download.append(remote_file)
                # elif remote_file.hash and local_files[remote_file.name].hash:
                #     # Both have hash, compare them
                #     if remote_file.hash != local_files[remote_file.name].hash:
                #         print(f"[TUI DEBUG] {remote_file.name} has different hash - will download")
                #         files_to_download.append(remote_file)
                #     else:
                #         print(f"[TUI DEBUG] {remote_file.name} is up to date")

            if len(files_to_download) == 0:
                self.update_status("All files are up to date")
                return

            self.update_status(f"Found {len(files_to_download)} files to download...")

            # Download files with different hash
            for i, file in enumerate(files_to_download, 1):
                self.update_progress(i, len(files_to_download), f"Downloading: {file.name}")
                await self._download_file(file)

            # Clear progress when done
            self.clear_progress()

            # Refresh local panel
            self.local_panel.load_files()
            self.local_panel._update_display()

            self.update_status(f"Downloaded {len(files_to_download)} files")

        except Exception as e:
            self.update_status(f"Download all failed: {e}")

    async def _handle_download(self):
        """Handle download operation."""
        if not self.remote_panel or self.active_panel != "remote":
            return

        selected = self.remote_panel.get_selected_file()
        if selected and selected.name != "..":
            # Check if file/directory already exists locally
            local_path = Path(self.local_panel.current_path) / selected.name
            if local_path.exists():
                # Show confirmation dialog
                self.update_status(f"'{selected.name}' exists. Press 'y' to overwrite, 'n' to cancel")
                # Wait for user input in the next key press
                self._pending_download = selected
                return

            # Allow downloading both files and directories
            await self._download_file(selected)

    async def _handle_upload_all(self):
        """Handle upload all files from current local directory."""
        if not self.remote_panel or self.active_panel != "local":
            return

        # Get all files in current local directory (excluding ..)
        files_to_upload = [f for f in self.local_panel.files if f.name != ".." and not f.is_directory]
        folders_to_upload = [f for f in self.local_panel.files if f.name != ".." and f.is_directory]

        if not files_to_upload and not folders_to_upload:
            self.update_status("No files to upload in current directory")
            return

        total_count = len(files_to_upload) + len(folders_to_upload)
        self.update_status(f"Uploading {total_count} items from current directory...")

        uploaded = 0
        failed = []

        # Upload all files first
        for file in files_to_upload:
            uploaded += 1
            self.update_progress(uploaded, total_count, f"Uploading ({uploaded}/{total_count}): {file.name}")
            try:
                await self._upload_file(file)
            except Exception as e:
                failed.append((file.name, str(e)))

        # Then upload all folders
        for folder in folders_to_upload:
            uploaded += 1
            self.update_progress(uploaded, total_count, f"Uploading folder ({uploaded}/{total_count}): {folder.name}")
            try:
                await self._upload_folder(folder)
            except Exception as e:
                failed.append((folder.name, str(e)))

        # Clear progress and show summary
        self.clear_progress()

        if failed:
            self.update_status(f"Uploaded {uploaded - len(failed)}/{total_count} items. {len(failed)} failed.")
        else:
            self.update_status(f"Successfully uploaded all {total_count} items")

        # Refresh remote panel
        await self.remote_panel.load_files()

    async def _handle_upload(self):
        """Handle upload operation."""
        if not self.remote_panel or self.active_panel != "local":
            return

        selected = self.local_panel.get_selected_file()
        if selected and selected.name != "..":
            if selected.is_directory:
                # Handle folder upload
                self.update_status(f"Upload folder '{selected.name}' with all contents? Press 'y' to confirm, 'n' to cancel")
                self._pending_upload = selected
            else:
                # Check if file already exists in remote
                remote_files = {f.name: f for f in self.remote_panel.files if f.name != ".."}
                if selected.name in remote_files:
                    # Show confirmation dialog
                    self.update_status(f"'{selected.name}' already exists in remote. Press 'y' to overwrite, 'n' to cancel")
                    self._pending_upload = selected
                    return

                # Upload file
                await self._upload_file(selected)

    async def _proceed_download(self):
        """Proceed with pending download after confirmation."""
        if self._pending_download:
            file_to_download = self._pending_download
            self._pending_download = None
            await self._download_file(file_to_download)

    async def _proceed_download_all(self):
        """Proceed with full repository download after confirmation."""
        if self._pending_download_all:
            self._pending_download_all = False
            self.update_status("Starting repository download...")
            try:
                await self._download_entire_repository()
            except Exception as e:
                self.update_status(f"Repository download failed: {e}")
                self.clear_progress()

    async def _proceed_upload(self):
        """Proceed with pending upload after confirmation."""
        if self._pending_upload:
            file_to_upload = self._pending_upload
            self._pending_upload = None

            if file_to_upload.is_directory:
                await self._upload_folder(file_to_upload)
            else:
                await self._upload_file(file_to_upload)

    async def _proceed_upload_all(self):
        """Proceed with uploading all files after confirmation."""
        if self._pending_upload_all:
            self._pending_upload_all = False
            await self._handle_upload_all()

    async def _download_file(self, file: File):
        """Download a file from remote to local."""
        try:
            # Show initial progress immediately
            if file.is_directory:
                self.update_status(f"Downloading folder: {file.name}...")
            else:
                self.update_progress(0, 100, f"Downloading: {file.name}")
                await asyncio.sleep(0.1)  # Brief pause to show initial state

            # Create download task
            with ThreadPoolExecutor() as executor:
                # Start the download
                download_future = asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.download_file(
                        repository_id=self.remote_panel.repository.id,
                        path=file.actual_path,
                        output_dir=self.local_panel.current_path,
                        show_progress=False,  # Disable progress bar in TUI
                        is_directory=file.is_directory  # Pass directory flag
                    )
                )

                # Show progress animation
                if file.is_directory:
                    # For directories, show dots animation
                    dots = 0
                    while not download_future.done():
                        dots = (dots + 1) % 4
                        status = f"Downloading folder: {file.name}" + "." * dots
                        self.update_status(status)
                        await asyncio.sleep(0.5)
                else:
                    # For files, show animated progress bar
                    progress = 10
                    while not download_future.done():
                        self.update_progress(progress, 100, f"Downloading: {file.name}")
                        progress = min(progress + 15, 90)  # Increment faster
                        await asyncio.sleep(0.2)  # Update more frequently

                # Wait for completion
                result = await download_future

                # Show completion
                if file.is_directory:
                    self.update_status(f"Downloaded folder: {file.name}")
                else:
                    self.update_progress(100, 100, f"Downloading: {file.name}")
                    await asyncio.sleep(0.3)  # Show 100% longer
                    self.clear_progress()
                    self.update_status(f"Downloaded {file.name}")

            # Refresh local panel
            self.local_panel.load_files()
            self.local_panel._update_display()

        except Exception as e:
            self.clear_progress()
            self.update_status(f"Download failed: {e}")

    async def _upload_file(self, file: File, remote_subpath: str = ""):
        """Upload a file from local to remote."""
        try:
            # Show progress bar for upload
            self.update_progress(0, 100, f"Uploading: {file.name}")

            # For folder uploads, remote_subpath contains the folder structure to create
            # For single file uploads, use current_path
            if remote_subpath:
                # Combine current path with subpath for folder uploads
                if self.remote_panel.current_path:
                    full_remote_path = f"{self.remote_panel.current_path}/{remote_subpath}"
                else:
                    full_remote_path = remote_subpath
            else:
                full_remote_path = self.remote_panel.current_path

            with ThreadPoolExecutor() as executor:
                # Simulate progress (since we can't get real progress from sync upload)
                for i in range(0, 90, 20):
                    self.update_progress(i, 100, f"Uploading: {file.name}")
                    await asyncio.sleep(0.1)  # Small delay to show progress

                result = await asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.upload_file(
                        repository_id=self.remote_panel.repository.id,
                        file_path=Path(file.path) if isinstance(file.path, str) else file.path,  # Safely convert to Path
                        remote_path=full_remote_path,
                        show_progress=False  # Disable client progress bar, use TUI progress instead
                    )
                )

                # Complete progress
                self.update_progress(100, 100, f"Uploading: {file.name}")
                await asyncio.sleep(0.2)  # Brief pause to show 100%

            # Clear progress and show completion message
            self.clear_progress()
            self.update_status(f"Uploaded {file.name}")

            # Don't refresh panel during batch upload
            if not remote_subpath:
                await self.remote_panel.load_files()  # Refresh remote panel only for single file upload

        except Exception as e:
            self.clear_progress()
            self.update_status(f"Upload failed: {e}")
            raise  # Re-raise for folder upload to handle

    async def _upload_folder(self, folder: File):
        """Upload an entire folder recursively."""
        try:
            folder_path = Path(folder.path)
            folder_name = folder.name

            # Count total files to upload
            total_files = 0
            files_to_upload = []

            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    total_files += 1
                    file_path = Path(root) / file
                    # Calculate relative path from the folder itself
                    relative_path = file_path.relative_to(folder_path)
                    # Prepend the folder name to maintain structure
                    full_relative_path = Path(folder_name) / relative_path
                    files_to_upload.append((file_path, str(full_relative_path)))

            if total_files == 0:
                self.update_status("Folder is empty - nothing to upload")
                return

            self.update_status(f"Uploading folder '{folder_name}' ({total_files} files)...")

            # Upload all files with progress tracking
            uploaded = 0
            failed = []

            for file_path, relative_path in files_to_upload:
                uploaded += 1
                self.update_progress(uploaded, total_files, f"Uploading ({uploaded}/{total_files}): {file_path.name}")

                try:
                    # Create a File object for the file
                    file_obj = File(
                        name=file_path.name,
                        path=str(file_path),
                        size=file_path.stat().st_size,
                        is_dir=False,
                        last_modified=None
                    )

                    # Upload with the full relative path preserved (including folder structure)
                    # The relative_path already includes folder_name/subfolders/filename
                    # Extract just the directory path (exclude the filename at the end)
                    path_obj = Path(relative_path)
                    # Get parent directory (folder_name/subfolders without the filename)
                    # Add trailing slash if not empty to match API format
                    if path_obj.parent != Path('.'):
                        remote_dir = str(path_obj.parent) + "/"
                    else:
                        remote_dir = ""

                    # Debug logging to file
                    with open("/tmp/upload_debug.log", "a") as f:
                        f.write(f"[DEBUG] Uploading: {file_path.name}\n")
                        f.write(f"[DEBUG] relative_path: {relative_path}\n")
                        f.write(f"[DEBUG] remote_dir: {remote_dir}\n")
                        f.write(f"[DEBUG] current_path: {self.remote_panel.current_path}\n")
                        f.write("---\n")

                    await self._upload_file(file_obj, remote_dir)

                except Exception as e:
                    failed.append((file_path.name, str(e)))
                    continue

            # Clear progress and show summary
            self.clear_progress()

            if failed:
                self.update_status(f"Uploaded {uploaded - len(failed)}/{total_files} files. {len(failed)} failed.")
            else:
                self.update_status(f"Successfully uploaded folder '{folder_name}' ({total_files} files)")

            # Refresh remote panel to show new files
            await self.remote_panel.load_files()

        except Exception as e:
            self.clear_progress()
            self.update_status(f"Folder upload failed: {e}")

    async def _download_entire_repository(self):
        """Download entire repository (all files from root)."""
        if not self.remote_panel or not self.remote_panel.repository:
            return

        try:
            repo_name = self.remote_panel.repository.name

            # Show initial progress bar for repository download
            self.update_progress(0, 100, f"Preparing download: {repo_name}")
            await asyncio.sleep(0.2)

            with ThreadPoolExecutor() as executor:
                download_future = asyncio.get_event_loop().run_in_executor(
                    executor,
                    lambda: self.client.download_file(
                        repository_id=self.remote_panel.repository.id,
                        path=None,  # Download entire repository
                        output_dir=self.local_panel.current_path,
                        show_progress=False,  # Disable progress bar in TUI
                        is_directory=True  # Treat as directory download
                    )
                )

                # Show animated progress bar for repository download
                progress = 10
                while not download_future.done():
                    self.update_progress(progress, 100, f"Downloading repository: {repo_name}")
                    progress = min(progress + 8, 85)  # Slower increment for big downloads
                    await asyncio.sleep(0.4)  # Update every 400ms

                # Wait for download to complete
                result = await download_future

                # Show completion
                self.update_progress(100, 100, f"Downloading repository: {repo_name}")
                await asyncio.sleep(0.5)  # Show 100% for half a second
                self.clear_progress()

            self.update_status(f"Downloaded entire repository '{repo_name}'")
            self.local_panel.load_files()  # Refresh local panel
            self.local_panel._update_display()

        except Exception as e:
            self.clear_progress()
            self.update_status(f"Repository download failed: {e}")

    async def initialize(self):
        """Initialize the file manager."""
        try:
            self.client = KitechClient()
            self.remote_panel = RemotePanel(self.client)

            # Connect remote panel buffer to layout
            self.remote_buffer_control.buffer = self.remote_panel.buffer

            if self.selected_repository:
                # Load files for pre-selected repository
                self.update_status(f"Loading files from {self.selected_repository.name}...")
                self.remote_panel.buffer.text = f"Loading files from {self.selected_repository.name}..."
                self.remote_panel.repository = self.selected_repository
                await self.remote_panel.load_files()
                self.update_status(f"Ready - Repository: {self.selected_repository.name}")
            else:
                # Load repository list
                self.update_status("Loading repositories...")
                self.remote_panel.buffer.text = "Loading repositories..."
                await self.remote_panel.load_repositories()
                self.update_status("Ready")

            # Update display to show initial active panel
            self.local_panel._update_display(active=(self.active_panel == "local"))
            self.remote_panel._update_display(active=(self.active_panel == "remote"))

        except AuthenticationError:
            self.update_status("Authentication required - please login first")
            self.remote_buffer.text = "Authentication required - please login first"
            self.remote_panel = None
        except Exception as e:
            self.update_status(f"Error: {e}")
            self.remote_buffer.text = f"Error: {e}"
            self.remote_panel = None

    async def run(self):
        """Run the file manager."""
        await self.initialize()
        await self.app.run_async()


async def start_dual_panel_manager():
    """Start the dual-panel file manager."""
    manager = DualPanelManager()
    await manager.run()


async def start_dual_panel_manager_with_repo(repository: Repository):
    """Start the dual-panel file manager with pre-selected repository."""
    manager = DualPanelManager(repository=repository)
    await manager.run()