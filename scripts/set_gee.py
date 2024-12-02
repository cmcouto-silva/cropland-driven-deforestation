#!/usr/bin/env python3
import os
import sys
import json

def setup_gee_authentication():
    """Set up Google Earth Engine authentication"""
    import ee
    
    # Determine credentials path based on OS
    if sys.platform.startswith('win'):
        credentials_dir = os.path.join(os.path.expanduser('~'), '.config', 'earthengine')
    else:  # Linux/Mac
        credentials_dir = os.path.join(os.path.expanduser('~'), '.config', 'earthengine')
    
    credentials_path = os.path.join(credentials_dir, 'credentials')
    
    # Check if already authenticated
    if os.path.exists(credentials_path):
        try:
            with open(credentials_path) as f:
                credentials = json.load(f)
            ee.Initialize(credentials)
            print("Existing Earth Engine credentials found and verified.")
            return True
        except Exception:
            print("Existing credentials invalid. Proceeding with new authentication.")
    
    # Create credentials directory if it doesn't exist
    os.makedirs(credentials_dir, exist_ok=True)
    
    # Perform authentication
    print("Please follow the instructions in your browser to authenticate Earth Engine...")
    try:
        ee.Authenticate()
        ee.Initialize()
        print("\nAuthentication successful!")
        print(f"Credentials stored at: {credentials_path}")
        print("\nYou can now run your Earth Engine scripts without further authentication.")
        return True
    except Exception as e:
        print(f"Authentication failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("Setting up Google Earth Engine authentication...")
    if setup_gee_authentication():
        print("\nSetup completed successfully!")
    else:
        print("\nSetup failed. Please try again or contact support.")
