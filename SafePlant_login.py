from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, 
    QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QInputDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
import sys
import os
import json
from SafePlant_function import SP_Function


class SafePlant(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Welcome to SafePlant+!")
        self.setGeometry(500, 200, 400, 500)

        # --- Layout Setup ---
        """
        """
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # --- Logo Display ---
        self.logo_display = QLabel(self)
        logo_path = os.path.join(os.path.dirname(__file__), "assets/CV_app_logo.jpeg")
        pixmap = QPixmap(logo_path)
        self.logo_display.setPixmap(pixmap.scaled(150, 150, Qt.AspectRatioMode.KeepAspectRatio))
        self.logo_display.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.logo_display)

        # --- Title ---
        self.header_label = QLabel("Log In/Sign Up!")
        self.header_label.setObjectName("HeaderLabel")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.header_label)

        # --- Username Field ---
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("Username")
        self.input_username.setFixedHeight(35)
        main_layout.addWidget(self.input_username)

        # --- Password Field ---
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setFixedHeight(35)
        main_layout.addWidget(self.input_password)

        # --- Buttons ---
        button_layout = QHBoxLayout()
        self.btn_login = QPushButton("Log In")
        self.btn_login.clicked.connect(self.process_login)
        button_layout.addWidget(self.btn_login)

        self.btn_signup = QPushButton("Sign Up")
        self.btn_signup.clicked.connect(self.register_new_user)
        button_layout.addWidget(self.btn_signup)

        main_layout.addLayout(button_layout)

        # --- Forgot Password ---
        self.btn_reset_password = QPushButton("Reset Password")
        self.btn_reset_password.clicked.connect(self.reset_password)
        self.btn_reset_password.setStyleSheet("margin-bottom: 20px;")
        main_layout.addWidget(self.btn_reset_password)

        description_layout = QVBoxLayout()
        self.app_description = QLabel(
            "<b>Welcome to SafePlant+!</b><br><br>"
            "SafePlant+ is a powerful, user-friendly application that leverages advanced Computer Vision technology to analyze plant health efficiently.<br>"
            "Follow these simple steps to get started:<br>"
        )
        self.app_description.setWordWrap(True)
        self.app_description.setStyleSheet("padding: 10px;")
        description_layout.addWidget(self.app_description)

        # Add numbered steps with styling
        steps = [
            "Sign up or log in to your account.",
            "Upload your plant images by either dragging and dropping them or selecting files manually.",
            "Click 'Quick Scan' to let the AI-powered model, <b>Flora</b> analyze your images.",
            "View and manage scan results in the history section for future reference."
        ]

        for i, step in enumerate(steps, start=1):
            step_label = QLabel(f"<b>{i}.</b> {step}")
            step_label.setStyleSheet("margin: 5px 0;")
            description_layout.addWidget(step_label)

        # Add closing statement
        self.app_description_end = QLabel(
            "We hope SafePlant+ enhances your plant care experience! For questions or feedback, reach out to us at <b>sai.keerthan01@gmail.com</b>.<br>"
            "Thank you for choosing SafePlant+!"
        )
        self.app_description_end.setWordWrap(True)
        self.app_description_end.setStyleSheet("padding: 10px;")
        description_layout.addWidget(self.app_description_end)

        main_layout.addLayout(description_layout)


        # --- Footer ---
        main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        footer = QLabel("Developed by: Lee Xiu Wen, Satini Sai Keerthan, Leong Jun Ming and Tiah Wei Xuan")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("font-size: 10px; margin-top: 15px;")
        main_layout.addWidget(footer)

        # --- Initialize Storage ---
        self.user_data_file = os.path.join(os.path.dirname(__file__), "user_data.json")
        self.load_user_data()

        # --- Set Window Icon ---
        icon_path = os.path.join(os.path.dirname(__file__), "assets/icon.png")
        self.setWindowIcon(QIcon(icon_path))

    # --- Data Handling ---
    def load_user_data(self):
        """Load user credentials."""
        if not os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'w') as file:
                json.dump({}, file)

        try:
            with open(self.user_data_file, 'r') as file:
                self.user_credentials = json.load(file)
        except (json.JSONDecodeError, IOError):
            QMessageBox.critical(self, "Error", "Failed to load user data!")
            self.user_credentials = {}

    def save_user_data(self):
        """Save updated credentials."""
        try:
            with open(self.user_data_file, 'w') as file:
                json.dump(self.user_credentials, file)
        except IOError:
            QMessageBox.critical(self, "Error", "Failed to save user data!")

    # --- Authentication Methods ---
    def process_login(self):
        """Validate login details."""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        if username in self.user_credentials and self.user_credentials[username] == password:
            QMessageBox.information(self, "Success", "Login successful!")
            self.hide()
            self.main_app = SP_Function(username)
            self.main_app.show()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password!")

    def register_new_user(self):
        """Register a new user."""
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Username and password are required!")
        elif username in self.user_credentials:
            QMessageBox.warning(self, "Error", "Username already exists!")
        else:
            self.user_credentials[username] = password
            self.save_user_data()
            QMessageBox.information(self, "Success", "Account created successfully!")

    def reset_password(self):
        """Reset user password."""
        username, ok = QInputDialog.getText(self, "Reset Password", "Enter your username:")
        if ok and username:
            if username in self.user_credentials:
                new_password, ok = QInputDialog.getText(self, "New Password", "Enter new password:")
                if ok and new_password:
                    self.user_credentials[username] = new_password
                    self.save_user_data()
                    QMessageBox.information(self, "Success", "Password updated!")
                else:
                    QMessageBox.warning(self, "Error", "Password cannot be empty!")
            else:
                QMessageBox.warning(self, "Error", "Username not found!")
        else:
            QMessageBox.warning(self, "Error", "Username cannot be empty!")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # --- Stylesheet ---
    app.setStyleSheet("""
        QWidget {
            background-color: #f7f7f7;
            color: #333;
            font-family: 'Verdana';
            font-size: 11pt;
        }
        QLabel#HeaderLabel {
            font-size: 22px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 15px;
        }
        QLineEdit {
            background-color: #fff;
            border: 1px solid #aaa;
            border-radius: 5px;
            padding: 8px;
            font-size: 10pt;
        }
        QPushButton {
            background-color: #5cb85c;
            color: white;
            border-radius: 5px;
            padding: 8px 15px;
        }
        QPushButton:hover {
            background-color: #4cae4c;
        }
        QPushButton:pressed {
            background-color: #398439;
        }
    """)

    # --- Start App ---
    window = SafePlant()
    window.show()
    sys.exit(app.exec())