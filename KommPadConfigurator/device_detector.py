import serial
import serial.tools.list_ports
import time
import json
import os

# Configuration file for storing device settings including last connected port
CONFIG_FILE = "config.json"

def find_kommpad(baudrate=9600, timeout=2, debug=True):
    """
    Search all COM ports for a device that responds to 'ping' with 'KommPong'
    Tries the last successful port first for faster connection.
    
    Args:
        baudrate (int): Serial communication baud rate (default: 9600)
        timeout (int): Serial timeout in seconds (default: 2)
        debug (bool): Print debug information (default: True)
    
    Returns:
        serial.Serial: Connected serial object if KommPad found, None otherwise
    """
    if debug:
        print("Searching for KommPad on available COM ports...")
    
    # First, try the last known working port
    last_port = load_last_port()
    if last_port:
        if debug:
            print(f"Trying last known port: {last_port}")
        
        # Check if the port still exists
        available_ports = [port.device for port in serial.tools.list_ports.comports()]
        if last_port in available_ports:
            ser = try_connect_to_port(last_port, baudrate, timeout, debug)
            if ser:
                # Send settings to the macropad after successful connection
                app_state = load_app_state()  # Assuming a function to load app state
                send_settings_to_macropad(ser, app_state)
                return ser
        else:
            if debug:
                print(f"Last port {last_port} no longer available.")
    
    # Get a list of all available COM ports
    ports = list(serial.tools.list_ports.comports())
    
    if not ports:
        if debug:
            print("No COM ports found. Make sure your device is connected.")
        return None
    
    if debug:
        print(f"Found {len(ports)} COM ports to check.")
    
    # Try all other ports (excluding the last port if we already tried it)
    for port in ports:
        if last_port and port.device == last_port:
            continue  # Skip the last port since we already tried it
            
        if debug:
            # Display detailed port information
            print(f"\nPort: {port.device}")
            print(f"  Description: {port.description}")
            print(f"  Hardware ID: {port.hwid}")
            if hasattr(port, 'manufacturer') and port.manufacturer:
                print(f"  Manufacturer: {port.manufacturer}")
            if hasattr(port, 'product') and port.product:
                print(f"  Product: {port.product}")
        
        ser = try_connect_to_port(port.device, baudrate, timeout, debug)
        if ser:
            # Send settings to the macropad after successful connection
            app_state = load_app_state()  # Assuming a function to load app state
            send_settings_to_macropad(ser, app_state)
            return ser
    
    if debug:
        print("\nKommPad not found on any available COM port.")
    return None

def ping_device(ser, timeout=2):
    """
    Ping an already connected device to verify it's still a KommPad
    
    Args:
        ser (serial.Serial): Connected serial object
        timeout (int): Response timeout in seconds
    
    Returns:
        bool: True if device responds with KommPong, False otherwise
    """
    if not ser or not ser.is_open:
        return False
    
    try:
        # Clear input buffer
        ser.reset_input_buffer()
        
        # Send ping
        ser.write(b'ping\n')
        
        # Wait for response
        start_time = time.time()
        while (time.time() - start_time) < timeout:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                if "KommPong" in line:
                    return True
            time.sleep(0.1)
        
        return False
        
    except (serial.SerialException, OSError):
        return False

def get_device_info(port_device):
    """
    Get detailed information about a specific COM port
    
    Args:
        port_device (str): Port device name (e.g., 'COM9')
    
    Returns:
        dict: Port information or None if port not found
    """
    ports = list(serial.tools.list_ports.comports())
    
    for port in ports:
        if port.device == port_device:
            info = {
                'device': port.device,
                'description': port.description,
                'hwid': port.hwid
            }
            
            if hasattr(port, 'manufacturer') and port.manufacturer:
                info['manufacturer'] = port.manufacturer
            if hasattr(port, 'product') and port.product:
                info['product'] = port.product
            if hasattr(port, 'serial_number') and port.serial_number:
                info['serial_number'] = port.serial_number
                
            return info
    
    return None

def list_available_ports():
    """
    List all available COM ports with their information
    
    Returns:
        list: List of dictionaries containing port information
    """
    ports = list(serial.tools.list_ports.comports())
    port_list = []
    
    for port in ports:
        info = {
            'device': port.device,
            'description': port.description,
            'hwid': port.hwid
        }
        
        if hasattr(port, 'manufacturer') and port.manufacturer:
            info['manufacturer'] = port.manufacturer
        if hasattr(port, 'product') and port.product:
            info['product'] = port.product
        if hasattr(port, 'serial_number') and port.serial_number:
            info['serial_number'] = port.serial_number
            
        port_list.append(info)
    
    return port_list

def save_last_port(port_device):
    """
    Save the last successfully connected port to config.json
    
    Args:
        port_device (str): Port device name (e.g., 'COM9')
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)

        # Load existing config or create new one
        config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)

        # Ensure device section exists
        if 'device' not in config:
            config['device'] = {}

        # Check if the port is different from the saved one
        if config['device'].get('COM') == port_device:
            return  # No need to save if the port is the same

        # Update only the COM port
        config['device']['COM'] = port_device

        # Save back to file
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

    except Exception as e:
        print(f"Warning: Could not save last port: {e}")

def load_last_port():
    """
    Load the last successfully connected port from config.json
    
    Returns:
        str: Last connected port device name or None if not found
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        if not os.path.exists(config_path):
            return None
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Get the COM port from device section
        device_config = config.get('device', {})
        last_port = device_config.get('COM')
        
        return last_port
        
    except Exception as e:
        print(f"Warning: Could not load last port: {e}")
        return None

