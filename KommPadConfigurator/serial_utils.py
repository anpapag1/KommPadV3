"""
Serial Utilities Module for KommPad Configurator
Centralized serial communication functions
"""

# Global variable to store the serial connection
_serial_connection = None

def set_serial_connection(connection):
    """Set the global serial connection"""
    global _serial_connection
    _serial_connection = connection

def get_serial_connection():
    """Get the current serial connection"""
    return _serial_connection

def write_serial(command):
    """
    Write a command to the serial connection
    
    Args:
        command (str): Command to send to the device
        
    Returns:
        bool: True if command was sent successfully, False otherwise
    """
    if _serial_connection and _serial_connection.is_open:
        try:
            # Ensure command ends with newline
            if not command.endswith('\n'):
                command += '\n'
            _serial_connection.write(command.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending serial command '{command.strip()}': {e}")
            return False
    else:
        print(f"No serial connection available to send command: {command.strip()}")
        return False
