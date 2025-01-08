import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog,
    QHBoxLayout, QMessageBox, QTextEdit, QScrollArea, QLineEdit, QListWidget,
    QListWidgetItem, QProgressBar, QInputDialog, QGridLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal
import os
import shutil
import datetime
import sys
import appdirs  # Ensure this is installed via pip

def get_app_directory():
    """
    Returns the directory where the application can store data.
    Uses user-specific directories to avoid permission issues.
    """
    app_name = "PlantDiseaseDetector"
    app_author = "YourName"  # Replace with your name or organization
    data_dir = appdirs.user_data_dir(app_name, app_author)
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

# Setup Logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(get_app_directory(), "app_debug.log")),
        logging.StreamHandler()
    ]
)

### NEW: A clickable QFrame class to handle mouse clicks. ###
class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event: QMouseEvent):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

class SP_Function(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"Welcome {self.username} - Plant Disease Detector")
        self.setGeometry(300, 200, 800, 600)
        self.setObjectName("MainAppWindow")  # For styling via QSS

        # Layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(15)

        # Top bar layout
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        # History button
        self.history_button = QPushButton("View History")
        self.history_button.setObjectName("HistoryButton")
        self.history_button.clicked.connect(self.view_history)
        top_bar.addWidget(self.history_button)

        # Create group button
        self.create_group_button = QPushButton("Create Group")
        self.create_group_button.setObjectName("CreateGroupButton")
        self.create_group_button.clicked.connect(self.create_group)
        top_bar.addWidget(self.create_group_button)

        # Stop using group button
        self.stop_group_button = QPushButton("Stop Using Group")
        self.stop_group_button.setObjectName("StopGroupButton")
        self.stop_group_button.clicked.connect(self.stop_using_group)
        self.stop_group_button.setEnabled(False)  # start disabled
        top_bar.addWidget(self.stop_group_button)

        self.layout.addLayout(top_bar)

        # Section label
        self.label = QLabel("Choose an Option:")
        self.label.setObjectName("SectionLabel")
        self.layout.addWidget(self.label)

        # Quick Scan button
        self.quick_scan_button = QPushButton("Quick Scan")
        self.quick_scan_button.setObjectName("QuickScanButton")
        # NOTE: Now only initiates scanning, does NOT open a file dialog.
        self.quick_scan_button.clicked.connect(self.quick_scan)
        self.layout.addWidget(self.quick_scan_button)

        # Enable drag-and-drop
        self.setAcceptDrops(True)
        # Initialize a list to store dragged image paths
        self.dragged_images = []

        # Setup drag-and-drop UI components
        self.setup_drag_drop_ui()

        # History folder and group settings
        app_directory = get_app_directory()
        self.history_folder = os.path.join(app_directory, 'history', self.username)
        os.makedirs(self.history_folder, exist_ok=True)
        self.current_group = None

        # Keep a reference to the history window if opened
        self.history_window = None

        # #Change the theme in the app
        # self.change_theme_button = QPushButton("Dark Mode")
        # self.change_theme_button.setObjectName("theme_change_button")
        # self.change_theme_button.clicked.connect(self.change_theme)
        # top_bar.addWidget(self.change_theme_button)

    def setup_drag_drop_ui(self):
        """Set up the UI components for drag-and-drop functionality."""
        # Label for drag-and-drop area
        drag_drop_label = QLabel("Drag and drop images here OR click the box to select:")
        drag_drop_label.setObjectName("DragDropLabel")
        self.layout.addWidget(drag_drop_label)

        ### UPDATED: Use our ClickableFrame instead of QFrame. ###
        self.drag_drop_frame = ClickableFrame()
        self.drag_drop_frame.setObjectName("DragDropFrame")
        self.drag_drop_frame.setFixedHeight(150)
        # Connect the clicked signal to open the file dialog for image selection
        self.drag_drop_frame.clicked.connect(self.select_images)

        drag_drop_layout = QVBoxLayout(self.drag_drop_frame)
        drag_drop_layout.setContentsMargins(0, 0, 0, 0)
        drag_drop_layout.setSpacing(0)

        drag_drop_instructions = QLabel("Click or drag-and-drop your images into this area")
        drag_drop_instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drag_drop_instructions.setObjectName("DragDropInstructions")
        drag_drop_layout.addWidget(drag_drop_instructions)

        self.layout.addWidget(self.drag_drop_frame)

        # List widget to display dragged images
        self.dragged_images_list = QListWidget()
        self.dragged_images_list.setObjectName("DraggedImagesList")
        ### NEW: Allow extended selection (select multiple items) ###
        self.dragged_images_list.setSelectionMode(self.dragged_images_list.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.dragged_images_list)

        # Buttons to clear or remove selected images
        button_layout = QHBoxLayout()

        clear_dragged_button = QPushButton("Clear ALL Dragged Images")
        clear_dragged_button.setObjectName("ClearDraggedButton")
        clear_dragged_button.clicked.connect(self.clear_dragged_images)
        button_layout.addWidget(clear_dragged_button)

        ### NEW: Remove selected images only ###
        remove_selected_button = QPushButton("Remove Selected")
        remove_selected_button.setObjectName("RemoveSelectedButton")
        remove_selected_button.clicked.connect(self.remove_selected_images)
        button_layout.addWidget(remove_selected_button)

        self.layout.addLayout(button_layout)

    ### NEW: This method opens a file dialog when the user clicks the drag_drop_frame. ###
    def select_images(self):
        """
        Let the user pick images from a file dialog, adding them to the 'dragged_images' list.
        """
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_paths, _ = file_dialog.getOpenFileNames(
            self, "Select Image Files", "", "Images (*.png *.jpg *.jpeg)"
        )

        new_images = 0
        for path in file_paths:
            if path not in self.dragged_images:
                self.dragged_images.append(path)
                self.dragged_images_list.addItem(path)
                new_images += 1

        if new_images > 0:
            QMessageBox.information(self, "Images Added", f"{new_images} image(s) selected.")
        else:
            # Could show a small info message or ignore
            pass

    def clear_dragged_images(self):
        """Clear the list of *all* dragged or selected images."""
        self.dragged_images.clear()
        self.dragged_images_list.clear()
        QMessageBox.information(self, "Cleared", "All dragged images have been cleared.")
        logging.info("Dragged images list cleared by user.")

    ### NEW: Remove only the user-selected images from the list. ###
    def remove_selected_images(self):
        selected_items = self.dragged_images_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please select one or more images to remove.")
            return

        count_removed = 0
        for item in selected_items:
            file_path = item.text()
            if file_path in self.dragged_images:
                self.dragged_images.remove(file_path)
            self.dragged_images_list.takeItem(self.dragged_images_list.row(item))
            count_removed += 1

        QMessageBox.information(self, "Removed", f"Removed {count_removed} selected image(s).")
        logging.info(f"{count_removed} images removed from dragged list.")

    def dragEnterEvent(self, event):
        """Accept the event if it's a file with an image extension."""
        if event.mimeData().hasUrls():
            # Check if at least one of the dragged files is an image
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        """Handle the dropped files."""
        if event.mimeData().hasUrls():
            new_images = 0
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                    if file_path not in self.dragged_images:
                        self.dragged_images.append(file_path)
                        self.dragged_images_list.addItem(file_path)
                        logging.info(f"Image dragged into app: {file_path}")
                        new_images += 1
            if new_images > 0:
                QMessageBox.information(self, "Images Added", f"{new_images} image(s) added via drag-and-drop.")
            else:
                QMessageBox.information(
                    self, "No New Images",
                    "No new images were added. They might already be in the list."
                )

    def create_group(self):
        """Create a group and auto-refresh history."""
        try:
            group_name, ok = QInputDialog.getText(self, "Create Group", "Enter group name:")
            if ok and group_name:
                group_path = os.path.join(self.history_folder, group_name)
                os.makedirs(group_path, exist_ok=True)
                self.current_group = group_path
                self.stop_group_button.setEnabled(True)  # Enable the button
                QMessageBox.information(self, "Success", f"Group '{group_name}' created!")
                logging.info(f"Group created: {group_path}")

                # Auto-refresh history if open
                if self.history_window:
                    self.history_window.load_history()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create group: {str(e)}")
            logging.error(f"Exception in create_group: {e}")

    def stop_using_group(self):
        """Stop grouping images."""
        try:
            self.current_group = None
            self.stop_group_button.setEnabled(False)  # Return to disabled
            QMessageBox.information(self, "Stopped", "You have stopped using the group!")
            logging.info("Stopped using group.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to stop using group: {str(e)}")
            logging.error(f"Exception in stop_using_group: {e}")

    def quick_scan(self):
        """
        Initiate scanning of images that are currently in the dragged_images list.
        No file dialog is opened here now; just processes what’s in self.dragged_images.
        """
        try:
            target_folder = self.current_group if self.current_group else self.history_folder

            all_images = set(self.dragged_images)
            if all_images:
                # Add a progress bar
                progress = QProgressBar()
                progress.setObjectName("QuickScanProgressBar")
                progress.setMaximum(len(all_images))
                progress.setValue(0)
                self.layout.addWidget(progress)

                for i, file_path in enumerate(all_images, start=1):
                    file_name = os.path.basename(file_path)
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    new_file_name = f"{timestamp}_{file_name}"
                    destination_path = os.path.join(target_folder, new_file_name)

                    # Copy each selected file to the target directory
                    shutil.copy(file_path, destination_path)
                    logging.info(f"Image copied to: {destination_path}")

                    # Create description file for each image
                    desc_file = f"{destination_path}.txt"
                    with open(desc_file, 'w') as f:
                        f.write("Enter description here...")
                    logging.debug(f"Description file created for: {new_file_name}")

                    # Update progress
                    progress.setValue(i)

                # Remove the progress bar after completion
                self.layout.removeWidget(progress)
                progress.deleteLater()

                QMessageBox.information(
                    self, "Success", f"{len(all_images)} image(s) saved successfully!"
                )

                # Clear dragged images after scanning
                self.dragged_images.clear()
                self.dragged_images_list.clear()

                # Auto-refresh history if open
                if self.history_window:
                    self.history_window.load_history()
            else:
                QMessageBox.warning(self, "Error", "No images selected or dragged for scanning!")
                logging.warning("Quick Scan attempted with no images selected or dragged.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed during quick scan: {str(e)}")
            logging.error(f"Exception in quick_scan: {e}")

    def view_history(self):
        """Open the history window."""
        try:
            if not self.history_window:
                self.history_window = HistoryWindow(self.history_folder)
            self.history_window.show()
            self.history_window.raise_()
            logging.info("History window opened.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open History window: {str(e)}")
            logging.error(f"Exception in view_history: {e}")


