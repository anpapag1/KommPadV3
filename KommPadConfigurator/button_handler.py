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

def execute_key_action(key_value, modifier=None):
    # Execute a single key action with optional modifiers
    # modifier can be a single key or a list of keys
    # join value with modifier if provided in keys
    keys = []
    if modifier:
        keys.extend(get_key_from_string(mod) for mod in modifier)
    keys.append(get_key_from_string(key_value))
    
    print(f"Executing key action: {keys}")
    
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

def execute_function_action(function_name):
    """Execute special functions like volume control, brightness, etc."""
    
    if function_name == "layerUp":
        write_serial("leyerUp")
        print("Layer up command sent")
        return True
    
    elif function_name == "volumeUp":
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
        
    elif function_name == "brightnessUp":
        # Windows brightness control (may require additional setup)
        try:
            subprocess.run(['powershell', '-Command', 
                          '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,100)'], 
                          capture_output=True)
        except:
            print("Brightness control not available")
        return True
        
    elif function_name == "brightnessDown":
        # Windows brightness control (may require additional setup)
        try:
            subprocess.run(['powershell', '-Command', 
                          '(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,50)'], 
                          capture_output=True)
        except:
            print("Brightness control not available")
        return True
        
    elif function_name == "toggleFullscreen":
        # F11 key typically toggles fullscreen
        keyboard.press(Key.f11)
        keyboard.release(Key.f11)
        return True
        
    else:
        print(f"Unknown function: {function_name}")
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
    action_modifier = button_config.get("modifier", None)
    
    # Execute the appropriate action
    if action_type == "key":
        execute_key_action(action_value ,action_modifier)
        
    elif action_type == "macro":
        execute_macro_action(action_value)
        
    elif action_type == "function":
        execute_function_action(action_value)
        
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
