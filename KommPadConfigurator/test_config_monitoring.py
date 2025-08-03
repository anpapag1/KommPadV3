#!/usr/bin/env python3
"""
Test script to verify config file monitoring
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import get_config_path, CONFIG_PATH
import json
import time

def test_config_monitoring():
    """Test the config monitoring functionality"""
    print("Testing config monitoring...")
    
    print(f"Config path: {get_config_path()}")
    print(f"CONFIG_PATH: {CONFIG_PATH}")
    
    # Check if config file exists
    if os.path.exists(CONFIG_PATH):
        print("Config file exists")
        
        # Get current modification time
        mod_time = os.path.getmtime(CONFIG_PATH)
        print(f"Current modification time: {mod_time}")
        
        # Try to read the config
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
            print("Config loaded successfully")
            print(f"Device max_layers: {config.get('device', {}).get('max_layers', 'Not found')}")
        except Exception as e:
            print(f"Error reading config: {e}")
    else:
        print("Config file not found!")
    
    print("Test completed!")

if __name__ == "__main__":
    test_config_monitoring()
