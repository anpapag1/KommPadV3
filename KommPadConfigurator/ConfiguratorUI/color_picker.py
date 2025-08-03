import sys
import math
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QDialog, QApplication)
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPixmap, QConicalGradient, QRadialGradient, QLinearGradient

class ColorWheel(QWidget):
    colorChanged = pyqtSignal(QColor)
    
    def __init__(self, width=300, height=200):
        super().__init__()
        self.setFixedSize(width, height)
        self.selected_color = QColor(255, 0, 0)  # Default red
        self.hue = 0.0
        self.saturation = 1.0
        self.brightness = 1.0
        
        # Calculate areas with centering
        self.hue_strip_width = 25  # Slightly wider for better usability
        self.gap = 15  # Bigger gap for cleaner separation
        
        # Calculate total content width and center it
        total_content_width = width - 20  # Reduced margins for larger content
        self.color_area_width = total_content_width - self.hue_strip_width - self.gap
        self.color_area_height = height - 30  # Reduced space for preview strip
        
        # Preview strip dimensions
        self.preview_height = 18  # Slightly taller preview
        self.preview_gap = 10  # Slightly larger gap
        
        # Center the content
        self.content_start_x = (width - total_content_width) // 2
        self.content_start_y = (height - self.color_area_height - self.preview_height - self.preview_gap) // 2
        
        # Selection positions
        self.color_pos = QPoint(self.content_start_x + self.color_area_width, self.content_start_y + self.preview_height + self.preview_gap)  # Start at top-right of color area
        self.hue_pos = self.content_start_y + self.preview_height + self.preview_gap  # Position on hue strip
        
        # Cache variables for performance
        self._last_hue = -1  # Track when hue changes to regenerate color area
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw background with subtle border
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(Qt.NoBrush)
        
        # Draw the color preview strip
        self.draw_color_preview(painter)
        
        # Border around color area
        color_area_y = self.content_start_y + self.preview_height + self.preview_gap
        painter.drawRoundedRect(self.content_start_x, color_area_y, self.color_area_width, self.color_area_height, 8, 8)
        
        # Border around hue strip
        hue_x = self.content_start_x + self.color_area_width + self.gap
        painter.drawRoundedRect(hue_x, color_area_y, self.hue_strip_width, self.color_area_height, 6, 6)
        
        # Draw the main color area
        self.draw_color_area(painter)
        
        # Draw the hue strip
        self.draw_hue_strip(painter)
        
        # Draw selection indicators
        self.draw_selection_indicators(painter)
        
    def draw_color_preview(self, painter):
        """Draw the color preview strip at the top"""
        # Calculate preview strip dimensions
        preview_width = self.color_area_width + self.gap + self.hue_strip_width
        preview_rect_x = self.content_start_x
        preview_rect_y = self.content_start_y
        
        # Draw border around preview
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(preview_rect_x, preview_rect_y, preview_width, self.preview_height, 6, 6)
        
        # Fill with current color
        painter.setBrush(QBrush(self.selected_color))
        painter.setPen(Qt.NoPen)
        
        # Create clipping path for rounded corners
        from PyQt5.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(preview_rect_x, preview_rect_y, preview_width, self.preview_height, 6, 6)
        painter.setClipPath(path)
        
        painter.fillRect(preview_rect_x, preview_rect_y, preview_width, self.preview_height, QBrush(self.selected_color))
        
        # Reset clipping
        painter.setClipping(False)
        
    def draw_color_area(self, painter):
        """Draw the main color selection area using gradients for better performance"""
        # Create a QPixmap for the color area if it doesn't exist or hue changed
        if not hasattr(self, '_color_area_pixmap') or self._last_hue != self.hue:
            self._color_area_pixmap = QPixmap(self.color_area_width, self.color_area_height)
            pixmap_painter = QPainter(self._color_area_pixmap)
            
            # Get the current hue color
            hue_color = QColor.fromHsvF(self.hue, 1.0, 1.0)
            
            # Create horizontal gradient from white to hue color (saturation)
            h_gradient = QLinearGradient(0, 0, self.color_area_width, 0)
            h_gradient.setColorAt(0.0, QColor(255, 255, 255))  # White at left
            h_gradient.setColorAt(1.0, hue_color)  # Hue color at right
            
            # Fill the entire area with the saturation gradient
            pixmap_painter.fillRect(0, 0, self.color_area_width, self.color_area_height, QBrush(h_gradient))
            
            # Create vertical gradient from transparent to black (brightness)
            v_gradient = QLinearGradient(0, 0, 0, self.color_area_height)
            v_gradient.setColorAt(0.0, QColor(0, 0, 0, 0))    # Transparent at top
            v_gradient.setColorAt(1.0, QColor(0, 0, 0, 255))  # Black at bottom
            
            # Overlay the brightness gradient
            pixmap_painter.fillRect(0, 0, self.color_area_width, self.color_area_height, QBrush(v_gradient))
            
            pixmap_painter.end()
            self._last_hue = self.hue
        
        # Draw the cached pixmap with rounded corners
        painter.save()
        color_area_y = self.content_start_y + self.preview_height + self.preview_gap
        painter.setClipRect(self.content_start_x, color_area_y, self.color_area_width, self.color_area_height)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle path for clipping
        from PyQt5.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(self.content_start_x, color_area_y, self.color_area_width, self.color_area_height, 8, 8)
        painter.setClipPath(path)
        
        painter.drawPixmap(self.content_start_x, color_area_y, self._color_area_pixmap)
        painter.restore()
    
    def draw_hue_strip(self, painter):
        """Draw the vertical hue strip using gradient for better performance"""
        # Create a QPixmap for the hue strip if it doesn't exist
        if not hasattr(self, '_hue_strip_pixmap'):
            self._hue_strip_pixmap = QPixmap(self.hue_strip_width, self.color_area_height)
            pixmap_painter = QPainter(self._hue_strip_pixmap)
            
            # Create vertical gradient for all hues
            hue_gradient = QLinearGradient(0, 0, 0, self.color_area_height)
            
            # Add color stops for the full hue spectrum
            steps = 20  # More steps for smoother gradient
            for i in range(steps + 1):
                position = i / steps
                hue = position
                color = QColor.fromHsvF(hue, 1.0, 1.0)
                hue_gradient.setColorAt(position, color)
            
            # Fill the hue strip
            pixmap_painter.fillRect(0, 0, self.hue_strip_width, self.color_area_height, QBrush(hue_gradient))
            pixmap_painter.end()
        
        # Draw the cached hue strip with rounded corners
        hue_x = self.content_start_x + self.color_area_width + self.gap
        color_area_y = self.content_start_y + self.preview_height + self.preview_gap
        painter.save()
        painter.setClipRect(hue_x, color_area_y, self.hue_strip_width, self.color_area_height)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create rounded rectangle path for clipping
        from PyQt5.QtGui import QPainterPath
        path = QPainterPath()
        path.addRoundedRect(hue_x, color_area_y, self.hue_strip_width, self.color_area_height, 6, 6)
        painter.setClipPath(path)
        
        painter.drawPixmap(hue_x, color_area_y, self._hue_strip_pixmap)
        painter.restore()
    
    def draw_selection_indicators(self, painter):
        """Draw selection indicators with better styling"""
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Color area indicator (crosshair style)
        # White outer ring
        painter.setPen(QPen(QColor(255, 255, 255), 3))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(self.color_pos.x() - 6, self.color_pos.y() - 6, 12, 12)
        
        # Black inner ring for contrast
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawEllipse(self.color_pos.x() - 5, self.color_pos.y() - 5, 10, 10)
        
        # Small center dot for precise selection
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(0, 0, 0), 1))
        painter.drawEllipse(self.color_pos.x() - 2, self.color_pos.y() - 2, 4, 4)
        
        # Hue strip indicator (triangle-like arrows)
        hue_x = self.content_start_x + self.color_area_width + self.gap
        
        # Left arrow pointing to hue strip
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        left_triangle = [
            QPoint(hue_x - 4, self.hue_pos),
            QPoint(hue_x - 12, self.hue_pos - 6),
            QPoint(hue_x - 12, self.hue_pos + 6)
        ]
        painter.drawPolygon(left_triangle)
        
        # Right arrow pointing to hue strip
        right_triangle = [
            QPoint(hue_x + self.hue_strip_width + 4, self.hue_pos),
            QPoint(hue_x + self.hue_strip_width + 12, self.hue_pos - 6),
            QPoint(hue_x + self.hue_strip_width + 12, self.hue_pos + 6)
        ]
        painter.drawPolygon(right_triangle)
    
    def mousePressEvent(self, event):
        self.update_color_from_position(event.pos())
        
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.update_color_from_position(event.pos())
    
    def update_color_from_position(self, pos):
        """Update color based on mouse position"""
        x, y = pos.x(), pos.y()
        changed = False
        
        # Adjust coordinates relative to content area
        rel_x = x - self.content_start_x
        rel_y = y - (self.content_start_y + self.preview_height + self.preview_gap)
        
        if (rel_x >= 0 and rel_x <= self.color_area_width and 
            rel_y >= 0 and rel_y <= self.color_area_height):
            # Click in color area
            new_saturation = max(0, min(1, rel_x / self.color_area_width))
            new_brightness = max(0, min(1, 1.0 - (rel_y / self.color_area_height)))
            
            if new_saturation != self.saturation or new_brightness != self.brightness:
                self.saturation = new_saturation
                self.brightness = new_brightness
                self.color_pos = QPoint(x, y)
                changed = True
            
        elif (x >= self.content_start_x + self.color_area_width + self.gap and 
              x <= self.content_start_x + self.color_area_width + self.gap + self.hue_strip_width and
              rel_y >= 0 and rel_y <= self.color_area_height):
            # Click in hue strip
            new_hue = max(0, min(1, rel_y / self.color_area_height))
            
            if new_hue != self.hue:
                self.hue = new_hue
                self.hue_pos = y
                changed = True
        
        if changed:
            # Update selected color
            self.selected_color = QColor.fromHsvF(self.hue, self.saturation, self.brightness)
            self.colorChanged.emit(self.selected_color)
            self.update()
    
    def set_color(self, color):
        """Set the color programmatically"""
        self.selected_color = QColor(color)
        h, s, v, _ = self.selected_color.getHsvF()
        self.hue = h if h >= 0 else 0
        self.saturation = s
        self.brightness = v
        
        # Update positions
        self.color_pos = QPoint(
            self.content_start_x + int(self.saturation * self.color_area_width),
            self.content_start_y + self.preview_height + self.preview_gap + int((1.0 - self.brightness) * self.color_area_height)
        )
        self.hue_pos = self.content_start_y + self.preview_height + self.preview_gap + int(self.hue * self.color_area_height)
        self.update()

