import serial
import serial.tools.list_ports
import time
import threading
import json
import os
from pynput.keyboard import Key, Controller
import subprocess
from device_detector import find_kommpad, get_last_port_info, ping_device
from button_handler import handle_button_press, handle_encoder_press, handle_encoder_rotation
from serial_utils import write_serial, set_serial_connection
import pystray
from PIL import Image
import webbrowser

# Initialize keyboard controller
keyboard = Controller()

# Global variables for the application state
app_state = {
    'connected': False,
    'device_port': None,
    'device_info': None,
    'serial_connection': None,
    'config': None,
    'tray_icon': None,
    'current_layer': 0  # Current layer (0-3)
}

# Load the configuration file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def read_serial(ser, config):
    """Continuously read from the serial port and process commands"""
    try:
        while app_state['connected'] and ser.is_open:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    # Handle button press messages in the style "button1 layer0"
                    parts = line.split()
                    if parts[0].startswith("button"):
                        try:
                            handle_button_press(config, parts[0], parts[1])
                        except ValueError:
                            print(f"Invalid button or layer: {line}")
                    
            time.sleep(0.1)
    except serial.SerialException as e:
        print(f"Device disconnected: {e}")
        app_state['connected'] = False
        update_tray_status(False)
    except UnicodeDecodeError:
        pass  # Ignore decode errors

def main():
    print("Starting KommPad Configurator...")
    
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Using default settings.")
        config = {}
    else:
        print(f"Loaded configuration for {config.get('device', {}).get('name', 'Unknown device')}")
    
    # Store config in global state
    app_state['config'] = config
      # Setup tray icon first
    tray_icon = setup_tray_icon()
    # Show last connection info if available
    last_info = get_last_port_info()
    if last_info:
        print(f"Last connected to {last_info['port']}")
    
    # Try to connect to device in a separate thread
    def connect_to_device():
        # Wait a moment for tray icon to be fully initialized
        time.sleep(1)
        
        ser = find_kommpad(baudrate=9600, debug=False)
        
        if ser:
            app_state['serial_connection'] = ser
            set_serial_connection(ser)  # Update serial_utils
            app_state['device_port'] = ser.port
            app_state['connected'] = True
            app_state['device_info'] = config.get('device', {})
            
            print(f"Connected to KommPad on {ser.port}")
            update_tray_status(True)
            
            # Start serial reading thread
            read_thread = threading.Thread(target=read_serial, args=(ser, config), daemon=True)
            read_thread.start()
        else:
            print("KommPad not found. Use tray icon to reconnect.")
            app_state['connected'] = False
            update_tray_status(False)
    
    # Start connection attempt in background
    connect_thread = threading.Thread(target=connect_to_device, daemon=True)
    connect_thread.start()
    
    print("Running in system tray. Right-click tray icon for options.")
    
    # Run the tray icon (this blocks until quit)
    try:
        tray_icon.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        if app_state['serial_connection'] and app_state['serial_connection'].is_open:
            app_state['serial_connection'].close()
        print("KommPad Configurator stopped.")

def load_tray_image(connected=False):
    """Load the appropriate tray icon image"""
    try:
        if connected:
            image_path = os.path.join(os.path.dirname(__file__), 'assets', 'Logo.png')
        else:
            image_path = os.path.join(os.path.dirname(__file__), 'assets', 'Logo_disconnected.png')
        
        if os.path.exists(image_path):
            return Image.open(image_path)
        else:
            # Create a simple fallback image if files don't exist
            color = 'green' if connected else 'red'
            return Image.new('RGB', (64, 64), color=color)
    except Exception as e:
        print(f"Error loading tray image: {e}")
        # Create a simple fallback image
        color = 'green' if connected else 'red'
        return Image.new('RGB', (64, 64), color=color)

def get_device_info_text():
    """Get formatted device information for the tray menu"""
    if app_state['connected'] and app_state['device_info']:
        info = app_state['device_info']
        return f"Device: {info.get('name', 'KommPad')}\nPort: {app_state['device_port']}\nStatus: Connected"
    else:
        return "Device: KommPad\nStatus: Disconnected"

def open_config_file():
    """Open the config.json file with the default editor"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        if os.path.exists(config_path):
            # Try to open with default editor
            if os.name == 'nt':  # Windows
                os.startfile(config_path)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['open', config_path])
        else:
            print("Config file not found!")
    except Exception as e:
        print(f"Error opening config file: {e}")

def reconnect_device():
    """Attempt to reconnect to the KommPad device"""
    print("Attempting to reconnect...")
    update_tray_status(False)  # Show disconnected status
    
    # Stop current connection if exists
    if app_state['serial_connection'] and app_state['serial_connection'].is_open:
        app_state['serial_connection'].close()
      # Try to find device again
    ser = find_kommpad(baudrate=9600, debug=False)
    
    if ser:
        app_state['serial_connection'] = ser
        set_serial_connection(ser)  # Update serial_utils
        app_state['device_port'] = ser.port
        app_state['connected'] = True
        update_tray_status(True)
        
        # Restart the serial reading thread
        read_thread = threading.Thread(target=read_serial, args=(ser, app_state['config']), daemon=True)
        read_thread.start()
        
        print(f"Reconnected to KommPad on {ser.port}")
    else:
        app_state['connected'] = False
        app_state['device_port'] = None
        print("Reconnection failed - device not found")

def quit_application(icon, item):
    """Quit the application"""
    print("Shutting down KommPad Configurator...")
    
    # Close serial connection
    if app_state['serial_connection'] and app_state['serial_connection'].is_open:
        app_state['serial_connection'].close()
    
    # Stop the tray icon
    icon.stop()

def update_tray_status(connected):
    """Update the tray icon to reflect connection status"""
    if app_state['tray_icon']:
        app_state['connected'] = connected
        new_image = load_tray_image(connected)
        app_state['tray_icon'].icon = new_image
        
        # Update tooltip
        tooltip = f"KommPad - {'Connected' if connected else 'Disconnected'}"
        if connected and app_state['device_port']:
            tooltip += f" ({app_state['device_port']})"
        app_state['tray_icon'].title = tooltip

def create_tray_menu():
    """Create the context menu for the tray icon"""
    return pystray.Menu(
        pystray.MenuItem("Configure", lambda icon, item: open_config_file()),
        pystray.MenuItem("Reconnect", lambda icon, item: reconnect_device()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Quit", quit_application)
    )

def setup_tray_icon():
    """Setup and run the system tray icon"""
    # Load initial image (disconnected)
    image = load_tray_image(False)
    
    # Create tray icon
    app_state['tray_icon'] = pystray.Icon(
        "KommPad",
        image,
        "KommPad - Disconnected",
        menu=create_tray_menu()
    )
    
    return app_state['tray_icon']

if __name__ == "__main__":
    main()