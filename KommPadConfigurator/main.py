import serial
import serial.tools.list_ports
import time
import threading
import json
import os
import sys
from pynput.keyboard import Key, Controller
import subprocess
from device_detector import find_kommpad, get_last_port_info, ping_device, get_device_info
from button_handler import handle_button_press, handle_encoder_press, handle_encoder_rotation
from serial_utils import write_serial, set_serial_connection
import pystray
from PIL import Image
import webbrowser

# Initialize keyboard controller
keyboard = Controller()

# Global config path
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

# Global variables for the application state
app_state = {
    'connected': False,
    'device_port': None,
    'device_info': None,
    'serial_connection': None,
    'config': None, 
    'tray_icon': None,
    'current_layer': 0,  # Current layer (0-3)
    'device_monitoring_enabled': True,  # Toggle for device monitoring
    'monitoring_thread_running': False  # Flag to control monitoring thread
}

# Load the configuration file
def load_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        # Load device monitoring setting
        settings = config.get("settings", {})
        app_state['device_monitoring_enabled'] = settings.get("EnableDeviceMonitoring", True)
        
        return config
    except Exception as e:
        print(f"Error loading config: {e}")
        # Set default device monitoring if config fails to load
        app_state['device_monitoring_enabled'] = True
        return None

def get_config_path():
    """Get the path to the config.json file"""
    return CONFIG_PATH

def force_config_reload():
    """Force a reload of the configuration (can be called by UI)"""
    reload_config()

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
                    elif parts[0].startswith("encoder"):
                        try:
                            handle_encoder_press(config, parts[0], parts[1])
                        except ValueError:
                            print(f"Invalid encoder or layer: {line}")

            time.sleep(0.1)
    except serial.SerialException as e:
        print(f"Device disconnected: {e}")
        app_state['connected'] = False
        update_tray_status(False)
    except PermissionError as e:
        print("Device disconnected (unplugged)")
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
        
        ser = find_kommpad(baudrate=9600, timeout=1, debug=False)
        
        if ser:
            app_state['serial_connection'] = ser
            set_serial_connection(ser)  # Update serial_utils
            app_state['device_port'] = ser.port
            app_state['connected'] = True
            app_state['device_info'] = config.get('device', {})
            
            print(f"Connected to KommPad on {ser.port}")
            update_tray_status(True)
            
            # Send current configuration immediately after initial connection
            try:
                from device_detector import send_settings_to_macropad
                send_settings_to_macropad(ser, app_state['config'])
                print("Initial configuration sent to macropad")
            except Exception as e:
                print(f"Error sending initial configuration to device: {e}")
            
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
    
    # Start config file watcher
    config_watcher_thread = threading.Thread(target=watch_config_file, daemon=True)
    config_watcher_thread.start()
    
    # Start device monitor for automatic reconnection when new devices are plugged in
    device_monitor_thread = threading.Thread(target=monitor_for_new_devices, daemon=True)
    device_monitor_thread.start()
    
    print("Running in system tray. Right-click tray icon for options.")
    
    # Run the tray icon (this blocks until quit)
    try:
        tray_icon.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Cleanup
        app_state['monitoring_thread_running'] = False  # Stop monitoring thread
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
    """Launch the UI configurator"""
    try:
        # Path to the UI configurator script
        ui_script_path = os.path.join(os.path.dirname(__file__), 'ConfiguratorUI', 'main_ui.py')
        
        if os.path.exists(ui_script_path):
            # Launch the UI configurator in a separate process
            python_executable = sys.executable
            subprocess.Popen([python_executable, ui_script_path])
            print("Launching KommPad UI Configurator...")
        else:
            print(f"UI configurator not found at: {ui_script_path}")
            # Fallback to opening config file in text editor
            if os.path.exists(CONFIG_PATH):
                if os.name == 'nt':  # Windows
                    os.startfile(CONFIG_PATH)
                elif os.name == 'posix':  # macOS and Linux
                    print("DEBUG: Opening config file with macOS/Linux default application")
                    subprocess.call(['open', CONFIG_PATH])
            else:
                print(f"DEBUG: Config file not found at: {CONFIG_PATH}")
    except Exception as e:
        print(f"Error launching configurator: {e}")
        print(f"DEBUG: Exception details: {type(e).__name__}: {str(e)}")

def reload_config():
    """Reload the configuration file"""
    try:
        print("Reloading configuration...")
        config = load_config()
        if config:
            app_state['config'] = config
            # Device monitoring setting is updated in load_config()
            print(f"Configuration reloaded successfully for {config.get('device', {}).get('name', 'Unknown device')}")
            print(f"Device monitoring: {'Enabled' if app_state['device_monitoring_enabled'] else 'Disabled'}")
        else:
            print("Failed to reload configuration - using existing settings")
    except Exception as e:
        print(f"Error reloading config: {e}")
        # Attempt to reconnect
        reconnect_device()