class ColorPickerDialog(QDialog):
    def __init__(self, initial_color=QColor(255, 0, 255), parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Color")
        self.setFixedSize(350, 420)  # Slightly larger for better proportions
        self.selected_color = QColor(initial_color)
        
        # Set window attributes for proper closing behavior
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        
        # Apply dark theme styling
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
            QPushButton {
                background-color: #404040;
                color: #e0e0e0;
                border: 2px solid #606060;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                font-family: 'JetBrains Mono', 'Consolas', 'Monaco', monospace;
                min-width: 80px;
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
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)  # Optimized spacing for better fit
        layout.setContentsMargins(20, 20, 20, 20)  # Reduced margins to maximize space
        
        # Color wheel centered both horizontally and vertically
        self.color_wheel = ColorWheel(300, 200)  # Increased size to better fill the dialog
        self.color_wheel.set_color(self.selected_color)
        self.color_wheel.colorChanged.connect(self.on_color_changed)
        
        # Center the color wheel with minimal spacing
        wheel_layout = QVBoxLayout()
        wheel_layout.addStretch(1)  # Minimal stretch above
        
        wheel_h_layout = QHBoxLayout()
        wheel_h_layout.addStretch()  # Add stretch to the left
        wheel_h_layout.addWidget(self.color_wheel)
        wheel_h_layout.addStretch()  # Add stretch to the right
        
        wheel_layout.addLayout(wheel_h_layout)
        wheel_layout.addStretch(1)  # Minimal stretch below
        layout.addLayout(wheel_layout)
        
        # Hex input with compact styling
        hex_layout = QVBoxLayout()
        hex_layout.setSpacing(8)  # Reduced space for compact layout
        
        hex_label = QLabel("HEX:")
        hex_label.setFont(QFont("JetBrains Mono", 12, QFont.Bold))
        hex_layout.addWidget(hex_label)
        
        self.hex_input = QLineEdit()
        self.hex_input.setPlaceholderText("#FF00FF")
        self.hex_input.setText(self.selected_color.name().upper())
        self.hex_input.textChanged.connect(self.on_hex_changed)
        hex_layout.addWidget(self.hex_input)
        
        layout.addLayout(hex_layout)
        
        # Buttons with compact spacing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)  # Slightly reduced space between buttons
        button_layout.addStretch()  # Push buttons to the right
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
    
    def on_color_changed(self, color):
        """Handle color change from wheel"""
        self.selected_color = color
        # Update hex input without triggering textChanged
        self.hex_input.blockSignals(True)
        self.hex_input.setText(color.name().upper())
        self.hex_input.blockSignals(False)
    
    def on_hex_changed(self, text):
        """Handle hex input change"""
        if len(text) == 7 and text.startswith('#'):
            try:
                color = QColor(text)
                if color.isValid():
                    self.selected_color = color
                    self.color_wheel.set_color(color)
            except:
                pass
    
    def get_selected_color(self):
        """Get the selected color"""
        return self.selected_color
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.accept()
        if self.parent() is None:  # Only quit if this is a standalone dialog
            QApplication.quit()

# Test the color picker
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)  # Ensure app quits when last window closes
    
    dialog = ColorPickerDialog(QColor("#FF00FF"))
    dialog.show()  # Use show() instead of exec_() for standalone testing
    
    sys.exit(app.exec_())
