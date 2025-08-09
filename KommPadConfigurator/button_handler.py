"""
Button Handler Module for KommPad Configurator
Handles all button press actions including keys, macros, and functions
"""

from pynput.keyboard import Key, Controller
from serial_utils import write_serial
import subprocess
import os

# Initialize keyboard controller
keyboard = Controller()

def get_key_from_string(key_str):
    """Convert string representation of key to pynput Key object if special key"""
    special_keys = {
        # keyboard keys
        'CTRL': Key.ctrl, 'ALT': Key.alt, 'SHIFT': Key.shift,
        'ENTER': Key.enter, 'ESC': Key.esc, 'TAB': Key.tab,
        'SPACE': Key.space, 'BACKSPACE': Key.backspace,
        'DELETE': Key.delete, 'INSERT': Key.insert,
        'HOME': Key.home, 'END': Key.end,
        'PAGE_UP': Key.page_up, 'PAGE_DOWN': Key.page_down,
        'UP': Key.up, 'DOWN': Key.down, 'LEFT': Key.left, 'RIGHT': Key.right,
        'F1': Key.f1, 'F2': Key.f2, 'F3': Key.f3, 'F4': Key.f4,
        'F5': Key.f5, 'F6': Key.f6, 'F7': Key.f7, 'F8': Key.f8,
        'F9': Key.f9, 'F10': Key.f10, 'F11': Key.f11, 'F12': Key.f12,
        # media keys
        'MEDIA_VOLUME_UP': Key.media_volume_up,
        'MEDIA_VOLUME_DOWN': Key.media_volume_down,
        'MEDIA_VOLUME_MUTE': Key.media_volume_mute,
        'MEDIA_PLAY_PAUSE': Key.media_play_pause,
        'MEDIA_NEXT': Key.media_next,
        'MEDIA_PREVIOUS': Key.media_previous,
        'MEDIA_STOP': Key.media_stop,
        
        
    }
    
    return special_keys.get(key_str.upper(), key_str)

def execute_key_action(key_value, modifiers=None):
    # Execute a single key action with optional modifierss
    # modifiers can be a single key or a list of keys
    # join value with modifiers if provided in keys
    keys = []
    if modifiers:
        keys.extend(get_key_from_string(mod) for mod in modifiers)
    keys.append(get_key_from_string(key_value))

    
    # Press all keys in sequence
    for key in keys:
        keyboard.press(key)
    # Release all keys in reverse order
    for key in reversed(keys):
        keyboard.release(key)
     
def execute_macro_action(macro_keys):
    """Execute a key combination macro"""
    # Convert string keys to pynput Key objects
    keys = [get_key_from_string(k) for k in macro_keys]
    
    # Press all keys in sequence
    for key in keys:
        keyboard.press(key)
    
    # Release all keys in reverse order
    for key in reversed(keys):
        keyboard.release(key)

def execute_media_action(media_value):
    """Execute media control actions"""
    
    if media_value == "Volume_Up":
        keyboard.press(Key.media_volume_up)
        keyboard.release(Key.media_volume_up)
        return True
        
    elif media_value == "Volume_Down":
        keyboard.press(Key.media_volume_down)
        keyboard.release(Key.media_volume_down)
        return True
        
    elif media_value == "Volume_Mute":
        keyboard.press(Key.media_volume_mute)
        keyboard.release(Key.media_volume_mute)
        return True
        
    elif media_value == "Media_Next":
        keyboard.press(Key.media_next)
        keyboard.release(Key.media_next)
        return True
        
    elif media_value == "Media_Previous":
        keyboard.press(Key.media_previous)
        keyboard.release(Key.media_previous)
        return True
        
    elif media_value == "Media_Play_Pause":
        keyboard.press(Key.media_play_pause)
        keyboard.release(Key.media_play_pause)
        return True
        
    else:
        print(f"Unknown media action: {media_value}")
        return False

