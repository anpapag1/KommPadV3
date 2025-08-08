import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QLineEdit, QPushButton, QDialog, QSpinBox, QMenu, QAction
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QPixmap, QKeySequence, QColor
from PyQt5.QtSvg import QSvgWidget
from button_configurator import ButtonSettingsDialog
from dial_configurator import DialSettingsDialog
from settings_configurator import SettingsDialog
import json

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Get the parent directory (KommPadConfigurator)
        parent_dir = os.path.dirname(script_dir)
        # Construct path to assets folder
        self.assets_path = os.path.join(parent_dir, "assets")
        
        self.setWindowTitle("KommPad Configurator")
        self.setGeometry(100, 100, 1200, 650)
        # small image at the top left corner
        self.setWindowIcon(QIcon(os.path.join(self.assets_path, "Logo.png")))
        self.setStyleSheet("""
            QWidget {
                background-color: #565656;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
        """)
        
        # Define accent color for consistent theming
        self.accent_color = "#D51BBF"  # Main accent color
        self.accent_hover = self.lighten_color(self.accent_color, 0.3)  # Lighter shade for hover
        self.accent_pressed = self.darken_color(self.accent_color, 0.3)  # Darker shade for pressed
        
        # Initialize button configurations storage
        self.button_configs = {}
        
        # Initialize layer system
        self.selected_layer = 0
        self.layer_names = ["Layer 1", "Layer 2", "Layer 3", "Layer 4"]
        self.full_mappings = {}  # Store all layer configurations
        
        self.init_ui()
    
    def lighten_color(self, hex_color, factor):
        """Lighten a hex color by the given factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Lighten each component
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, hex_color, factor):
        """Darken a hex color by the given factor (0.0 to 1.0)"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Darken each component
        r = max(0, int(r * (1 - factor)))
        g = max(0, int(g * (1 - factor)))
        b = max(0, int(b * (1 - factor)))
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def init_ui(self):
        # Create main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        header = QWidget()
        
        
        # Header layout
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(30, 25, 30, 25)
        
        # Layers section
        layers_widget = QWidget()
        layers_layout = QVBoxLayout(layers_widget)
        layers_layout.setContentsMargins(15, 10, 15, 10)
        layers_layout.setSpacing(8)
        
        # Layers image (SVG)
        layers_image = QSvgWidget(os.path.join(self.assets_path, "layers.svg"))
        layers_image.setFixedSize(26, 26)  # Set desired size
        
        # Layers label
        layers_label = QLabel("Layers")
        layers_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 5px;
            font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
        """)
        
        # Create horizontal layout for image and label
        layers_header_layout = QHBoxLayout()
        layers_header_layout.setContentsMargins(0, 0, 0, 0)
        layers_header_layout.setSpacing(8)
        layers_header_layout.addWidget(layers_image)
        layers_header_layout.addWidget(layers_label)
        layers_header_layout.addStretch()
        
        # Create a widget to contain the header layout
        layers_header_widget = QWidget()
        layers_header_widget.setLayout(layers_header_layout)
        
        # Layer controls container
        layer_controls = QWidget()
        layer_controls_layout = QHBoxLayout(layer_controls)
        layer_controls_layout.setContentsMargins(0, 0, 0, 0)
        layer_controls_layout.setSpacing(15)
        
        # Layer name input
        layer_name_input = QLineEdit()
        layer_name_input.setPlaceholderText("LayerName")
        layer_name_input.setFixedWidth(150)
        layer_name_input.setContextMenuPolicy(Qt.CustomContextMenu)
        layer_name_input.customContextMenuRequested.connect(self.show_custom_context_menu)
        layer_name_input.setStyleSheet("""
            QLineEdit {
                background-color: #606060;
                color: white;
                border: 2px solid #606060;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
                font-weight: 500;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }
            QLineEdit:focus {
                border: 2px solid #606060;
                background-color: #656565;
            }
            QLineEdit::placeholder {
                color: #b0b0b0;
            }
        """)
        
        # Store reference for layer name input
        self.layer_name_input = layer_name_input
        layer_name_input.textChanged.connect(self.on_layer_name_changed)
        layer_name_input.editingFinished.connect(self.save_configuration)
        
        # Layer buttons
        button_style = f"""
            QPushButton {{
                background-color: #606060;
                color: white;
                border: 2px solid #606060;
                border-radius: 20px;
                font-size: 13px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QPushButton:hover {{
                background-color: #656565;
            }}
            QPushButton:pressed {{
                background-color: #757575;
            }}
            QPushButton:checked {{
                background-color: {self.accent_color};
            }}
        """
        
        layer1_btn = QPushButton("1")
        layer1_btn.setFixedSize(40, 40)
        layer1_btn.setCheckable(True)
        layer1_btn.setChecked(True)  # Default selected
        layer1_btn.setStyleSheet(button_style)
        layer1_btn.clicked.connect(lambda: self.select_layer(0))
        
        layer2_btn = QPushButton("2")
        layer2_btn.setFixedSize(40, 40)
        layer2_btn.setCheckable(True)
        layer2_btn.setStyleSheet(button_style)
        layer2_btn.clicked.connect(lambda: self.select_layer(1))
        
        layer3_btn = QPushButton("3")
        layer3_btn.setFixedSize(40, 40)
        layer3_btn.setCheckable(True)
        layer3_btn.setStyleSheet(button_style)
        layer3_btn.clicked.connect(lambda: self.select_layer(2))
        
        layer4_btn = QPushButton("4")
        layer4_btn.setFixedSize(40, 40)
        layer4_btn.setCheckable(True)
        layer4_btn.setStyleSheet(button_style)
        layer4_btn.clicked.connect(lambda: self.select_layer(3))
        
        # Store layer buttons for reference
        self.layer_buttons = [layer1_btn, layer2_btn, layer3_btn, layer4_btn]
        
        # Max layers label
        max_layers_label = QLabel("  Number of Layers:")
        max_layers_label.setStyleSheet("""
            color: #e0e0e0;
            font-size: 13px;
            font-weight: bold;
            font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
        """)
        
        # Max layers spin box
        max_layers_spinbox = QSpinBox()
        max_layers_spinbox.setMinimum(1)
        max_layers_spinbox.setMaximum(4)  # Allow up to 4 layers
        max_layers_spinbox.setValue(4)  # Default to 4 layers/
        max_layers_spinbox.setFixedSize(70, 40)
        max_layers_spinbox.setContextMenuPolicy(Qt.CustomContextMenu)
        max_layers_spinbox.customContextMenuRequested.connect(self.show_spinbox_context_menu)
        max_layers_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background-color: #606060;
                color: white;
                border: 2px solid #606060;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QSpinBox:hover {{
                background-color: #656565;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background-color: none;
                border: none;
                width: 18px;
                border-radius: 4px;
                margin: 4px;
            }}
            QSpinBox::up-arrow {{
                image: url('{os.path.join(self.assets_path, "up_arrow.png").replace(os.sep, "/")}');
                width: 12px;
                height: 12px;
                border: none;
            }}
            QSpinBox::down-arrow {{
                image: url('{os.path.join(self.assets_path, "down_arrow.png").replace(os.sep, "/")}');
                width: 12px;
                height: 12px;
                border: none;
            }}
        """)
        
        # Connect spin box to max layers change
        max_layers_spinbox.valueChanged.connect(self.on_max_layers_changed)
        self.max_layers_spinbox = max_layers_spinbox
        
        # Add to layer controls layout
        layer_controls_layout.addWidget(layer_name_input)
        layer_controls_layout.addWidget(layer1_btn)
        layer_controls_layout.addWidget(layer2_btn)
        layer_controls_layout.addWidget(layer3_btn)
        layer_controls_layout.addWidget(layer4_btn)
        layer_controls_layout.addWidget(max_layers_label)
        layer_controls_layout.addWidget(max_layers_spinbox)
        layer_controls_layout.addStretch()
        
        # Add to layers layout
        layers_layout.addWidget(layers_header_widget)
        layers_layout.addWidget(layer_controls)
        # Settings button (QPushButton with SVG icon inside)
        settings_btn = QPushButton()
        settings_btn.setFixedSize(40, 40)
        settings_btn.setToolTip("Settings")
        settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #292929;
                border: none;
                border-radius: 20px;
                padding: 0px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:hover QSvgWidget {{
            }}
            QPushButton:pressed {{
                background-color: {self.accent_pressed};
            }}
            QPushButton:pressed QSvgWidget {{
            }}
        """)
        # Store reference to settings button
        self.settings_btn = settings_btn
        # Add SVG icon to button/
        icon_widget = QSvgWidget(os.path.join(self.assets_path, "settings.svg"))
        icon_widget.setFixedSize(24, 24)
        icon_widget.setStyleSheet("""
            QSvgWidget {
                background: transparent;
            }
        """)
        # Make the icon widget ignore mouse events so button hover works
        icon_widget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        # Place the SVG in a layout inside the button
        icon_layout = QHBoxLayout(settings_btn)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_widget)
        
        # Store reference to icon for hover effects
        settings_btn.icon_widget = icon_widget
        
        # Connect settings button to open settings dialog
        settings_btn.clicked.connect(self.open_settings_dialog)
        # Add to header layout
        header_layout.addWidget(layers_widget)
        header_layout.addStretch()  # Push settings button to the right
        header_layout.addWidget(settings_btn)
        
        # Add header to main layout
        main_layout.addWidget(header)
        
        # Create body layout
        body_widget = QWidget()
        body_layout = QVBoxLayout(body_widget)
        body_layout.setContentsMargins(30, 30, 30, 30)
                
        # Create a container widget for absolute positioning
        container = QWidget()
        container.setFixedSize(700, 400) 
        
        # Create dial buttons behind the rectangle, sticking out on top
        dial_button_style = f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: 2px solid #505050;
                border-radius: 12px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
                border-color: #606060;
            }}
            QPushButton:pressed {{
                background-color: {self.accent_pressed};
            }}
        """

        # Dial button positions and sizes
        dial_button_size = 80
        dial_y_position = 30  # Position them so they stick out above the rectangle
        dial_spacing = 120
        dial_start_x = 45  # Start position for first dial
        
        # Store dial button references
        self.dial_buttons = []
        
        # Create 3 dial buttons
        for i in range(3):
            dial_btn = QPushButton(f"D{i+1}", container)
            dial_btn.setFixedSize(dial_button_size, dial_button_size)
            dial_btn.move(dial_start_x + i * dial_spacing, dial_y_position)
            dial_btn.setStyleSheet(dial_button_style)
            
            # Connect dial button to configuration dialog
            dial_btn.clicked.connect(lambda checked, num=i+7: self.configure_button(num))  # Use buttons 7-9 for dials
            
            # Store dial button reference
            self.dial_buttons.append(dial_btn)
            
        # Create the centered square
        square = QWidget(container)
        square.setFixedSize(700, 280)  # 600x280 pixel square
        square.move(0, 100)
        square.setStyleSheet("""
            QWidget {
                background-color: #292929;
                border-radius: 24px;
            }
        """)
        
        # Create the Encoder on top of the square
        encoder = QWidget(container)
        encoder.setFixedSize(260, 260)  # 260x260 pixel circle
        encoder.move(420, 30)  # Position circle above and centered on the square
        encoder.setStyleSheet(f"""
            QWidget {{
                background-color: {self.accent_color};
                border-radius: 130px;  /* Half of width/height for perfect circle */
            }}
        """)
        
        # Store reference to encoder
        self.encoder = encoder
        
        # Create layout for buttons inside the encoder
        encoder_layout = QVBoxLayout(encoder)
        encoder_layout.setAlignment(Qt.AlignCenter)

        # Store encoder button references
        self.encoder_buttons = []
        
        # Create buttons for the encoder
        encoder_btn1 = QPushButton(f"E1")
        encoder_btn1.setFixedSize(200, 50)  # Fixed size for encoder buttons
        encoder_btn1.setStyleSheet(f"""
            QPushButton {{
                background-color: #606060;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.accent_pressed};
            }}
        """)
        encoder_btn1.clicked.connect(lambda: self.configure_button(10))
        encoder_layout.addWidget(encoder_btn1)
        self.encoder_buttons.append(encoder_btn1)

        # Create buttons for the encoder
        encoder_btn2 = QPushButton(f"E2")
        encoder_btn2.setFixedSize(200, 50)  # Fixed size for encoder buttons
        encoder_btn2.setStyleSheet(f"""
            QPushButton {{
                background-color: #606060;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.accent_pressed};
            }}
        """)
        encoder_btn2.clicked.connect(lambda: self.configure_button(11))
        encoder_layout.addWidget(encoder_btn2)
        self.encoder_buttons.append(encoder_btn2)

        # Create buttons for the encoder
        encoder_btn3 = QPushButton(f"E3")
        encoder_btn3.setFixedSize(200, 50)  # Fixed size for encoder buttons
        encoder_btn3.setStyleSheet(f"""
            QPushButton {{
                background-color: #606060;
                color: white;
                border-radius: 8px;
                font-size: 16px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QPushButton:hover {{
                background-color: {self.accent_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.accent_pressed};
            }}
        """)
        encoder_btn3.clicked.connect(lambda: self.configure_button(12))
        encoder_layout.addWidget(encoder_btn3)
        self.encoder_buttons.append(encoder_btn3)

        # Create button matrix 3x2 (3 columns, 2 rows)
        button_matrix_style = f"""
            QPushButton {{
                background-color: #606060;
                color: black;
                border-radius: 16px;
                font-size: 24px;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
            }}
            QPushButton:hover {{
                background-color: #868686;
            }}
            QPushButton:pressed {{
                background-color: #666;
            }}
        """
        
        # Button matrix positions and sizes
        button_width = 124
        button_height = button_width
        start_x = 12
        start_y = 112
        spacing_x = button_width + 7
        spacing_y = button_height + 7
        
        # Store button references for configuration
        self.matrix_buttons = []
        
        # Create 3x2 matrix of buttons
        for row in range(2):
            for col in range(3):
                button_num = row * 3 + col + 1
                btn = QPushButton(f"B{button_num}", container)
                btn.setFixedSize(button_width, button_height)
                btn.move(start_x + col * spacing_x, start_y + row * spacing_y)
                btn.setStyleSheet(button_matrix_style)
                
                # Connect button to configuration dialog
                btn.clicked.connect(lambda checked, num=button_num: self.configure_button(num))
                
                # Store button reference
                self.matrix_buttons.append(btn)

        # Add container to body
        body_layout.setAlignment(Qt.AlignCenter)
        body_layout.addStretch()
        body_layout.addWidget(container)
        body_layout.addStretch()

        # Add body to main layout
        main_layout.addWidget(body_widget)
    
        # Set the layout
        self.setLayout(main_layout)
        
        # Load saved configuration
        self.load_configuration()
        
        # Initialize layer name display
        self.layer_name_input.setText(self.layer_names[self.selected_layer])
        
    def configure_button(self, button_num):
        """Open configuration dialog for the specified button"""
        # Always ensure we have fresh data from the file
        self.load_configuration()
        
        # Get existing configuration
        button_num_str = str(button_num)
        
        # Determine default name based on button type
        if button_num <= 6:
            default_name = f"B{button_num}"
        elif button_num <= 9:
            default_name = f"D{button_num-6}"  # D1, D2, D3 for dials
        else:
            default_name = f"E{button_num-9}"  # E1, E2, E3 for encoder buttons
            
        stored_config = self.button_configs.get(button_num_str, {
            "display_name": default_name,
            "action_type": "🔤 Key Press",
            "value": "",
            "modifiers": []
        })
        
        # Create and show appropriate dialog based on button type
        if button_num <= 6:
            # Regular matrix buttons - use ButtonSettingsDialog
            dialog_title = f"Button {button_num}"
            dialog = ButtonSettingsDialog(dialog_title, stored_config, self)
        elif button_num <= 9:
            # Dial buttons - use DialSettingsDialog
            dial_num = button_num - 6
            dialog_title = f"Dial {dial_num}"
            dialog = DialSettingsDialog(dialog_title, stored_config, self)
        else:
            # Encoder buttons - use ButtonSettingsDialog
            encoder_num = button_num - 9
            dialog_title = f"Encoder {encoder_num}"
            dialog = ButtonSettingsDialog(dialog_title, stored_config, self)
        
        if dialog.exec_() == QDialog.Accepted:
            # Save the configuration
            new_config = dialog.get_config()
            self.button_configs[button_num_str] = new_config
            
            # Update button text
            if new_config["display_name"].strip():
                if button_num <= 6:
                    self.matrix_buttons[button_num - 1].setText(new_config["display_name"])
                elif button_num <= 9:
                    self.dial_buttons[button_num - 7].setText(new_config["display_name"])
                else:
                    encoder_num = button_num - 9
                    encoder_labels = ["Clockwise", "Press", "CounterClockwise"]
                    encoder_label = encoder_labels[encoder_num - 1]
                    self.encoder_buttons[encoder_num - 1].setText(f"{encoder_label}: {new_config['display_name']}")
            else:
                if button_num <= 6:
                    self.matrix_buttons[button_num - 1].setText(f"B{button_num}")
                elif button_num <= 9:
                    self.dial_buttons[button_num - 7].setText(f"D{button_num-6}")
                else:
                    encoder_num = button_num - 9
                    encoder_labels = ["Clockwise", "Press", "CounterClockwise"]
                    encoder_label = encoder_labels[encoder_num - 1]
                    self.encoder_buttons[encoder_num - 1].setText(f"{encoder_label}: E{encoder_num}")
            
            # Auto-save configuration
            self.save_configuration()
    
    def get_button_config_from_json(self, button_num):
        """Get button configuration directly from JSON file"""
        try:
            with open("config.json", 'r') as f:
                config_data = json.load(f)
            
            if "mappings" not in config_data:
                return None
                
            # Map button number to JSON key
            if button_num <= 6:
                button_key = f"button{button_num}"
            elif button_num <= 9:
                encoder_num = button_num - 6
                button_key = f"encoder{encoder_num}"
            else:
                # Circle buttons also map to encoder1-encoder3
                circle_num = button_num - 9
                button_key = f"encoder{circle_num}"
            
            # Get current layer configuration
            current_layer = f"layer{self.selected_layer}"
            
            if button_key in config_data["mappings"] and current_layer in config_data["mappings"][button_key]:
                layer_config = config_data["mappings"][button_key][current_layer]
                
                # Convert to old format for dialog
                return {
                    "display_name": layer_config.get("display", self.get_default_button_name(button_num)),
                    "action_type": self.convert_action_to_old_format(layer_config.get("action", "key")),
                    "value": layer_config.get("value", ""),
                    "modifiers": layer_config.get("modifiers", [])
                }
            
            return None
        except Exception as e:
            print(f"Error reading config from JSON: {e}")
            return None
    
    def save_configuration(self, filename="config.json"):
        """Save button configurations to file"""
        try:
            # Save current layer to mappings before saving
            if hasattr(self, 'full_mappings'):
                self.save_current_layer_to_mappings()
            
            # Load existing config to preserve device and other settings
            try:
                with open(filename, 'r') as f:
                    existing_config = json.load(f)
            except FileNotFoundError:
                existing_config = {
                    "device": {
                        "max_layers": 4,
                        "COM": "COM12"
                    }
                }
            
            # Update mappings
            existing_config["mappings"] = self.full_mappings
            
            # Update settings with layer information
            if "settings" not in existing_config:
                existing_config["settings"] = {}
            
            # Get max layers from spin box
            max_layers = self.max_layers_spinbox.value() if hasattr(self, 'max_layers_spinbox') else 4
            existing_config["settings"]["MaxLayers"] = max_layers
            
            # Preserve existing layer data and only update names for active layers
            if "Layers" not in existing_config["settings"]:
                existing_config["settings"]["Layers"] = {}
            
            # Update layer names only for currently active layers (don't delete existing ones)
            for i, name in enumerate(self.layer_names):
                if i < len(self.layer_names):  # Only update layers we have in memory
                    existing_config["settings"]["Layers"][f"layer{i}"] = {"name": name}
            
            with open(filename, 'w') as f:
                json.dump(existing_config, f, indent=2)
            print(f"Configuration saved to {filename}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def load_configuration(self, filename="config.json"):
        """Load button configurations from file"""
        try:
            with open(filename, 'r') as f:
                config_data = json.load(f)
            
            # Load accent color from device section and update UI colors
            if "device" in config_data and "AccentColor" in config_data["device"]:
                self.accent_color = config_data["device"]["AccentColor"]
                self.accent_hover = self.lighten_color(self.accent_color, 0.3)
                self.accent_pressed = self.darken_color(self.accent_color, 0.3)
                # Update UI elements with new accent color
                self.update_accent_colors()
            
            # Load mappings
            if "mappings" in config_data:
                self.full_mappings = config_data["mappings"]
                
                # Load layer names from settings
                if "settings" in config_data and "Layers" in config_data["settings"]:
                    layers_data = config_data["settings"]["Layers"]
                    max_layers_from_config = config_data["settings"].get("MaxLayers", 4)
                    
                    self.layer_names = []
                    for i in range(max_layers_from_config):
                        layer_key = f"layer{i}"
                        if layer_key in layers_data:
                            self.layer_names.append(layers_data[layer_key]["name"])
                        else:
                            self.layer_names.append(f"Layer {i+1}")
                    
                    # Update spin box value
                    if hasattr(self, 'max_layers_spinbox'):
                        self.max_layers_spinbox.setValue(max_layers_from_config)
                        # Update button visibility based on loaded max layers
                        self.on_max_layers_changed(max_layers_from_config)
                    
                    # Ensure we have at least the required layers
                    while len(self.layer_names) < max_layers_from_config:
                        self.layer_names.append(f"Layer {len(self.layer_names)+1}")
                else:
                    # Default case
                    if hasattr(self, 'max_layers_spinbox'):
                        self.max_layers_spinbox.setValue(4)
                
                # Load configurations for current layer
                self.load_layer_configurations()
            
            # Update button displays
            if hasattr(self, 'matrix_buttons'):
                self.update_button_displays()
                    
            print(f"Configuration loaded from {filename}")
        except FileNotFoundError:
            print(f"Configuration file {filename} not found. Using defaults.")
        except Exception as e:
            print(f"Error loading configuration: {e}")
        
    def select_layer(self, layer_index):
        """Handle layer selection"""
        # Save current layer configs before switching
        if hasattr(self, 'full_mappings'):
            self.save_current_layer_to_mappings()
        
        # Update layer selection
        for i, btn in enumerate(self.layer_buttons):
            btn.setChecked(i == layer_index)
        
        self.selected_layer = layer_index
        self.layer_name_input.setText(self.layer_names[layer_index])
        
        # Load configurations for the new layer
        self.load_layer_configurations()
        
        # Update button displays
        self.update_button_displays()
        
        # Auto-save configuration when switching layers
        self.save_configuration()
    
    def on_max_layers_changed(self, value):
        """Handle max layers change from spin box"""
        # Update the number of available layers
        while len(self.layer_names) < value:
            self.layer_names.append(f"Layer {len(self.layer_names)+1}")
        
        # If current layer is beyond new max, switch to last available layer
        if self.selected_layer >= value:
            self.select_layer(value - 1)
        
        # Update layer button visibility/availability
        for i, btn in enumerate(self.layer_buttons):
            if i < value:
                btn.setVisible(True)
                btn.setEnabled(True)
            else:
                btn.setVisible(False)
                btn.setEnabled(False)
                btn.setChecked(False)
        
        # Auto-save configuration
        self.save_configuration()
    
    def save_current_layer_to_mappings(self):
        """Save current UI state to the full mappings data"""
        if not hasattr(self, 'full_mappings'):
            self.full_mappings = {}
            
        current_layer = f"layer{self.selected_layer}"
        
        # Save button configurations
        for button_num_str, config in self.button_configs.items():
            button_num = int(button_num_str)
            
            # Map button numbers to correct keys based on config.json schema
            if button_num <= 6:
                # Matrix buttons: button1-button6
                button_key = f"button{button_num}"
            elif button_num <= 9:
                # Dial buttons: dial1-dial3
                dial_num = button_num - 6
                button_key = f"dial{dial_num}"
            else:
                # Encoder buttons: encoder1-encoder3
                encoder_num = button_num - 9
                button_key = f"encoder{encoder_num}"
            
            if button_key not in self.full_mappings:
                self.full_mappings[button_key] = {}
            
            modifiers = config.get("modifiers", [])
            # Ensure modifiers are in list format
            if isinstance(modifiers, dict):
                converted_modifiers = []
                for mod, enabled in modifiers.items():
                    if enabled:
                        converted_modifiers.append(mod)
            else:
                converted_modifiers = modifiers
            
            # Handle different button types with different JSON structures
            if button_num <= 6:
                # Matrix buttons use standard format
                self.full_mappings[button_key][current_layer] = {
                    "action": self.convert_action_from_old_format(config.get("action_type", "🔤 Key Press")),
                    "value": self.convert_value_from_old_format(config),
                    "modifiers": converted_modifiers,
                    "display": config.get("display_name", self.get_default_button_name(button_num))
                }
            elif button_num <= 9:
                # Dial buttons use dial format with exe, min, max
                self.full_mappings[button_key][current_layer] = {
                    "exe": config.get("value", ""),
                    "min": config.get("min", 0),
                    "max": config.get("max", 100),
                    "display": config.get("display_name", self.get_default_button_name(button_num))
                }
            else:
                # Encoder buttons use standard format
                self.full_mappings[button_key][current_layer] = {
                    "action": self.convert_action_from_old_format(config.get("action_type", "🔤 Key Press")),
                    "value": self.convert_value_from_old_format(config),
                    "modifiers": converted_modifiers,
                    "display": config.get("display_name", self.get_default_button_name(button_num))
                }
    
    def load_layer_configurations(self):
        """Load configurations for the current layer"""
        if not hasattr(self, 'full_mappings'):
            return
            
        current_layer = f"layer{self.selected_layer}"
        self.button_configs = {}
        
        # Load button configurations for current layer
        # Matrix buttons (1-6): map from button1-button6
        for button_num in range(1, 7):
            button_key = f"button{button_num}"
            if button_key in self.full_mappings and current_layer in self.full_mappings[button_key]:
                layer_config = self.full_mappings[button_key][current_layer]
                self.button_configs[str(button_num)] = {
                    "display_name": layer_config.get("display", f"B{button_num}"),
                    "action_type": self.convert_action_to_old_format(layer_config.get("action", "key")),
                    "value": self.convert_value_to_old_format(layer_config),
                    "modifiers": layer_config.get("modifiers", [])
                }
        
        # Dial buttons (7-9): map from dial1-dial3
        for dial_num in range(1, 4):
            button_num = dial_num + 6  # Map to buttons 7-9
            dial_key = f"dial{dial_num}"
            if dial_key in self.full_mappings and current_layer in self.full_mappings[dial_key]:
                layer_config = self.full_mappings[dial_key][current_layer]
                self.button_configs[str(button_num)] = {
                    "display_name": layer_config.get("display", f"D{dial_num}"),
                    "action_type": "🎛️ Dial Control",  # Special action type for dials
                    "value": layer_config.get("exe", ""),
                    "modifiers": [],
                    "min": layer_config.get("min", 0),
                    "max": layer_config.get("max", 100)
                }
        
        # Circle buttons (10-12): also map from encoder1-encoder3
        for encoder_num in range(1, 4):
            button_num = encoder_num + 9  # Map to buttons 10-12
            encoder_key = f"encoder{encoder_num}"  # Use encoder mapping for encoder buttons
            if encoder_key in self.full_mappings and current_layer in self.full_mappings[encoder_key]:
                layer_config = self.full_mappings[encoder_key][current_layer]
                self.button_configs[str(button_num)] = {
                    "display_name": layer_config.get("display", f"E{encoder_num}"),
                    "action_type": self.convert_action_to_old_format(layer_config.get("action", "key")),
                    "value": self.convert_value_to_old_format(layer_config),
                    "modifiers": layer_config.get("modifiers", [])
                }
    
    def update_button_displays(self):
        """Update button text displays based on current configurations"""
        # Update matrix buttons (1-6)
        for button_num in range(1, 7):
            button_num_str = str(button_num)
            if button_num_str in self.button_configs:
                config = self.button_configs[button_num_str]
                display_name = config.get("display_name", f"B{button_num}")
                if display_name.strip():
                    self.matrix_buttons[button_num - 1].setText(display_name)
                else:
                    self.matrix_buttons[button_num - 1].setText(f"B{button_num}")
            else:
                self.matrix_buttons[button_num - 1].setText(f"B{button_num}")
        
        # Update dial buttons (7-9)
        for dial_num in range(1, 4):  # Dial buttons 1-3
            button_num = dial_num + 6  # Map to buttons 7-9
            button_num_str = str(button_num)
            if button_num_str in self.button_configs:
                config = self.button_configs[button_num_str]
                display_name = config.get("display_name", f"D{dial_num}")
                if display_name.strip():
                    self.dial_buttons[dial_num - 1].setText(display_name)
                else:
                    self.dial_buttons[dial_num - 1].setText(f"D{dial_num}")
            else:
                self.dial_buttons[dial_num - 1].setText(f"D{dial_num}")
        
        # Update encoder buttons (10-12)
        for encoder_num in range(1, 4):  # Encoder buttons 1-3
            button_num = encoder_num + 9  # Map to buttons 10-12
            button_num_str = str(button_num)
            
            # Define encoder action labels
            encoder_labels = ["Clockwise", "Press", "CClockwise"]
            encoder_label = encoder_labels[encoder_num - 1]
            
            if button_num_str in self.button_configs:
                config = self.button_configs[button_num_str]
                display_name = config.get("display_name", f"E{encoder_num}")
                if display_name.strip():
                    self.encoder_buttons[encoder_num - 1].setText(f"{encoder_label}: {display_name}")
                else:
                    self.encoder_buttons[encoder_num - 1].setText(f"{encoder_label}: E{encoder_num}")
            else:
                self.encoder_buttons[encoder_num - 1].setText(f"{encoder_label}: E{encoder_num}")
    
    def on_layer_name_changed(self, text):
        """Handle layer name changes"""
        if hasattr(self, 'layer_names') and hasattr(self, 'selected_layer'):
            self.layer_names[self.selected_layer] = text
    
    def open_settings_dialog(self):
        """Open the settings dialog"""
        dialog = SettingsDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Reload configuration to get updated accent color
            self.load_configuration()
            print("Settings saved")
    
    def get_default_button_name(self, button_num):
        """Get default button name based on button number"""
        if button_num <= 6:
            return f"B{button_num}"
        elif button_num <= 9:
            return f"D{button_num-6}"  # D1, D2, D3 for dials
        else:
            return f"E{button_num-9}"  # E1, E2, E3 for encoder buttons
    
    def show_custom_context_menu(self, position):
        """Show a custom Figma-style context menu"""
        line_edit = self.sender()
        
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
                background-color: {self.accent_color};
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
            QMenu::right-arrow {{
                width: 12px;
                height: 12px;
                margin-right: 8px;
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
    
    def show_spinbox_context_menu(self, position):
        """Show a custom Figma-style context menu for spinbox"""
        spinbox = self.sender()
        
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
                background-color: {self.accent_color};
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
        
        # Check current state
        has_text = len(spinbox.text()) > 0
        clipboard = QApplication.clipboard()
        has_clipboard = clipboard.mimeData().hasText()
        has_selection = spinbox.lineEdit().hasSelectedText()
        
        # Cut action
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.setEnabled(has_selection)
        cut_action.triggered.connect(lambda: spinbox.lineEdit().cut())
        menu.addAction(cut_action)
        
        # Copy action
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(lambda: spinbox.lineEdit().copy())
        menu.addAction(copy_action)
        
        # Paste action
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.setEnabled(has_clipboard)
        paste_action.triggered.connect(lambda: spinbox.lineEdit().paste())
        menu.addAction(paste_action)
        
        # Separator
        menu.addSeparator()
        
        # Select All action
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.setEnabled(has_text)
        select_all_action.triggered.connect(lambda: spinbox.lineEdit().selectAll())
        menu.addAction(select_all_action)
        
        # Show menu at cursor position
        global_pos = spinbox.mapToGlobal(position)
        menu.exec_(global_pos)
    
    # Conversion methods for compatibility with UI2 format
    def convert_action_from_old_format(self, old_action):
        """Convert old action format to new format"""
        action_map = {
            "🔤 Key Press": "key",
            "📝 Text/String": "text",
            "🖱️ Mouse Click": "mouse",
            "🎮 Gamepad": "gamepad",
            "🎵 Media Control": "media",  # Fixed to match button configurator
            "⚙️ System": "system",
            "� Macro": "macro",  # Fixed to match button configurator
            "⚡ Function": "function"  # Fixed to match button configurator
        }
        return action_map.get(old_action, "key")
    
    def convert_action_to_old_format(self, new_action):
        """Convert new action format to old format"""
        action_map = {
            "key": "🔤 Key Press",
            "text": "📝 Text/String",
            "mouse": "🖱️ Mouse Click",
            "gamepad": "🎮 Gamepad",
            "media": "🎵 Media Control",  # Fixed to match button configurator
            "system": "⚙️ System",
            "macro": "� Macro",  # Fixed to match button configurator
            "function": "⚡ Function"  # Fixed to match button configurator
        }
        return action_map.get(new_action, "🔤 Key Press")
    
    def convert_value_from_old_format(self, config):
        """Convert old value format to new format"""
        return config.get("value", "")
    
    def convert_value_to_old_format(self, layer_config):
        """Convert new value format to old format"""
        return layer_config.get("value", "")
    
    def update_accent_colors(self):
        """Update all UI elements with the current accent color"""
        # Update layer buttons
        if hasattr(self, 'layer_buttons'):
            button_style = f"""
                QPushButton {{
                    background-color: #606060;
                    color: white;
                    border: 2px solid #606060;
                    border-radius: 20px;
                    font-size: 13px;
                    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                }}
                QPushButton:hover {{
                    background-color: #656565;
                }}
                QPushButton:pressed {{
                    background-color: #757575;
                }}
                QPushButton:checked {{
                    background-color: {self.accent_color};
                }}
            """
            for btn in self.layer_buttons:
                btn.setStyleSheet(button_style)
        
        # Update settings button
        if hasattr(self, 'settings_btn'):
            self.settings_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #292929;
                    border: none;
                    border-radius: 20px;
                    padding: 0px;
                }}
                QPushButton:hover {{
                    background-color: {self.accent_hover};
                }}
                QPushButton:pressed {{
                    background-color: {self.accent_pressed};
                }}
            """)
        
        # Update dial buttons
        if hasattr(self, 'dial_buttons'):
            dial_button_style = f"""
                QPushButton {{
                    background-color: {self.accent_color};
                    color: white;
                    border: 2px solid #505050;
                    border-radius: 12px;
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                }}
                QPushButton:hover {{
                    background-color: {self.accent_hover};
                    border-color: #606060;
                }}
                QPushButton:pressed {{
                    background-color: {self.accent_pressed};
                }}
            """
            for btn in self.dial_buttons:
                btn.setStyleSheet(dial_button_style)
        
        # Update encoder circle
        if hasattr(self, 'encoder'):
            self.encoder.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.accent_color};
                    border-radius: 130px;
                }}
            """)
        
        # Update encoder buttons
        if hasattr(self, 'encoder_buttons'):
            encoder_button_style = f"""
                QPushButton {{
                    background-color: #606060;
                    color: white;
                    border-radius: 8px;
                    font-size: 16px;
                    font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                }}
                QPushButton:hover {{
                    background-color: {self.accent_hover};
                }}
                QPushButton:pressed {{
                    background-color: {self.accent_pressed};
                }}
            """
            for btn in self.encoder_buttons:
                btn.setStyleSheet(encoder_button_style)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())