def watch_config_file():
    """Watch for changes to the config file and reload when modified"""
    import time
    last_modified = 0
    
    try:
        if os.path.exists(CONFIG_PATH):
            last_modified = os.path.getmtime(CONFIG_PATH)
    except:
        pass
    
    while True:
        try:
            if os.path.exists(CONFIG_PATH):
                current_modified = os.path.getmtime(CONFIG_PATH)
                if current_modified > last_modified:
                    time.sleep(0.1)  # Small delay to ensure file write is complete
                    reload_config()
                    
                    # Only send new settings if device is connected, don't reconnect unnecessarily
                    if app_state['connected'] and app_state['serial_connection']:
                        try:
                            # Import here to avoid circular imports
                            from device_detector import send_settings_to_macropad
                            send_settings_to_macropad(app_state['serial_connection'], app_state['config'])
                            print("Updated settings sent to macropad")
                        except Exception as e:
                            print(f"Error sending updated settings: {e}")
                            # Only reconnect if sending settings failed
                            print("Attempting to reconnect due to settings update failure...")
                            reconnect_device()
                    elif not app_state['connected']:
                        # Only try to reconnect if we're not connected
                        print("Device not connected, attempting to reconnect...")
                        reconnect_device()
                    
                    last_modified = current_modified
            time.sleep(1)  # Check every second
        except Exception as e:
            print(f"Error watching config file: {e}")
            time.sleep(5)  # Wait longer on error

def reconnect_device():
    """Attempt to reconnect to the KommPad device"""
    print("Reconnecting to device...")
    update_tray_status(False)  # Show disconnected status
    
    # Stop current connection if exists
    if app_state['serial_connection'] and app_state['serial_connection'].is_open:
        try:
            app_state['serial_connection'].close()
        except:
            pass  # Ignore errors when closing
        app_state['serial_connection'] = None
    
    # Try to find device again (with reduced timeout for faster reconnection)
    ser = find_kommpad(baudrate=9600, timeout=1, debug=False)

    if ser:
        app_state['serial_connection'] = ser
        set_serial_connection(ser)  # Update serial_utils
        app_state['device_port'] = ser.port
        app_state['connected'] = True
        update_tray_status(True)
        
        # Send current configuration immediately after reconnection
        try:
            from device_detector import send_settings_to_macropad
            send_settings_to_macropad(ser, app_state['config'])
            print("Configuration sent to newly connected device")
        except Exception as e:
            print(f"Error sending configuration to device: {e}")
        
        # Start serial reading thread
        read_thread = threading.Thread(target=read_serial, args=(ser, app_state['config']), daemon=True)
        read_thread.start()

        print(f"Reconnected to KommPad on {ser.port}")
    else:
        app_state['connected'] = False
        app_state['device_port'] = None
        print("Reconnection failed - device not found")