def execute_function_action(function_name, modifiers=None):
    """Execute special functions like volume control, brightness, etc."""
    
    if function_name == "Layer_Up":
        write_serial("layerUp")
        print("Layer up command sent")
        return True
    
    elif function_name == "Open_Web":
        if modifiers and isinstance(modifiers, list):
            url = next((mod[4:] for mod in modifiers if mod.startswith("url:")), None)
            if url:
                try:
                    import webbrowser
                    webbrowser.open(url)
                    print(f"Opening URL: {url}")
                except Exception as e:
                    print(f"Error opening URL: {e}")
            else:
                print("No URL found in modifiers for Open_Web")
        else:
            print("No valid URL modifier provided for Open_Web")
        return True

    elif function_name == "Open_App":
        if modifiers and isinstance(modifiers, list):
            exe_path = next((mod[4:] for mod in modifiers if mod.startswith("exe:")), None)
            if exe_path:
                try:
                    # Try different approaches to launch the application
                    if os.path.isabs(exe_path) and os.path.exists(exe_path):
                        # Absolute path that exists
                        subprocess.Popen([exe_path])
                        print(f"Opening application: {exe_path}")
                    elif exe_path.endswith('.exe'):
                        # Try to find the executable in PATH or use shell=True for Windows
                        if os.name == 'nt':  # Windows
                            subprocess.Popen(exe_path, shell=True)
                            print(f"Opening application via shell: {exe_path}")
                        else:
                            subprocess.Popen([exe_path])
                            print(f"Opening application: {exe_path}")
                    else:
                        # Treat as application name and let the shell handle it
                        subprocess.Popen(exe_path, shell=True)
                        print(f"Opening application via shell: {exe_path}")
                except FileNotFoundError:
                    print(f"Application not found: {exe_path}")
                    print("Make sure the executable path is correct or the application is installed")
                except Exception as e:
                    print(f"Error opening application: {e}")
                    print(f"Tried to open: {exe_path}")
            else:
                print("No executable path found in modifiers for Open_App")
        else:
            print("No valid executable modifier provided for Open_App")
        return True
    
    elif function_name == "Text":
        if modifiers and isinstance(modifiers, list):
            keyboard.type(modifiers[0].split(":")[1])  
            return True

    else:
        print(f"Unknown function action: {function_name}")
        return False  

def handle_button_press(config, button_key, layer_key):
    """
    Process button press according to JSON config using specified layer
    
    Args:
        config (dict): Configuration dictionary loaded from config.json
        button_key (str): Button identifier (e.g., "button1", "encoder1")
        layer_key (str): Layer identifier (e.g., "layer0", "layer1")
    """
    
    if not config or "mappings" not in config or button_key not in config["mappings"]:
        print(f"No mapping found for {button_key}")
        return
    
    # Get the button mappings
    button_mappings = config["mappings"][button_key]
    
    # Check if the layer exists for this button
    if layer_key not in button_mappings:
        print(f"No mapping found for {button_key} on {layer_key}")
        return
    
    # Get the action configuration for this button and layer
    button_config = button_mappings[layer_key]
    action_type = button_config.get("action")
    action_value = button_config.get("value")
    action_modifiers = button_config.get("modifiers", None)
    
    # Execute the appropriate action
    if action_type == "key":
        execute_key_action(action_value, action_modifiers)
        
    elif action_type == "macro":
        execute_macro_action(action_value)
        
    elif action_type == "media":
        execute_media_action(action_value)
        
    elif action_type == "function":
        execute_function_action(action_value, action_modifiers)
        
    else:
        print(f"Unknown action type: {action_type}")

def handle_encoder_press(config, encoder_key, layer_key):
    """
    Handle encoder button presses (same as regular buttons but with different naming)
    
    Args:
        config (dict): Configuration dictionary loaded from config.json
        encoder_key (str): Encoder identifier (e.g., "encoder1", "encoder2")
        layer_key (str): Layer identifier (e.g., "layer0", "layer1")
    """
    handle_button_press(config, encoder_key, layer_key)

def handle_encoder_rotation(config, encoder_key, direction, layer_key):
    """
    Handle encoder rotation events
    
    Args:
        config (dict): Configuration dictionary loaded from config.json
        encoder_key (str): Encoder identifier (e.g., "encoder1_cw", "encoder1_ccw")
        direction (str): Rotation direction ("cw" for clockwise, "ccw" for counter-clockwise)
        layer_key (str): Layer identifier (e.g., "layer0", "layer1")
    """
    # Create the rotation-specific key
    rotation_key = f"{encoder_key}_{direction}"
    handle_button_press(config, rotation_key, layer_key)
