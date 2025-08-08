import sys
import os
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, QSpinBox,
                             QGroupBox, QFormLayout, QFrame, QMessageBox, QMenu, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence

class DialSettingsDialog(QDialog):
    def __init__(self, title, config, parent=None):
        super().__init__(parent)
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory (KommPadConfigurator)
        parent_dir = os.path.dirname(script_dir)
        # Construct path to assets folder
        self.assets_path = os.path.join(parent_dir, "assets")
        
        self.setWindowTitle(f"Configure {title}")
        self.setModal(True)
        self.setFixedSize(600, 500)  # Match button configurator size ratio
        
        # Apply modern styling matching button configurator
        down_arrow_path = os.path.join(self.assets_path, "down_arrow.png").replace(os.sep, "/")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #565656;
                border-radius: 16px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QLabel {{
                color: #e0e0e0;
                font-weight: 500;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QLineEdit {{
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QLineEdit:focus {{
                border-color: #888888;
                background-color: #505050;
                outline: none;
            }}
            QLineEdit::placeholder {{
                color: #b0b0b0;
            }}
            QComboBox {{
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
                min-width: 200px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
                background-color: #505050;
                border-radius: 6px;
            }}
            QComboBox::down-arrow {{
                image: url('{down_arrow_path}');
                border: none;
                width: 12px;
                height: 12px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #404040;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 8px;
                selection-background-color: #606060;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QSpinBox {{
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
                min-width: 80px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QSpinBox:focus {{
                border-color: #888888;
                background-color: #505050;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: none;
                border: none;
                width: 25px;
                border-radius: 6px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: #606060;
            }}
            QSpinBox::up-button::before {{
                content: "▲";
                color: #e0e0e0;
                font-size: 10px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QSpinBox::down-button::before {{
                content: "▼";
                color: #e0e0e0;
                font-size: 10px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QSpinBox::up-arrow, QSpinBox::down-arrow {{
                image: none;
                border: none;
                width: 0px;
                height: 0px;
            }}
        """)
        
        self.config = config.copy()
        self.init_ui()
        self.load_config(config)
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Dialog title
        title = QLabel("Configure Dial")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("JetBrains Mono", 20, QFont.Bold))
        title.setStyleSheet("color: #888888; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)
        
        # Display Name
        name_group = QVBoxLayout()
        name_group.setSpacing(8)
        name_label = QLabel("Display Name")
        name_label.setFont(QFont("JetBrains Mono", 16, QFont.Bold))
        name_group.addWidget(name_label)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Enter dial name...")
        self.display_name_input.setFont(QFont("JetBrains Mono", 14))
        self.display_name_input.setContextMenuPolicy(Qt.CustomContextMenu)
        self.display_name_input.customContextMenuRequested.connect(self.show_custom_context_menu)
        name_group.addWidget(self.display_name_input)
        form_layout.addLayout(name_group)
        
        # Target Application
        app_group = QVBoxLayout()
        app_group.setSpacing(8)
        app_label = QLabel("Target Application")
        app_label.setFont(QFont("JetBrains Mono", 16, QFont.Bold))
        app_group.addWidget(app_label)
        
        self.exe_combo = QComboBox()
        self.exe_combo.setEditable(True)
        self.exe_combo.addItems([
            "MIC",
            "SYSTEM"
        ])
        self.exe_combo.setFont(QFont("JetBrains Mono", 14))
        self.exe_combo.lineEdit().setPlaceholderText("Enter application executable...")
        self.exe_combo.lineEdit().setContextMenuPolicy(Qt.CustomContextMenu)
        self.exe_combo.lineEdit().customContextMenuRequested.connect(self.show_custom_context_menu)
        app_group.addWidget(self.exe_combo)
        form_layout.addLayout(app_group)
        
        # Volume Range
        range_group = QVBoxLayout()
        range_group.setSpacing(8)
        range_label = QLabel("Volume Range")
        range_label.setFont(QFont("JetBrains Mono", 16, QFont.Bold))
        range_group.addWidget(range_label)
        
        range_layout = QHBoxLayout()
        range_layout.setSpacing(15)
        
        min_label = QLabel("Min:")
        min_label.setFont(QFont("JetBrains Mono", 14))
        min_label.setStyleSheet("color: #b0b0b0;")
        range_layout.addWidget(min_label)
        
        self.min_spinbox = QSpinBox()
        self.min_spinbox.setRange(0, 100)
        self.min_spinbox.setValue(0)
        self.min_spinbox.setSuffix("%")
        self.min_spinbox.setFont(QFont("JetBrains Mono", 14))
        range_layout.addWidget(self.min_spinbox)
        
        max_label = QLabel("Max:")
        max_label.setFont(QFont("JetBrains Mono", 14))
        max_label.setStyleSheet("color: #b0b0b0;")
        range_layout.addWidget(max_label)
        
        self.max_spinbox = QSpinBox()
        self.max_spinbox.setRange(0, 100)
        self.max_spinbox.setValue(100)
        self.max_spinbox.setSuffix("%")
        self.max_spinbox.setFont(QFont("JetBrains Mono", 14))
        range_layout.addWidget(self.max_spinbox)
        
        range_layout.addStretch()
        range_group.addLayout(range_layout)
        form_layout.addLayout(range_group)
        
        layout.addLayout(form_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 30, 0, 0)
        
        # Cancel button with button configurator styling
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("JetBrains Mono", 14, QFont.Medium))
        cancel_btn.setMinimumSize(120, 50)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QPushButton:hover {
                background-color: #505050;
                border-color: #707070;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #606060;
                border-color: #808080;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Save button with button configurator styling
        save_btn = QPushButton("Save Settings")
        save_btn.setFont(QFont("JetBrains Mono", 14, QFont.Medium))
        save_btn.setMinimumSize(140, 50)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #000000;
                border: 2px solid #888888;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QPushButton:hover {
                background-color: #a0a0a0;
                border-color: #a0a0a0;
            }
            QPushButton:pressed {
                background-color: #707070;
                border-color: #707070;
            }
        """)
        save_btn.clicked.connect(self.validate_and_accept)
        save_btn.setDefault(True)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def validate_and_accept(self):
        """Validate the configuration before accepting"""
        min_val = self.min_spinbox.value()
        max_val = self.max_spinbox.value()
        
        # Check if min is greater than max
        if min_val > max_val:
            # Show warning message
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Invalid Range")
            msg.setText("Invalid volume range!")
            msg.setInformativeText(f"Minimum value ({min_val}%) cannot be greater than maximum value ({max_val}%).\n\nPlease correct the values before saving.")
            msg.setStandardButtons(QMessageBox.Ok)
            
            # Apply the same dark theme styling to the message box
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #565656;
                    color: #e0e0e0;
                    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                }
                QMessageBox QLabel {
                    color: #e0e0e0;
                    font-size: 14px;
                    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                }
                QMessageBox QPushButton {
                    background-color: #888888;
                    color: #000000;
                    border: 2px solid #888888;
                    border-radius: 8px;
                    padding: 8px 16px;
                    font-size: 12px;
                    font-weight: 600;
                    min-width: 80px;
                    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                }
                QMessageBox QPushButton:hover {
                    background-color: #a0a0a0;
                    border-color: #a0a0a0;
                }
                QMessageBox QPushButton:pressed {
                    background-color: #707070;
                    border-color: #707070;
                }
            """)
            
            msg.exec_()
            return  # Don't close the dialog, let user fix the values
        
        # If validation passes, accept the dialog
        self.accept()
    
    def load_config(self, config):
        """Load configuration into the dialog"""
        self.display_name_input.setText(config.get("display_name", ""))
        
        # For dial configurations, the exe is stored in the "value" field
        exe_value = config.get("value", "")
        self.exe_combo.setCurrentText(exe_value)
        
        # Min/Max values
        self.min_spinbox.setValue(config.get("min", 0))
        self.max_spinbox.setValue(config.get("max", 100))
    
    def get_config(self):
        """Get the current configuration from the dialog"""
        # No need for validation here since it's done in validate_and_accept
        return {
            "display_name": self.display_name_input.text().strip(),
            "action_type": "🎛️ Dial Control",  # Fixed action type for dials
            "value": self.exe_combo.currentText().strip(),  # Store exe in value field
            "modifiers": [],  # Dials don't use modifiers
            "min": self.min_spinbox.value(),
            "max": self.max_spinbox.value()
        }
    
    def show_custom_context_menu(self, position):
        """Show a custom Figma-style context menu"""
        line_edit = self.sender()
        
        # Get accent color from parent if available
        accent_color = "#D51BBF"  # Default accent color
        if hasattr(self.parent(), 'accent_color'):
            accent_color = self.parent().accent_color
        
        # Create custom menu
        menu = QMenu(self)
        menu.setAttribute(Qt.WA_TranslucentBackground, True)
        menu.setWindowFlags(menu.windowFlags() | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: #2C2C2C;
                border: none;
                border-radius: 24px;
                padding: 12px 0px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                font-size: 13px;
                color: #FFFFFF;
                outline: none;
            }}
            QMenu::item {{
                background-color: transparent;
                padding: 12px 20px 12px 16px;
                margin: 3px 8px;
                border-radius: 16px;
                min-width: 120px;
                border: none;
                outline: none;
            }}
            QMenu::item:selected {{
                background-color: {accent_color};
                color: #FFFFFF;
            }}
            QMenu::item:disabled {{
                color: #666666;
                background-color: transparent;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: #444444;
                margin: 8px 16px;
                border-radius: 2px;
                border: none;
            }}
        """)
        
        # Check if text is selected
        has_selection = line_edit.hasSelectedText()
        has_text = len(line_edit.text()) > 0
        clipboard = QApplication.clipboard()
        has_clipboard = clipboard.mimeData().hasText()
        
        # Cut action
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.setEnabled(has_selection)
        cut_action.triggered.connect(line_edit.cut)
        menu.addAction(cut_action)
        
        # Copy action
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(line_edit.copy)
        menu.addAction(copy_action)
        
        # Paste action
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.setEnabled(has_clipboard)
        paste_action.triggered.connect(line_edit.paste)
        menu.addAction(paste_action)
        
        # Separator
        menu.addSeparator()
        
        # Select All action
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.setEnabled(has_text)
        select_all_action.triggered.connect(line_edit.selectAll)
        menu.addAction(select_all_action)
        
        # Show menu at cursor position
        global_pos = line_edit.mapToGlobal(position)
        menu.exec_(global_pos)

if __name__ == "__main__":
    # Test the dialog
    app = QApplication(sys.argv)
    
    test_config = {
        "display_name": "Spotify",
        "value": "Spotify.exe",
        "min": 0,
        "max": 100
    }
    
    dialog = DialSettingsDialog("Dial 1", test_config)
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        config = dialog.get_config()
        print("New configuration:", config)
    else:
        print("Dialog cancelled")
    
    # Properly exit the application
    app.quit()
