"""
Modern Settings Configurator Dialog
A standalone PyQt5 dialog for configuring application settings, matching the style of button and dial configurators.
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QSpinBox, QSlider, QComboBox, QGroupBox, QFrame,
    QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
import json
from color_picker import ColorPickerDialog
import os


class SettingsDialog(QDialog):
    """Modern popup dialog for application settings configuration"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("KommPad Settings")
        self.setFixedSize(450, 550)
        self.setModal(True)
        
        # Initialize settings with defaults
        self.led_brightness = 75
        self.led_mode = "solid"
        self.led_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
        self.accent_color = "#D51BBF"  # Default accent color
        
        # Apply modern styling matching button configurator dark theme
        self.setStyleSheet("""
            QDialog {
                background-color: #565656;
                border-radius: 16px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QLabel {
                color: #e0e0e0;
                font-weight: 500;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                background-color: transparent;
            }
            QLineEdit {
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QLineEdit:focus {
                border-color: #888888;
                background-color: #505050;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #b0b0b0;
            }
            QComboBox {
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
                min-width: 200px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QComboBox:focus {
                border-color: #888888;
                background-color: #505050;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
                background-color: #505050;
                border-radius: 6px;
            }
            QComboBox::down-arrow {
                image: url('assets/down_arrow.png');
                border: none;
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #404040;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 8px;
                selection-background-color: #606060;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QSpinBox {
                border: 2px solid #606060;
                border-radius: 12px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: #404040;
                color: #e0e0e0;
                min-height: 20px;
                min-width: 80px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QSpinBox:focus {
                border-color: #888888;
                background-color: #505050;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: none;
                border: none;
                width: 25px;
                border-radius: 6px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #606060;
            }
            QSpinBox::up-arrow, QSpinBox::down-arrow {
                image: none;
                border: none;
                width: 0px;
                height: 0px;
            }
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: transparent;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 8px 0 8px;
                background-color: transparent;
                color: #e0e0e0;
            }
            QCheckBox {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: 500;
                spacing: 8px;
                padding: 8px;
                margin: 4px;
                background-color: #404040;
                border-radius: 6px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #404040;
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #606060;
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #707070;
            }
            QScrollBar::handle:vertical:pressed {
                background-color: #808080;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
            QSlider::groove:horizontal {
                height: 6px;
                background: #404040;
                border-radius: 3px;
                border: 1px solid #606060;
            }
            QSlider::handle:horizontal {
                background: #888888;
                border: 2px solid #606060;
                width: 20px;
                height: 20px;
                margin: -8px 0;
                border-radius: 10px;
            }
            QSlider::handle:horizontal:hover {
                background: #a0a0a0;
                border-color: #888888;
            }
            QSlider::handle:horizontal:pressed {
                background: #707070;
                border-color: #505050;
            }
            QSlider::sub-page:horizontal {
                background: #888888;
                border-radius: 3px;
            }
            QSlider::add-page:horizontal {
                background: #404040;
                border-radius: 3px;
            }
        """)
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Dialog title
        title = QLabel("Settings")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("JetBrains Mono", 16, QFont.Bold))
        title.setStyleSheet("color: #e0e0e0; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Create scroll area for main content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create scroll content widget
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setSpacing(12)
        content_layout.setContentsMargins(5, 5, 5, 5)
        
        # LED Settings Group  
        self.create_led_settings(content_layout)
        
        # Configurator Settings Group
        self.create_configurator_settings(content_layout)
        
        # Configuration Management Group
        self.create_config_management(content_layout)
        
        # Add stretch to push content to top
        content_layout.addStretch()
        
        # Set the scroll content widget
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # Dialog buttons (outside scroll area)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(QFont("JetBrains Mono", 12, QFont.Medium))
        cancel_btn.setMinimumSize(100, 36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 12px;
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
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.setFont(QFont("JetBrains Mono", 12, QFont.Medium))
        save_btn.setMinimumSize(120, 36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #888888;
                color: #000000;
                border: 2px solid #888888;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 12px;
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
        save_btn.clicked.connect(self.save_settings)
        save_btn.setDefault(True)
        
        # Add buttons to layout
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def create_led_settings(self, layout):
        """Create LED configuration settings"""
        group = QGroupBox("LED Settings")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                border: 2px solid #606060;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #e0e0e0;
                background-color: #404040;
                border-radius: 6px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(12, 12, 12, 12)
        
        # Brightness control
        brightness_layout = QHBoxLayout()
        
        brightness_label = QLabel("Brightness:")
        brightness_label.setFont(QFont("JetBrains Mono", 12))
        brightness_layout.addWidget(brightness_label)
        
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setStyleSheet("background-color: transparent;")
        self.brightness_slider.setRange(0, 100)
        self.brightness_slider.setValue(self.led_brightness)
        self.brightness_slider.setTickPosition(QSlider.TicksBelow)
        self.brightness_slider.setTickInterval(25)
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        brightness_layout.addWidget(self.brightness_slider)
        
        self.brightness_value_label = QLabel(f"{self.led_brightness}%")
        self.brightness_value_label.setFont(QFont("JetBrains Mono", 12))
        self.brightness_value_label.setStyleSheet("color: #888888; font-weight: 600; min-width: 40px;")
        self.brightness_value_label.setAlignment(Qt.AlignCenter)
        brightness_layout.addWidget(self.brightness_value_label)
        
        group_layout.addLayout(brightness_layout)
        
        # Mode control
        mode_layout = QHBoxLayout()
        
        mode_label = QLabel("Mode:")
        mode_label.setFont(QFont("JetBrains Mono", 12))
        mode_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["solid", "breathing", "rainbow", "wave", "reactive"])
        self.mode_combo.setCurrentText(self.led_mode)
        self.mode_combo.setFont(QFont("JetBrains Mono", 12))
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        mode_layout.addStretch()
        group_layout.addLayout(mode_layout)
        
        # Color selection
        colors_layout = QHBoxLayout()
        
        colors_label = QLabel("Colors:")
        colors_label.setFont(QFont("JetBrains Mono", 12))
        colors_layout.addWidget(colors_label)
        
        self.color_buttons_container = QWidget()
        self.color_buttons_container.setStyleSheet("background-color: transparent;")
        self.color_buttons_layout = QHBoxLayout(self.color_buttons_container)
        self.color_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.color_buttons_layout.setSpacing(8)
        
        self.color_buttons = []
        self.update_color_buttons()
        
        colors_layout.addWidget(self.color_buttons_container)
        colors_layout.addStretch()
        
        group_layout.addLayout(colors_layout)
        
        layout.addWidget(group)
    
    def create_configurator_settings(self, layout):
        """Create configurator appearance and behavior settings"""
        group = QGroupBox("Configurator Settings")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                border: 2px solid #606060;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #e0e0e0;
                background-color: #404040;
                border-radius: 6px;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(12, 12, 12, 12)
        
        # Accent color selection
        accent_layout = QHBoxLayout()
        
        accent_label = QLabel("Accent Color:")
        accent_label.setFont(QFont("JetBrains Mono", 12))
        accent_layout.addWidget(accent_label)
        
        self.accent_color_btn = QPushButton()
        self.accent_color_btn.setFixedSize(40, 32)
        self.accent_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_color};
                border: 2px solid #cccccc;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border-color: #888888;
                border-width: 3px;
            }}
        """)
        self.accent_color_btn.clicked.connect(self.select_accent_color)
        accent_layout.addWidget(self.accent_color_btn)
        
        # Add accent color preview label
        self.accent_color_label = QLabel(self.accent_color)
        self.accent_color_label.setFont(QFont("JetBrains Mono", 11))
        self.accent_color_label.setStyleSheet("color: #888888; font-weight: 600; margin-left: 10px;")
        accent_layout.addWidget(self.accent_color_label)
        
        accent_layout.addStretch()
        group_layout.addLayout(accent_layout)
        
        layout.addWidget(group)
    
    def create_config_management(self, layout):
        """Create configuration management settings"""
        group = QGroupBox("Configuration Management")
        group.setStyleSheet("""
            QGroupBox {
                color: #e0e0e0;
                font-size: 14px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                border: 2px solid #606060;
                border-radius: 10px;
                margin-top: 12px;
                padding-top: 12px;
                background-color: #404040;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 6px;
                color: #e0e0e0;
                border-radius: 6px;
                background-color: #404040;
            }
        """)
        
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(12, 12, 12, 12)
        
        # Import/Export buttons
        buttons_layout = QHBoxLayout()
        
        import_btn = QPushButton("📥 Import")
        import_btn.setFont(QFont("JetBrains Mono", 11))
        import_btn.setFixedHeight(32)
        import_btn.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #606060;
                border-color: #707070;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        import_btn.clicked.connect(self.import_configuration)
        buttons_layout.addWidget(import_btn)
        
        export_btn = QPushButton("📤 Export")
        export_btn.setFont(QFont("JetBrains Mono", 11))
        export_btn.setFixedHeight(32)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #505050;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #606060;
                border-color: #707070;
            }
            QPushButton:pressed {
                background-color: #404040;
            }
        """)
        export_btn.clicked.connect(self.export_configuration)
        buttons_layout.addWidget(export_btn)
        
        group_layout.addLayout(buttons_layout)
        
        # Reset button
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setFont(QFont("JetBrains Mono", 11))
        reset_btn.setFixedHeight(32)
        reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #704040;
                color: #e0e0e0;
                border: 2px solid #806060;
                border-radius: 8px;
                padding: 6px 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #805050;
                border-color: #907070;
            }
            QPushButton:pressed {
                background-color: #603030;
            }
        """)
        reset_btn.clicked.connect(self.reset_to_defaults)
        group_layout.addWidget(reset_btn)
        
        layout.addWidget(group)
    
    def on_brightness_changed(self, value):
        """Handle brightness slider change"""
        self.led_brightness = value
        self.brightness_value_label.setText(f"{value}%")
    
    def on_mode_changed(self, mode):
        """Handle LED mode change"""
        self.led_mode = mode
    
    def select_accent_color(self):
        """Handle accent color selection"""
        current_color = QColor(self.accent_color)
        color_dialog = ColorPickerDialog(current_color, self)
        
        if color_dialog.exec_() == QDialog.Accepted:
            new_color = color_dialog.get_selected_color()
            if new_color.isValid():
                color_hex = new_color.name()
                self.accent_color = color_hex
                self.update_accent_color_display()
    
    def update_accent_color_display(self):
        """Update accent color button and label display"""
        self.accent_color_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_color};
                border: 2px solid #cccccc;
                border-radius: 8px;
            }}
            QPushButton:hover {{
                border-color: #888888;
                border-width: 3px;
            }}
        """)
        self.accent_color_label.setText(self.accent_color)
    
    def select_color(self, color_index):
        """Handle color selection"""
        current_color = QColor(self.led_colors[color_index])
        color_dialog = ColorPickerDialog(current_color, self)
        
        if color_dialog.exec_() == QDialog.Accepted:
            new_color = color_dialog.get_selected_color()
            if new_color.isValid():
                color_hex = new_color.name()
                self.led_colors[color_index] = color_hex
                self.update_color_buttons()
    
    def add_new_color(self):
        """Add a new color to the list"""
        if len(self.led_colors) < 4:
            self.led_colors.append("#FF0000")
            self.update_color_buttons()
            # Immediately open color picker for the new color
            self.select_color(len(self.led_colors) - 1)
    
    def remove_color(self, color_index):
        """Remove a color from the list"""
        if len(self.led_colors) > 1 and 0 <= color_index < len(self.led_colors):
            self.led_colors.pop(color_index)
            self.update_color_buttons()
    
    def update_color_buttons(self):
        """Update color buttons display"""
        # Clear existing buttons
        while self.color_buttons_layout.count() > 0:
            child = self.color_buttons_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        self.color_buttons.clear()
        
        # Create color buttons for existing colors
        for i, color_hex in enumerate(self.led_colors):
            color_container = QWidget()
            color_container.setFixedSize(32, 32)
            
            color_btn = QPushButton(color_container)
            color_btn.setFixedSize(32, 32)
            color_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color_hex};
                    border: 2px solid #cccccc;
                    border-radius: 16px;
                }}
                QPushButton:hover {{
                    border-color: #888888;
                    border-width: 3px;
                }}
            """)
            color_btn.clicked.connect(lambda checked, idx=i: self.select_color(idx))
            color_btn.move(0, 0)
            
            # Delete button (only if more than 1 color)
            if len(self.led_colors) > 1:
                delete_btn = QPushButton("×", color_container)
                delete_btn.setFixedSize(12, 12)
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #ff4444;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 8px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #cc0000;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, idx=i: self.remove_color(idx))
                delete_btn.move(0, 0)
                delete_btn.raise_()
            
            self.color_buttons.append(color_btn)
            self.color_buttons_layout.addWidget(color_container)
        
        # Add "Add Color" button if less than 4 colors
        if len(self.led_colors) < 4:
            add_color_btn = QPushButton("+")
            add_color_btn.setFixedSize(32, 32)
            add_color_btn.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    border: 2px dashed #888888;
                    border-radius: 16px;
                    font-size: 16px;
                    font-weight: bold;
                    color: #888888;
                }
                QPushButton:hover {
                    background-color: #505050;
                    border-color: #aaaaaa;
                    color: #aaaaaa;
                }
            """)
            add_color_btn.clicked.connect(self.add_new_color)
            self.color_buttons_layout.addWidget(add_color_btn)
        
        self.color_buttons_layout.addStretch()
    
    def export_configuration(self):
        """Export current configuration to a file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Configuration",
                "kommpad_config.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                if os.path.exists("config.json"):
                    with open("config.json", 'r') as source:
                        config = json.load(source)
                    
                    with open(file_path, 'w') as target:
                        json.dump(config, target, indent=2)
                    
                    self.show_info_message("Export Successful", f"Configuration exported to:\n{file_path}")
                else:
                    self.show_error_message("Export Error", "No configuration file found to export.")
                    
        except Exception as e:
            self.show_error_message("Export Error", f"Failed to export configuration: {str(e)}")
    
    def import_configuration(self):
        """Import configuration from a file"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Import Configuration",
                "",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if file_path:
                with open(file_path, 'r') as f:
                    imported_config = json.load(f)
                
                # Validate the imported config has required structure
                if not isinstance(imported_config, dict):
                    raise ValueError("Invalid configuration file format")
                
                # Save imported config
                with open("config.json", 'w') as f:
                    json.dump(imported_config, f, indent=2)
                
                # Reload settings from the imported config
                self.load_settings()
                
                # Update parent if available
                if self.parent_window:
                    self.parent_window.load_configuration()
                
                self.show_info_message("Import Successful", f"Configuration imported from:\n{file_path}")
                
        except Exception as e:
            self.show_error_message("Import Error", f"Failed to import configuration: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        reply = QMessageBox.question(
            self,
            "Reset to Defaults",
            "Are you sure you want to reset all settings to their default values?\n\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Reset UI elements to defaults
                self.led_brightness = 75
                self.brightness_slider.setValue(75)
                self.brightness_value_label.setText("75%")
                self.led_mode = "solid"
                self.mode_combo.setCurrentText("solid")
                self.led_colors = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
                self.update_color_buttons()
                self.accent_color = "#D51BBF"
                self.update_accent_color_display()
                
                # Create default config
                default_config = {
                    "device": {
                        "max_layers": 4,
                        "COM": "COM12",
                        "AccentColor": "#D51BBF"
                    },
                    "settings": {
                        "Brightness": 75,
                        "ColorMode": "solid",
                        "Colors": ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"]
                    },
                    "mappings": {}
                }
                
                # Save default config
                with open("config.json", 'w') as f:
                    json.dump(default_config, f, indent=2)
                
                # Update parent if available
                if self.parent_window:
                    self.parent_window.load_configuration()
                
                self.show_info_message("Reset Complete", "All settings have been reset to their default values.")
                
            except Exception as e:
                self.show_error_message("Reset Error", f"Failed to reset settings: {str(e)}")
    
    def show_error_message(self, title, message):
        """Show an error message with consistent styling"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        self.apply_message_box_style(msg)
        msg.exec_()
    
    def show_info_message(self, title, message):
        """Show an info message with consistent styling"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        self.apply_message_box_style(msg)
        msg.exec_()
    
    def apply_message_box_style(self, msg_box):
        """Apply consistent styling to message boxes"""
        msg_box.setStyleSheet("""
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
    
    def load_settings(self):
        """Load settings from config file"""
        try:
            if os.path.exists("config.json"):
                with open("config.json", 'r') as f:
                    config = json.load(f)
                
                # Load settings values
                settings = config.get("settings", {})
                self.led_brightness = settings.get("Brightness", 75)
                self.led_mode = settings.get("ColorMode", "solid")
                self.led_colors = settings.get("Colors", ["#FF0000", "#00FF00", "#0000FF", "#FFFF00"])
                
                # Load accent color from device section
                device = config.get("device", {})
                self.accent_color = device.get("AccentColor", "#D51BBF")
                
                # Update UI elements if they exist
                if hasattr(self, 'brightness_slider'):
                    self.brightness_slider.setValue(self.led_brightness)
                    self.brightness_value_label.setText(f"{self.led_brightness}%")
                if hasattr(self, 'mode_combo'):
                    self.mode_combo.setCurrentText(self.led_mode)
                if hasattr(self, 'color_buttons_container'):
                    self.update_color_buttons()
                if hasattr(self, 'accent_color_btn'):
                    self.update_accent_color_display()
                    
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to config file and update parent"""
        try:
            # Read existing config or create new one
            config = {}
            if os.path.exists("config.json"):
                with open("config.json", 'r') as f:
                    config = json.load(f)
            
            # Update settings section
            if "settings" not in config:
                config["settings"] = {}
            
            config["settings"]["Brightness"] = self.brightness_slider.value()
            config["settings"]["ColorMode"] = self.mode_combo.currentText()
            config["settings"]["Colors"] = self.led_colors.copy()
            
            # Update device section for accent color
            if "device" not in config:
                config["device"] = {}
            
            config["device"]["AccentColor"] = self.accent_color
            
            # Save config file
            with open("config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            # Update parent window if available
            if self.parent_window and hasattr(self.parent_window, 'load_configuration'):
                self.parent_window.load_configuration()
            
            self.accept()
            
        except Exception as e:
            self.show_error_message("Save Error", f"Failed to save settings: {str(e)}")


# Example usage and testing
def main():
    """Example of how to use the SettingsDialog"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the dialog
    dialog = SettingsDialog()
    
    result = dialog.exec_()
    
    if result == QDialog.Accepted:
        print("Settings saved successfully")
    else:
        print("Settings cancelled")


if __name__ == "__main__":
    main()