class HistoryWindow(QWidget):
    def __init__(self, history_folder):
        super().__init__()
        self.history_folder = history_folder
        self.setWindowTitle("History")
        self.setGeometry(350, 250, 900, 600)
        self.setObjectName("HistoryWindow")

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        scroll_area.setWidget(self.scroll_widget)

        # Main Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        layout.addWidget(scroll_area)
        self.setLayout(layout)

        # Load History
        self.load_history()

        # Add "Delete All" Button
        delete_all_button = QPushButton("Delete All")
        delete_all_button.setObjectName("DeleteAllButton")
        delete_all_button.clicked.connect(self.delete_all_items)
        delete_all_layout = QHBoxLayout()
        delete_all_layout.addStretch()
        delete_all_layout.addWidget(delete_all_button)
        delete_all_layout.addStretch()
        layout.addLayout(delete_all_layout)

    def load_history(self):
        """Refresh the history layout."""
        try:
            logging.debug("Loading history...")
            # Clear existing items
            for i in reversed(range(self.scroll_layout.count())):
                widget = self.scroll_layout.itemAt(i).widget()
                if widget:
                    widget.setParent(None)

            # Individual Scans
            self.scroll_layout.addWidget(QLabel("Individual Scans:"))
            for file in os.listdir(self.history_folder):
                file_path = os.path.join(self.history_folder, file)
                if os.path.isfile(file_path) and file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    self.scroll_layout.addWidget(self.create_scan_box(file, file_path))
                    logging.debug(f"Added scan box for: {file_path}")

            # Separator
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            self.scroll_layout.addWidget(separator)

            # Groups
            self.scroll_layout.addWidget(QLabel("Groups:"))
            for directory in os.listdir(self.history_folder):
                group_path = os.path.join(self.history_folder, directory)
                if os.path.isdir(group_path):
                    hbox = QHBoxLayout()
                    group_button = QPushButton(directory)
                    group_button.clicked.connect(lambda _, gp=group_path: self.open_group(gp))

                    delete_group = QPushButton("Delete")
                    delete_group.clicked.connect(lambda _, gp=group_path: self.delete_item(gp))

                    hbox.addWidget(group_button)
                    hbox.addWidget(delete_group)

                    wrapper = QWidget()
                    wrapper.setLayout(hbox)
                    self.scroll_layout.addWidget(wrapper)
                    logging.debug(f"Added group box for: {group_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load history: {str(e)}")
            logging.error(f"Exception in load_history: {e}")

    def create_scan_box(self, name, file_path):
        """
        Creates a scan box for individual scans with editable name and description.
        """
        box = QHBoxLayout()
        box.setSpacing(10)

        # Image Thumbnail
        img_label = QLabel()
        img_pixmap = QPixmap(file_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
        img_label.setPixmap(img_pixmap)
        box.addWidget(img_label)

        # Editable Name
        name_edit = QLineEdit(os.path.splitext(name)[0])  # Remove extension for editing
        box.addWidget(name_edit)

        # Editable Description
        desc_edit = QTextEdit()
        desc_file = f"{file_path}.txt"
        if os.path.exists(desc_file):
            with open(desc_file, 'r') as f:
                desc_content = f.read()
                desc_edit.setPlainText(desc_content)
        else:
            desc_edit.setPlainText("Enter description here...")
        box.addWidget(desc_edit)

        # Save Button
        save_button = QPushButton("Save")
        wrapper = QWidget()
        save_button.clicked.connect(
            lambda _, ip=file_path, ne=name_edit, de=desc_edit, wr=wrapper: self.save_changes(ip, ne, de, wr)
        )
        box.addWidget(save_button)

        # Delete Button
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(
            lambda _, ip=file_path, w=wrapper: self.delete_item(ip, w)
        )
        box.addWidget(delete_button)

        # Wrap
        wrapper.setLayout(box)
        return wrapper

    def save_changes(self, img_path, name_edit, desc_edit, wrapper):
        """Save the name and description, and update fields without refreshing the entire window."""
        try:
            logging.debug(f"Saving changes for: {img_path}")
            new_name = name_edit.text().strip()

            # Preserve file extension
            original_extension = os.path.splitext(img_path)[-1]
            if not new_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                new_name += original_extension

            new_path = os.path.join(os.path.dirname(img_path), new_name)
            # Prevent duplicate names
            if os.path.exists(new_path) and new_path != img_path:
                QMessageBox.warning(self, "Error", "A file with this name already exists!")
                logging.warning(f"Duplicate file name attempted: {new_path}")
                return

            # Rename the image file
            os.rename(img_path, new_path)
            logging.info(f"Image renamed from {img_path} to {new_path}")

            # Update the description file
            desc_file = f"{new_path}.txt"
            with open(desc_file, 'w') as f:
                f.write(desc_edit.toPlainText())
            logging.debug(f"Description file updated for: {new_path}")

            QMessageBox.information(self, "Saved", "Changes saved successfully!")
            logging.info(f"Changes saved for: {new_path}")

            # Update UI fields
            name_edit.setText(os.path.splitext(new_name)[0])
            desc_edit.setPlainText(desc_edit.toPlainText())

            # Reconnect the Delete button to the new path
            if wrapper:
                delete_button = None
                for child in wrapper.findChildren(QPushButton):
                    if child.text() == "Delete":
                        delete_button = child
                        break
                if delete_button:
                    delete_button.clicked.disconnect()
                    delete_button.clicked.connect(
                        lambda _, ip=new_path, w=wrapper: self.delete_item(ip, w)
                    )
                    logging.info(f"Delete button reconnected to new path: {new_path}")
                else:
                    logging.error("Delete button not found in wrapper after renaming.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
            logging.error(f"Exception in save_changes: {e}")

    def delete_item(self, path, wrapper=None):
        """Delete an individual scan or a group."""
        try:
            logging.debug(f"Attempting to delete: {path}")
            if os.path.isdir(path):
                shutil.rmtree(path)
                logging.info(f"Group deleted: {path}")
            elif os.path.isfile(path):
                os.remove(path)
                logging.info(f"File deleted: {path}")
                # Also remove .txt if present
                txt_file = f"{path}.txt"
                if os.path.exists(txt_file):
                    os.remove(txt_file)
            else:
                QMessageBox.warning(self, "Warning", "The selected item does not exist.")
                logging.warning(f"Attempted to delete non-existent item: {path}")
                return

            if wrapper:
                wrapper.setParent(None)
                logging.debug("Removed widget from UI.")

            QMessageBox.information(self, "Deleted", "Item deleted successfully!")
            self.load_history()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete item: {str(e)}")
            logging.error(f"Exception in delete_item: {e}")

    def open_group(self, group_path):
        """Open group window as a standalone window."""
        try:
            if not hasattr(self, 'group_windows'):
                self.group_windows = {}  # Persistent storage for group windows

            if group_path not in self.group_windows or self.group_windows[group_path] is None:
                self.group_windows[group_path] = GroupWindow(group_path)
                logging.info(f"Group window created for: {group_path}")

            self.group_windows[group_path].show()
            self.group_windows[group_path].raise_()
            logging.debug(f"Group window shown: {group_path}")

            # Override close event to hide instead of closing
            self.group_windows[group_path].closeEvent = (
                lambda event, gp=group_path: self.hide_group_window(gp)
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open group: {str(e)}")
            logging.error(f"Exception in open_group: {e}")

    def delete_all_items(self):
        """Delete all images, descriptions, and groups in history."""
        try:
            reply = QMessageBox.question(
                self,
                "Delete All",
                "Are you sure you want to delete ALL history items? This cannot be undone!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                for root, dirs, files in os.walk(self.history_folder, topdown=False):
                    for file in files:
                        os.remove(os.path.join(root, file))
                    for directory in dirs:
                        shutil.rmtree(os.path.join(root, directory))

                self.load_history()
                QMessageBox.information(self, "Deleted", "All history items have been deleted!")
                logging.info("All history items deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete all items: {str(e)}")
            logging.error(f"Exception in delete_all_items: {e}")

    def hide_group_window(self, group_path):
        """Hide the group window instead of closing it."""
        try:
            if group_path in self.group_windows:
                self.group_windows[group_path].hide()
                logging.debug(f"Group window hidden: {group_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to hide group window: {str(e)}")
            logging.error(f"Exception in hide_group_window: {e}")


class GroupWindow(QWidget):
    def __init__(self, group_path):
        super().__init__()
        self.group_path = group_path
        self.setWindowTitle(f"Group - {os.path.basename(group_path)}")
        self.setGeometry(350, 250, 900, 600)
        self.setObjectName("GroupWindow")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Title
        group_label = QLabel(f"Group Name: {os.path.basename(group_path)}")
        group_label.setStyleSheet("font-weight: bold; font-size: 18px;")
        layout.addWidget(group_label)

        # Scroll Area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Load Images in Group
        images = [f for f in os.listdir(self.group_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for img in images:
            img_path = os.path.join(self.group_path, img)

            box = QHBoxLayout()
            box.setSpacing(10)

            pixmap = QPixmap(img_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
            img_label = QLabel()
            img_label.setPixmap(pixmap)

            # Editable Name
            name_edit = QLineEdit(os.path.splitext(img)[0])

            # Editable Description
            description_edit = QTextEdit()
            desc_file = f"{img_path}.txt"
            if os.path.exists(desc_file):
                with open(desc_file, 'r') as f:
                    desc_content = f.read()
                    description_edit.setPlainText(desc_content)
            else:
                description_edit.setPlainText("Enter description here...")

            # Save Button
            save_button = QPushButton("Save")
            wrapper = QWidget()

            save_button.clicked.connect(
                lambda _, ip=img_path, ne=name_edit, de=description_edit, wr=wrapper: self.save_changes(ip, ne, de, wr)
            )

            # Delete Button
            delete_button = QPushButton("Delete")
            delete_button.clicked.connect(
                lambda _, ip=img_path, w=wrapper: self.delete_item(ip, w)
            )

            box.addWidget(img_label)
            box.addWidget(name_edit)
            box.addWidget(description_edit)
            box.addWidget(save_button)
            box.addWidget(delete_button)

            wrapper.setLayout(box)
            scroll_layout.addWidget(wrapper)

        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)

    def save_changes(self, img_path, name_edit, desc_edit, wrapper):
        """Save the name and description, and update fields without refreshing the entire window."""
        try:
            logging.debug(f"Saving changes for: {img_path}")
            new_name = name_edit.text().strip()

            original_extension = os.path.splitext(img_path)[-1]
            if not new_name.lower().endswith(('.png', '.jpg', '.jpeg')):
                new_name += original_extension

            new_path = os.path.join(os.path.dirname(img_path), new_name)
            if os.path.exists(new_path) and new_path != img_path:
                QMessageBox.warning(self, "Error", "A file with this name already exists!")
                logging.warning(f"Duplicate file name attempted: {new_path}")
                return

            # Rename the image file
            os.rename(img_path, new_path)
            logging.info(f"Image renamed from {img_path} to {new_path}")

            # Update the description file
            desc_file = f"{new_path}.txt"
            with open(desc_file, 'w') as f:
                f.write(desc_edit.toPlainText())
            logging.debug(f"Description file updated for: {new_path}")

            QMessageBox.information(self, "Saved", "Changes saved successfully!")
            logging.info(f"Changes saved for: {new_path}")

            # Update UI fields
            name_edit.setText(os.path.splitext(new_name)[0])
            desc_edit.setPlainText(desc_edit.toPlainText())

            # Reconnect the Delete button
            if wrapper:
                delete_button = None
                for child in wrapper.findChildren(QPushButton):
                    if child.text() == "Delete":
                        delete_button = child
                        break
                if delete_button:
                    delete_button.clicked.disconnect()
                    delete_button.clicked.connect(
                        lambda _, ip=new_path, w=wrapper: self.delete_item(ip, w)
                    )
                    logging.info(f"Delete button reconnected to new path: {new_path}")
                else:
                    logging.error("Delete button not found in wrapper after renaming.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save changes: {str(e)}")
            logging.error(f"Exception in save_changes: {e}")

    def delete_item(self, img_path, wrapper=None):
        """Delete the selected image and remove it from the UI."""
        try:
            logging.debug(f"Attempting to delete: {img_path}")
            if os.path.isfile(img_path):
                os.remove(img_path)
                logging.info(f"Image deleted: {img_path}")
            else:
                QMessageBox.warning(self, "Warning", "The image file does not exist.")
                logging.warning(f"Attempted to delete non-existent image: {img_path}")
                return

            desc_file = f"{img_path}.txt"
            if os.path.exists(desc_file):
                os.remove(desc_file)
                logging.debug(f"Description file deleted: {desc_file}")

            if wrapper:
                wrapper.setParent(None)
                logging.debug(f"Removed widget from UI: {img_path}")

            QMessageBox.information(self, "Deleted", "Image deleted successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete image: {str(e)}")
            logging.error(f"Exception in delete_item: {e}")

def main():
    app = QApplication(sys.argv)

    # ----------------------------------------------------------------------
    #  Global StyleSheet: we added a :disabled state for the "Stop Using Group" button.
    # ----------------------------------------------------------------------
    app.setStyleSheet("""
    /* General application styling */
    QWidget#MainAppWindow, QWidget#HistoryWindow, QWidget#GroupWindow {
        background-color: #f2f2f2;
        font-family: 'Arial';
        font-size: 11pt;
        color: #2c3e50;
    }

    /* Section label (e.g., "Choose an Option") */
    QLabel#SectionLabel {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 10px;
    }

    /* Drag & drop styling */
    QLabel#DragDropLabel {
        font-weight: bold;
        font-size: 12px;
    }
    QFrame#DragDropFrame {
        border: 2px dashed #aaa;
        background-color: #ffffff;
    }
    QLabel#DragDropInstructions {
        font-style: italic;
        color: #666;
    }

    /* QListWidget for dragged images */
    QListWidget#DraggedImagesList {
        border: 1px solid #ccc;
        background-color: #fff;
    }

    /* Buttons */
    QPushButton {
        background-color: #3498db;
        color: #ffffff;
        border-radius: 4px;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #2980b9;
    }
    QPushButton:pressed {
        background-color: #1F4788;
    }
    /* Disabled buttons clearly appear 'faded' */
    QPushButton:disabled {
        background-color: #cccccc;
        color: #666666;
        border-radius: 4px;
        padding: 6px 12px;
    }

    /* ProgressBar */
    QProgressBar#QuickScanProgressBar {
        border: 1px solid #ccc;
        height: 20px;
        border-radius: 4px;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #3498db;
        width: 10px;
    }
    
    """)

    username = "test_user"  # Replace with actual username handling
    main_app = SP_Function(username)
    main_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()# No code was selected, so we will add a new method to the MainApp class to improve the code.
def improve_code(self):
    # Add your improvement code here
    pass