def try_connect_to_port(port_device, baudrate=9600, timeout=2, debug=True):
    """
    Try to connect to a specific port and verify it's a KommPad
    
    Args:
        port_device (str): Port device name (e.g., 'COM9')
        baudrate (int): Serial communication baud rate
        timeout (int): Serial timeout in seconds
        debug (bool): Print debug information
    
    Returns:
        serial.Serial: Connected serial object if KommPad found, None otherwise
    """
    if debug:
        print(f"Trying {port_device}... ", end='', flush=True)
    
    try:
        # Try to open the port
        ser = serial.Serial(port_device, baudrate=baudrate, timeout=timeout)
        
        # Clear any initial data
        ser.reset_input_buffer()
        
        if debug:
            print("Pinging device... ", end='', flush=True)
        
        # Send ping command to identify the device
        ser.write(b'ping\n')
        
        # Read data for a few seconds to see if we get the KommPad identification
        start_time = time.time()
        response_received = False
        
        while (time.time() - start_time) < 3:  # Listen for 3 seconds
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='replace').strip()
                
                if debug and line:
                    print(f"\nReceived: '{line}'")
                
                # Check for the KommPong response
                if "KommPong" in line:
                    if debug:
                        print("Success! KommPad found and identified.")
                    # Save this port as the last successful connection
                    save_last_port(port_device)
                    return ser
                
                response_received = True
            
            time.sleep(0.1)
        
        # Close the port if it's not the KommPad
        if debug:
            if response_received:
                print(" Device responded but not a KommPad.")
            else:
                print(" No response from device.")
        
        ser.close()
        return None
        
    except (serial.SerialException, OSError) as e:
        if debug:
            print(f"Error: {str(e)}")
        return None

def clear_last_port():
    """
    Clear the saved last port information from config.json (useful for troubleshooting)
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Remove COM from device section
            if 'device' in config:
                config['device'].pop('COM', None)
            
            # Save back to file
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print("Last port information cleared from config.json.")
        else:
            print("No config.json file found.")
    except Exception as e:
        print(f"Error clearing last port: {e}")

def get_last_port_info():
    """
    Get information about the last connected port from config.json
    
    Returns:
        dict: Last port information or None if not available
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        if not os.path.exists(config_path):
            return None
            
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        device_config = config.get('device', {})
        last_port = device_config.get('COM')
        
        if not last_port:
            return None
            
        return {
            'port': last_port,
            'connected_at': 'Unknown',
            'age_hours': 0
        }
    except Exception as e:
        print(f"Error getting last port info: {e}")
        return None

def send_settings_to_macropad(ser, app_state):
    """
    Send settings to the macropad as a lightweight string.

    Args:
        ser (serial.Serial): The serial connection to the macropad.
        app_state (dict): The application state containing configuration data.
    """
    try:
        if 'settings' in app_state and 'mappings' in app_state:
            settings = app_state['settings']
            # Prepare settings string with layer names
            max_layers = settings.get('MaxLayers', 2)
            layer_names_str = "~".join([settings.get('Layers', {}).get(f"layer{i}", {}).get("name", "") for i in range(4)])
            brightness = settings.get('Brightness', 255)
            color_mode = settings.get('ColorMode', 'solid')
            colors = settings.get('Colors', [])
            colors_str = "~".join(colors) if colors else ""
            idle_timeout = settings.get('idleTimeout', 0)
            # create string of display names of each button for all layers
            mappings = app_state['mappings']
            display_names = []
            display_names_strs = []
            for layer in range(4):
                layer_display_names = []
                layer_key = f"layer{layer}"
                for button in range(1, 7):
                    button_key = f"button{button}"
                    display_name = mappings.get(button_key, {}).get(layer_key, {}).get("display", "")
                    layer_display_names.append(display_name)
                layer_display_names_str = "~".join(layer_display_names)
                display_names_strs.append(layer_display_names_str)
            display_names_str = "|".join(display_names_strs)

            settings_string = f"Settings: {max_layers},{layer_names_str},{brightness},{color_mode},{colors_str},{idle_timeout}"
            display_names_string = f"DisplayNames: {display_names_str}"
            ser.write((display_names_string + '\n').encode('utf-8'))
            ser.write((settings_string + '\n').encode('utf-8'))
            print(f"Settings sent to the macropad: {settings_string}, {display_names_string}")
        else:
            print("Error: 'settings' key is missing in app_state.")
    except Exception as e:
        print(f"Error sending settings to the macropad: {e}")

def load_app_state():
    """
    Load the application state from the config.json file.

    Returns:
        dict: The application state loaded from the config file.
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
        else:
            print("Config file not found. Returning empty state.")
            return {}
    except Exception as e:
        print(f"Error loading app state: {e}")
        return {}

# Test function
def test_device_detector():
    """Test the device detector functionality"""
    print("Testing KommPad Device Detector")
    print("=" * 40)
    
    # Show last port info if available
    last_info = get_last_port_info()
    if last_info:
        print(f"\nLast connected port: {last_info['port']}")
        print(f"Connected at: {last_info['connected_at']}")
        print(f"Age: {last_info['age_hours']:.1f} hours")
    else:
        print("\nNo previous connection history found.")
    
    # List available ports
    print("\nAvailable COM ports:")
    ports = list_available_ports()
    if ports:
        for port in ports:
            print(f"  {port['device']}: {port['description']}")
    else:
        print("  No COM ports found")
    
    # Try to find KommPad
    print(f"\nSearching for KommPad...")
    ser = find_kommpad()
    
    if ser:
        print(f"KommPad found on {ser.port}")
        
        # Test ping functionality
        print("Testing ping functionality...")
        if ping_device(ser):
            print("Ping test successful!")
        else:
            print("Ping test failed!")
        
        ser.close()
        print("Connection closed.")
    else:
        print("KommPad not found.")
        


if __name__ == "__main__":
    test_device_detector()
