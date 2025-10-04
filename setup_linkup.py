#!/usr/bin/env python3
"""
Setup script for LinkUp integration
"""

import os
import subprocess
import sys

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "linkup-sdk"])
        print("✓ LinkUp SDK installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing LinkUp SDK: {e}")
        return False
    return True

def check_api_key():
    """Check if LinkUp API key is set"""
    api_key = os.getenv("LINKUP_API_KEY")
    if not api_key:
        print("⚠️  LINKUP_API_KEY environment variable not set")
        print("Please set your LinkUp API key:")
        print("export LINKUP_API_KEY='your_api_key_here'")
        print("\nTo get your API key:")
        print("1. Visit: https://docs.linkup.so/pages/documentation/get-started/quickstart")
        print("2. Create a free account")
        print("3. Get your API key")
        return False
    else:
        print("✓ LinkUp API key is set")
        return True

def test_imports():
    """Test if all imports work"""
    print("Testing imports...")
    try:
        from linkup import LinkupClient
        print("✓ LinkUp import successful")
        return True
    except ImportError as e:
        print(f"✗ LinkUp import failed: {e}")
        return False

def main():
    """Main setup function"""
    print("MoveScout LinkUp Setup")
    print("=" * 30)
    
    # Install dependencies
    if not install_dependencies():
        print("Setup failed: Could not install dependencies")
        return False
    
    # Test imports
    if not test_imports():
        print("Setup failed: Import errors")
        return False
    
    # Check API key
    api_key_set = check_api_key()
    
    print("\n" + "=" * 30)
    if api_key_set:
        print("✓ Setup complete! You can now run:")
        print("  python linkup_main.py     # CLI interface")
        print("  python linkup_api.py      # API server")
        print("  python test_linkup.py     # Test the integration")
    else:
        print("⚠️  Setup mostly complete, but you need to set your LinkUp API key")
        print("After setting the API key, you can run:")
        print("  python linkup_main.py     # CLI interface")
        print("  python linkup_api.py      # API server")
        print("  python test_linkup.py     # Test the integration")
    
    return True

if __name__ == "__main__":
    main()

