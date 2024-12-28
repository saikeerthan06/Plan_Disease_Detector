from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QInputDialog
import sys
import os
import json
from main_page_app2 import MainApp  # Import the main app directly


class LoginSignupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login / Sign Up")
        self.setGeometry(300, 200, 400, 300)

        # Create layout
        self.layout = QVBoxLayout()

        # Title label
        self.title_label = QLabel("Welcome! Log in or Sign Up")
        self.layout.addWidget(self.title_label)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.password_input)

        # Buttons
        self.login_button = QPushButton("Log In")
        self.login_button.clicked.connect(self.login)
        self.layout.addWidget(self.login_button)

        self.signup_button = QPushButton("Sign Up")
        self.signup_button.clicked.connect(self.signup)
        self.layout.addWidget(self.signup_button)

        # Forgot password button
        self.forgot_password_button = QPushButton("Forgot Password?")
        self.forgot_password_button.clicked.connect(self.forgot_password)
        self.layout.addWidget(self.forgot_password_button)

        # Set layout
        self.setLayout(self.layout)

        # Storage for users
        self.user_data_file = "user_data.json"
        self.load_user_data()

    def load_user_data(self):
        """Load user data from file."""
        if not os.path.exists(self.user_data_file):
            with open(self.user_data_file, 'w') as f:
                json.dump({}, f)
        with open(self.user_data_file, 'r') as f:
            self.users = json.load(f)

    def save_user_data(self):
        """Save user data to file."""
        with open(self.user_data_file, 'w') as f:
            json.dump(self.users, f)

    def login(self):
        """Handle login functionality."""
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users and self.users[username] == password:
            QMessageBox.information(self, "Success", "Login successful!")
            self.hide()  # Hide the login window instead of closing it
            self.main_app = MainApp(username)  # Open the main application
            self.main_app.show()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password!")

    def signup(self):
        """Handle signup functionality."""
        username = self.username_input.text()
        password = self.password_input.text()

        if username in self.users:
            QMessageBox.warning(self, "Error", "Username already exists!")
        elif not username or not password:
            QMessageBox.warning(self, "Error", "Username and password cannot be empty!")
        else:
            self.users[username] = password
            self.save_user_data()
            QMessageBox.information(self, "Success", "Account created successfully!")

    def forgot_password(self):
        """Handle forgot password functionality."""
        username, ok = QInputDialog.getText(self, "Forgot Password", "Enter your username:")
        if ok and username:
            if username in self.users:
                # Ask for new password
                new_password, ok = QInputDialog.getText(self, "Reset Password", "Enter new password:")
                if ok and new_password:
                    # Update password
                    self.users[username] = new_password
                    self.save_user_data()
                    QMessageBox.information(self, "Success", "Password reset successful!")
                else:
                    QMessageBox.warning(self, "Error", "Password cannot be empty!")
            else:
                QMessageBox.warning(self, "Error", "Username not found!")
        else:
            QMessageBox.warning(self, "Error", "Username cannot be empty!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LoginSignupApp()
    window.show()
    sys.exit(app.exec())