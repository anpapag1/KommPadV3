"""
Modern Button Configurator Dialog
A standalone PyQt5 dialog for configuring button actions, values, and modifiers.
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, 
    QGroupBox, QComboBox, QCheckBox, QApplication, QMenu, QAction
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QKeySequence
import sys


class ButtonSettingsDialog(QDialog):
    """Modern popup dialog for button configuration"""
    
    def __init__(self, button_id, config=None, parent=None):
        super().__init__(parent)
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory (KommPadConfigurator)
        parent_dir = os.path.dirname(script_dir)
        # Construct path to assets folder
        self.assets_path = os.path.join(parent_dir, "assets")
        
        self.button_id = button_id
        self.config = config or {}
        
        self.setWindowTitle(f"Configure {self.button_id}")
        self.setFixedSize(600, 700)
        self.setModal(True)
        
        # Apply modern styling matching UI3 dark theme
        down_arrow_path = os.path.join(self.assets_path, "down_arrow.png").replace(os.sep, "/")
        self.setStyleSheet(f"""
            QDialog {{
                background-color: #565656;
                border-radius: 16px;
            }}
            QLabel {{
                color: #e0e0e0;
                font-weight: 500;
            }}
            QLineEdit {{
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
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
            }}
            QComboBox:focus {{
                border-color: #888888;
                background-color: #505050;
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
            }}
            QGroupBox {{
                font-size: 16px;
                font-weight: bold;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #404040;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px 0 8px;
                background-color: #404040;
                color: #e0e0e0;
            }}
        """)
        
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(25)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Dialog title
        title = QLabel(f"Configure {self.button_id}")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setStyleSheet("color: #888888; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Form layout
        form_layout = QVBoxLayout()
        form_layout.setSpacing(25)
        
        # Display Name
        name_group = QVBoxLayout()
        name_group.setSpacing(8)
        name_label = QLabel("Display Name")
        name_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        name_group.addWidget(name_label)
        
        self.display_name_input = QLineEdit()
        self.display_name_input.setPlaceholderText("Enter button name...")
        self.display_name_input.setFont(QFont("Segoe UI", 14))
        self.display_name_input.setContextMenuPolicy(Qt.CustomContextMenu)
        self.display_name_input.customContextMenuRequested.connect(self.show_custom_context_menu)
        name_group.addWidget(self.display_name_input)
        form_layout.addLayout(name_group)
        
        # Action Type
        action_group = QVBoxLayout()
        action_group.setSpacing(8)
        action_label = QLabel("Action Type")
        action_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        action_group.addWidget(action_label)
        
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems([
            "🔤 Key Press", 
            "🎵 Media Control", 
            "⚡ Function", 
            "📝 Macro"
        ])
        self.action_type_combo.setFont(QFont("Segoe UI", 14))
        self.action_type_combo.currentTextChanged.connect(self.on_action_type_changed)
        action_group.addWidget(self.action_type_combo)
        form_layout.addLayout(action_group)
        
        # Value
        value_group = QVBoxLayout()
        value_group.setSpacing(8)
        value_label = QLabel("Action Value")
        value_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        value_group.addWidget(value_label)
        
        self.value_combo = QComboBox()
        self.value_combo.setEditable(False)  # Changed to non-editable for better control
        self.value_combo.setFont(QFont("Segoe UI", 14))
        self.value_combo.currentTextChanged.connect(self.on_value_changed)
        value_group.addWidget(self.value_combo)
        
        # Additional input for function actions
        self.additional_input = QLineEdit()
        self.additional_input.setFont(QFont("Segoe UI", 14))
        self.additional_input.setVisible(False)
        self.additional_input.setContextMenuPolicy(Qt.CustomContextMenu)
        self.additional_input.customContextMenuRequested.connect(self.show_custom_context_menu)
        value_group.addWidget(self.additional_input)
        
        form_layout.addLayout(value_group)
        
        # Modifiers
        self.mod_group = QGroupBox("Modifier Keys")
        self.mod_group.setFont(QFont("Segoe UI", 14, QFont.Bold))
        mod_layout = QHBoxLayout(self.mod_group)

        # Style for checkboxes matching UI3 dark theme
        checkbox_style = """
            QCheckBox {
                font-size: 14px;
                font-weight: 500;
                color: #e0e0e0;
                spacing: 8px;
                padding: 8px;
                margin: 4px;
                background-color: #404040;
                border-radius: 6px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #606060;
                border-radius: 4px;
                background-color: #404040;
            }
            QCheckBox::indicator:hover {
                border-color: #888888;
                background-color: #505050;
            }
            QCheckBox::indicator:checked {
                background-color: #888888;
                border-color: #888888;
            }
            QCheckBox::indicator:checked:hover {
                background-color: #a0a0a0;
                border-color: #a0a0a0;
            }
        """
        
        self.ctrl_checkbox = QCheckBox("Ctrl")
        self.ctrl_checkbox.setFont(QFont("Segoe UI", 14, QFont.Medium))
        self.ctrl_checkbox.setStyleSheet(checkbox_style)
        
        self.alt_checkbox = QCheckBox("Alt")
        self.alt_checkbox.setFont(QFont("Segoe UI", 14, QFont.Medium))
        self.alt_checkbox.setStyleSheet(checkbox_style)
        
        self.shift_checkbox = QCheckBox("Shift")
        self.shift_checkbox.setFont(QFont("Segoe UI", 14, QFont.Medium))
        self.shift_checkbox.setStyleSheet(checkbox_style)
        
        self.win_checkbox = QCheckBox("Win")
        self.win_checkbox.setFont(QFont("Segoe UI", 14, QFont.Medium))
        self.win_checkbox.setStyleSheet(checkbox_style)
        
        mod_layout.addWidget(self.ctrl_checkbox)
        mod_layout.addWidget(self.alt_checkbox)
        mod_layout.addWidget(self.shift_checkbox)
        mod_layout.addWidget(self.win_checkbox)
        
        form_layout.addWidget(self.mod_group)
        layout.addLayout(form_layout)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setContentsMargins(0, 30, 0, 0)
        
        # Cancel button with UI3 dark theme styling
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("Segoe UI", 14, QFont.Medium))
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
        
        # OK button with UI3 accent color
        ok_btn = QPushButton("Save Settings")
        ok_btn.setFont(QFont("Segoe UI", 14, QFont.Medium))
        ok_btn.setMinimumSize(140, 50)
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #000000;
                border: 2px solid #888888;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
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
        # ok_btn.clicked.connect(self.save_and_print_config)
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
    def on_action_type_changed(self, action_type):
        """Handle action type changes to show/hide modifier keys and update value options"""
        # Clear current values
        self.value_combo.clear()
        self.additional_input.setVisible(False)
        self.additional_input.setPlaceholderText("")
        
        if action_type == "🔤 Key Press":
            # Keyboard keys
            keyboard_keys = [
                "Space", "Enter", "Escape", "Tab", "Backspace", "Delete",
                "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12",
                "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
                "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
                "1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                "Left", "Right", "Up", "Down", "Home", "End", "Page_Up", "Page_Down",
                "Insert", "Print_Screen", "Scroll_Lock", "Pause",
                "`", "-", "=", "[", "]", "\\", ";", "'", ",", ".", "/",
                "Numpad_0", "Numpad_1", "Numpad_2", "Numpad_3", "Numpad_4",
                "Numpad_5", "Numpad_6", "Numpad_7", "Numpad_8", "Numpad_9",
                "Numpad_Plus", "Numpad_Minus", "Numpad_Multiply", "Numpad_Divide", "Numpad_Enter"
            ]
            self.value_combo.addItems(keyboard_keys)
            self.mod_group.setVisible(True)
            
        elif action_type == "🎵 Media Control":
            # Media actions
            media_actions = [
                "Media_Play_Pause", "Media_Next", "Media_Previous", "Media_Stop",
                "Volume_Up", "Volume_Down", "Volume_Mute",
                "Browser_Back", "Browser_Forward", "Browser_Refresh", "Browser_Home",
                "Mail", "Calculator", "My_Computer"
            ]
            self.value_combo.addItems(media_actions)
            self.mod_group.setVisible(False)
            
        elif action_type == "⚡ Function":
            # Function actions
            function_actions = [
                "Layer_Up", "Open_App", "Open_Web", "Text"
            ]
            self.value_combo.addItems(function_actions)
            self.mod_group.setVisible(False)  # Will be shown conditionally
            
        elif action_type == "� Macro":
            # Macro actions (placeholder for future implementation)
            macro_actions = [
                "Custom_Macro"
            ]
            self.value_combo.addItems(macro_actions)
            self.mod_group.setVisible(False)
            
        # Update value combo selection to trigger on_value_changed
        if self.value_combo.count() > 0:
            self.on_value_changed(self.value_combo.currentText())
    
    def on_value_changed(self, value):
        """Handle value changes to show/hide additional inputs and modifiers"""
        current_action = self.action_type_combo.currentText()
        
        # Reset additional input visibility
        self.additional_input.setVisible(False)
        self.additional_input.setPlaceholderText("")
        
        if current_action == "⚡ Function":
            if value == "Open_App":
                self.additional_input.setVisible(True)
                self.additional_input.setPlaceholderText("Enter executable path (e.g., notepad.exe)")
                # Hide modifiers for Open_App
                self.mod_group.setVisible(False)
            elif value == "Open_Web":
                self.additional_input.setVisible(True)
                self.additional_input.setPlaceholderText("Enter URL (e.g., https://example.com)")
                # Hide modifiers for Open_Web
                self.mod_group.setVisible(False)
            elif value == "Text":
                self.additional_input.setVisible(True)
                self.additional_input.setPlaceholderText("Enter text to type")
                # Hide modifiers for Text
                self.mod_group.setVisible(False)
            elif value == "Layer_Up":
                # Hide additional input and modifiers for Layer_Up
                self.mod_group.setVisible(False)
        
    def load_config(self):
        """Load configuration into the form"""
        self.display_name_input.setText(
            self.config.get("display_name", str(self.button_id))
        )
        self.action_type_combo.setCurrentText(
            self.config.get("action_type", "🔤 Key Press")
        )
        
        # Update value options based on action type
        self.on_action_type_changed(self.action_type_combo.currentText())
        
        # Set value after populating options
        self.value_combo.setCurrentText(
            self.config.get("value", "")
        )
        
        # Load modifiers (handle both old dict format and new list format)
        modifiers_data = self.config.get("modifiers", [])
        
        # Reset all checkboxes first
        self.ctrl_checkbox.setChecked(False)
        self.alt_checkbox.setChecked(False)
        self.shift_checkbox.setChecked(False)
        self.win_checkbox.setChecked(False)
        
        additional_text = ""
        
        if isinstance(modifiers_data, list):
            # New list format
            for modifier in modifiers_data:
                if modifier == "ctrl":
                    self.ctrl_checkbox.setChecked(True)
                elif modifier == "alt":
                    self.alt_checkbox.setChecked(True)
                elif modifier == "shift":
                    self.shift_checkbox.setChecked(True)
                elif modifier == "win":
                    self.win_checkbox.setChecked(True)
                elif modifier.startswith("exe:"):
                    additional_text = modifier[4:]  # Remove "exe:" prefix
                elif modifier.startswith("text:"):
                    additional_text = modifier[5:]  # Remove "text:" prefix
                elif modifier.startswith("url:"):
                    additional_text = modifier[4:]  # Remove "url:" prefix
        else:
            # Old dictionary format for backward compatibility
            self.ctrl_checkbox.setChecked(modifiers_data.get("ctrl", False))
            self.alt_checkbox.setChecked(modifiers_data.get("alt", False))
            self.shift_checkbox.setChecked(modifiers_data.get("shift", False))
            self.win_checkbox.setChecked(modifiers_data.get("win", False))
            
            # Handle old format additional values
            current_action = self.config.get("action_type", "🔤 Key Press")
            current_value = self.config.get("value", "")
            
            if current_action == "⚡ Function":
                if current_value == "Open_App" and "exe" in modifiers_data:
                    additional_text = modifiers_data.get("exe", "")
                elif current_value == "Text" and "text" in modifiers_data:
                    additional_text = modifiers_data.get("text", "")
                elif current_value == "Open_Web" and "url" in modifiers_data:
                    additional_text = modifiers_data.get("url", "")

        # Trigger value change to show/hide additional input fields properly
        self.on_value_changed(self.value_combo.currentText())
        
        # Set additional input text after triggering value change
        if additional_text:
            self.additional_input.setText(additional_text.strip())
        
        
        
    def get_config(self):
        """Get the current configuration from the form"""
        # Build modifiers list with only active modifiers
        modifiers = []
        
        
        current_action = self.action_type_combo.currentText()
        current_value = self.value_combo.currentText().strip()
        # print(current_action, current_value)
        
        if current_action == "🔤 Key Press":
            # Add active modifier keys
            if self.ctrl_checkbox.isChecked():
                modifiers.append("ctrl")
            if self.alt_checkbox.isChecked():
                modifiers.append("alt")
            if self.shift_checkbox.isChecked():
                modifiers.append("shift")
            if self.win_checkbox.isChecked():
                modifiers.append("win")
        elif current_action == "⚡ Function":
            if current_value == "Open_App":
                modifiers.append(f"exe:{self.additional_input.text().strip()}")
            elif current_value == "Text":
                modifiers.append(f"text:{self.additional_input.text().strip()}") 
            elif current_value == "Open_Web":
                modifiers.append(f"url:{self.additional_input.text().strip()}")  
        print(modifiers)             
        
        config = {
            "display_name": self.display_name_input.text().strip() or str(self.button_id),
            "action_type": self.action_type_combo.currentText(),
            "value": self.value_combo.currentText().strip(),
            "modifiers": modifiers
        }
        
        return config
    
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
    

# Example usage and testing
def main():
    """Example of how to use the ButtonSettingsDialog"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Example configuration with new list format
    sample_config = {
        "display_name": "Open Notepad",
        "action_type": "⚡ Function",
        "value": "Open_Web",
        "modifiers": ["ctrl", "url:notepad.exe"]
    }
    
    # Create and show the dialog
    dialog = ButtonSettingsDialog("Test", sample_config)
    
    if dialog.exec_() == QDialog.Accepted:
        config = dialog.get_config()
        print(config)
    else:
        print("Configuration cancelled")


if __name__ == "__main__":
    main()
