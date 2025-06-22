import serial
import serial.tools.list_ports
import time
import threading
import json
import os
from pynput.keyboard import Key, Controller
import subprocess

# Initialize keyboard controller
keyboard = Controller()

# Load the configuration file
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return None

def find_kommpad(baudrate=9600, timeout=2):
    """Search all COM ports for a device that identifies as 'KommPad'"""
    print("Searching for KommPad on available COM ports...")
    
    # Get a list of all available COM ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        print("No COM ports found. Make sure your device is connected.")
        return None
    
    print(f"Found {len(ports)} COM ports to check.")
    
    for port in ports:
        # Display detailed port information
        print(f"\nPort: {port.device}")
        print(f"  Description: {port.description}")
        print(f"  Hardware ID: {port.hwid}")
        if hasattr(port, 'manufacturer') and port.manufacturer:
            print(f"  Manufacturer: {port.manufacturer}")
        if hasattr(port, 'product') and port.product:
            print(f"  Product: {port.product}")
        
        print(f"Trying {port.device}... ", end='', flush=True)
        try:
            # Try to open the port
            ser = serial.Serial(port.device, baudrate=baudrate, timeout=timeout)
            
            # Reset the device by toggling DTR
            print("Resetting device... ", end='', flush=True)
            ser.dtr = False  # Set DTR line low
            time.sleep(0.1)  # Brief pause
            ser.dtr = True   # Set DTR line high
            time.sleep(0.1)  # Brief pause
            ser.dtr = False  # Set DTR line low again
            
            # Wait a moment for the device to reset and initialize
            time.sleep(2)
            
            # Clear any initial data
            ser.reset_input_buffer()
            
            # Send ping command to identify the device
            print("Pinging device... ", end='', flush=True)
            ser.write(b'ping\n')
            
            # Read data for a few seconds to see if we get the KommPad identification
            start_time = time.time()
            while (time.time() - start_time) < 3:  # Listen for 3 seconds
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    
                    if "pong KommPad" in line or "KommPad" in line:
                        print(f"Success! KommPad found.")
                        return ser
                    
                    # Print other messages we might receive
                    if line:
                        print(f"\nReceived: {line}")
                
                time.sleep(0.3)
            
            # Close the port if it's not the KommPad
            print(" Not a KommPad.")
            ser.close()
            
        except (serial.SerialException, OSError) as e:
            print(f"Error: {str(e)}")
    
    return None

def get_key_from_string(key_str):
    """Convert string representation of key to pynput Key object if special key"""
    special_keys = {
        'CTRL': Key.ctrl, 'ALT': Key.alt, 'SHIFT': Key.shift,
        'ENTER': Key.enter, 'ESC': Key.esc, 'TAB': Key.tab,
        'SPACE': Key.space, 'BACKSPACE': Key.backspace,
        'DELETE': Key.delete, 'INSERT': Key.insert,
        'HOME': Key.home, 'END': Key.end,
        'PAGE_UP': Key.page_up, 'PAGE_DOWN': Key.page_down,
        'UP': Key.up, 'DOWN': Key.down, 'LEFT': Key.left, 'RIGHT': Key.right,
        'F1': Key.f1, 'F2': Key.f2, 'F3': Key.f3, 'F4': Key.f4,
        'F5': Key.f5, 'F6': Key.f6, 'F7': Key.f7, 'F8': Key.f8,
        'F9': Key.f9, 'F10': Key.f10, 'F11': Key.f11, 'F12': Key.f12
    }
    
    return special_keys.get(key_str.upper(), key_str)

def execute_function(function_name):
    """Execute special functions like volume control"""
    print(f"Executing function: {function_name}")
    
    if function_name == "volumeUp":
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        return True
    elif function_name == "volumeDown":
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        return True
    elif function_name == "mute":
        keyboard.press(Key.media_volume_mute)
        keyboard.release(Key.media_volume_mute)
        return True
    
    print(f"Unknown function: {function_name}")
    return False

def handle_button_press(config, button_number, ser=None):
    """Process button press according to JSON config (layer 1 only)"""
    button_key = f"button{button_number}"
    
    if not config or "mappings" not in config or button_key not in config["mappings"]:
        print(f"No mapping found for {button_key}")
        return
    
    # Get the layer 1 action for this button
    button_config = config["mappings"][button_key]["layer1"]
    action_type = button_config.get("action")
    action_value = button_config.get("value")
    
    print(f"Executing: {action_type} - {action_value} ({button_config.get('description', 'No description')})")
    
    # Process the action locally on the PC
    if action_type == "key":
        key_value = get_key_from_string(action_value)
        print(f"Pressing key: {key_value}")
        keyboard.press(key_value)
        keyboard.release(key_value)
        
    elif action_type == "macro":
        print(f"Executing macro: {'+'.join(action_value)}")
        # Press all keys in the combination
        keys = [get_key_from_string(k) for k in action_value]
        
        # Press all keys in sequence
        for key in keys:
            keyboard.press(key)
        
        # Release all keys in reverse order
        for key in reversed(keys):
            keyboard.release(key)
            
    elif action_type == "function":
        execute_function(action_value)

def read_serial(ser, config):
    """Continuously read from the serial port and process commands"""
    print("Monitoring device output (Ctrl+C to exit):")
    print("-" * 40)
    
    try:
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if line:
                    print(f"← {line}")
                    
                    # Handle button press messages
                    if line.startswith("b "):
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                button_number = int(parts[1])
                                handle_button_press(config, button_number)
                            except ValueError:
                                print(f"Invalid button number: {parts[1]}")
                    
            time.sleep(0.1)
    except serial.SerialException as e:
        print(f"\nError reading from device: {e}")
        print("Device may have been disconnected.")
    except UnicodeDecodeError:
        print("\nReceived data that couldn't be decoded as text.")

def main():
    # Load configuration
    config = load_config()
    if not config:
        print("Failed to load configuration. Using default settings.")
    else:
        print(f"Loaded configuration for {config.get('device', {}).get('name', 'Unknown device')}")
    
    # Find the KommPad device
    baudrate = 9600  # Default baudrate, adjust if needed
    print(f"Searching for KommPad (expecting 'pong KommPad' message)")
    print(f"Using baud rate: {baudrate}")
    
    ser = find_kommpad(baudrate=baudrate)
    
    if not ser:
        print("\nKommPad not found. Make sure it's connected and try again.")
        return
    
    print(f"\nConnected to KommPad on {ser.port} at {ser.baudrate} baud.")
    
    # Start a thread to continuously read from the serial port
    read_thread = threading.Thread(target=read_serial, args=(ser, config), daemon=True)
    read_thread.start()
    
    print("\nEnter commands to send to the KommPad (or 'exit' to quit):")
    
    try:
        while True:
            command = input("> ")
            if command.lower() == 'exit':
                break
                
            # Send the command to the device
            ser.write((command + '\n').encode('utf-8'))
            print(f"→ {command}")
    
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()