def monitor_for_new_devices():
    """Monitor for new devices being plugged in when disconnected"""
    import time
    last_ports = set()
    consecutive_errors = 0
    max_errors = 3
    
    # Set monitoring thread as running
    app_state['monitoring_thread_running'] = True
    
    # Get initial list of COM ports
    try:
        current_ports = set(port.device for port in serial.tools.list_ports.comports())
        last_ports = current_ports.copy()
        consecutive_errors = 0
    except Exception as e:
        print(f"Error getting initial COM ports: {e}")
        current_ports = set()
        last_ports = set()
        consecutive_errors += 1
    
    print(f"Device monitor started - Monitoring: {'Enabled' if app_state['device_monitoring_enabled'] else 'Disabled'}")
    
    while app_state['monitoring_thread_running']:
        try:
            # Only monitor if enabled in settings and when disconnected
            if app_state['device_monitoring_enabled'] and not app_state['connected']:
                # Get current COM ports (this is the main performance impact)
                current_ports = set(port.device for port in serial.tools.list_ports.comports())
                
                # Check if any new ports have been added
                new_ports = current_ports - last_ports
                
                if new_ports:
                    print(f"New COM port(s) detected: {', '.join(new_ports)}")
                    
                    # Try to connect to new ports, but limit to prevent excessive attempts
                    for port in list(new_ports)[:3]:  # Limit to 3 new ports max per cycle
                        # Check if monitoring is still enabled before attempting connection
                        if not app_state['device_monitoring_enabled']:
                            break
                            
                        try:
                            print(f"Checking if {port} is a KommPad...")
                            # Use a very short timeout for quick detection
                            ser = find_kommpad(baudrate=9600, timeout=0.3, debug=False)
                            
                            if ser:
                                print(f"KommPad detected on new port: {ser.port}")
                                
                                # Update app state
                                app_state['serial_connection'] = ser
                                set_serial_connection(ser)
                                app_state['device_port'] = ser.port
                                app_state['connected'] = True
                                update_tray_status(True)
                                
                                # Send current configuration
                                try:
                                    from device_detector import send_settings_to_macropad
                                    send_settings_to_macropad(ser, app_state['config'])
                                    print("Configuration sent to newly detected device")
                                except Exception as e:
                                    print(f"Error sending configuration to newly detected device: {e}")
                                
                                # Start serial reading thread
                                read_thread = threading.Thread(target=read_serial, args=(ser, app_state['config']), daemon=True)
                                read_thread.start()
                                
                                print(f"Auto-connected to KommPad on {ser.port}")
                                break  # Stop checking other new ports
                                
                        except Exception:
                            # Silently continue if this port isn't a KommPad
                            pass
                
                # Update the list of known ports
                last_ports = current_ports.copy()
                consecutive_errors = 0  # Reset error counter on success
                
                # Dynamic sleep interval based on connection state and monitoring enabled
                time.sleep(3)  # Check every 3 seconds when monitoring is enabled and disconnected
                
            elif app_state['device_monitoring_enabled'] and app_state['connected']:
                # If connected and monitoring enabled, check less frequently and just update port list
                try:
                    current_ports = set(port.device for port in serial.tools.list_ports.comports())
                    last_ports = current_ports.copy()
                    consecutive_errors = 0
                except:
                    consecutive_errors += 1
                
                # Much longer sleep when connected (device monitoring not critical)
                time.sleep(10)  # Check every 10 seconds when connected
            
            else:
                # Monitoring is disabled - sleep longer and just check if it gets re-enabled
                time.sleep(5)  # Check every 5 seconds if monitoring gets re-enabled
            
        except Exception as e:
            consecutive_errors += 1
            if consecutive_errors <= max_errors:
                print(f"Error in device monitor: {e}")
            
            # Exponential backoff on repeated errors
            error_sleep = min(10 + (consecutive_errors * 2), 30)  # Max 30 seconds
            time.sleep(error_sleep)
    
    print("Device monitoring thread stopped")

def quit_application(icon, item):
    """Quit the application"""
    print("Shutting down KommPad Configurator...")
    
    # Stop device monitoring thread
    app_state['monitoring_thread_running'] = False
    
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
        tooltip += "\nRight-click for menu"
        app_state['tray_icon'].title = tooltip

def toggle_device_monitoring(icon, item):
    """Toggle device monitoring on/off"""
    app_state['device_monitoring_enabled'] = not app_state['device_monitoring_enabled']
    
    # Update the config file with the new setting
    try:
        config = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
        
        # Update settings section
        if "settings" not in config:
            config["settings"] = {}
        
        config["settings"]["EnableDeviceMonitoring"] = app_state['device_monitoring_enabled']
        
        # Save config file
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        # Update app config
        app_state['config'] = config
        
        status = "enabled" if app_state['device_monitoring_enabled'] else "disabled"
        print(f"Device monitoring {status}")
        
        # Update the tray menu to reflect new state
        app_state['tray_icon'].menu = create_tray_menu()
        
    except Exception as e:
        print(f"Error toggling device monitoring: {e}")

def create_tray_menu():
    """Create the context menu for the tray icon"""
    monitoring_text = "🔍 Disable Auto-Detection" if app_state['device_monitoring_enabled'] else "🔍 Enable Auto-Detection"
    
    return pystray.Menu(
        pystray.MenuItem("📋 Open Configurator", lambda icon, item: open_config_file(), default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("🔄 Reconnect Device", lambda icon, item: reconnect_device()),
        pystray.MenuItem("🔃 Reload Config", lambda icon, item: reload_config()),
        pystray.MenuItem(monitoring_text, toggle_device_monitoring),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("❌ Quit", quit_application)
    )

def setup_tray_icon():
    """Setup and run the system tray icon"""
    # Load initial image (disconnected)
    image = load_tray_image(False)
    
    # Create tray icon - simplified approach
    app_state['tray_icon'] = pystray.Icon(
        "KommPad",
        image,
        "KommPad - Disconnected\nRight-click for menu",
        menu=create_tray_menu()
    )
    
    return app_state['tray_icon']

if __name__ == "__main__":
    main()