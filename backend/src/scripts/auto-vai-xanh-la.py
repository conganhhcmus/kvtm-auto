"""
Example script for KVTM Auto
Demonstrates simple script usage with new logging format
"""

import sys
import json
import argparse
from ._core import Core, KeyCode
from ..models.device import Device
from ..models.script import GameOptions

SCRIPT_META = {
    "id": "auto-vai-xanh-la",
    "name": "Auto Vải Xanh Lá",
    "order": 1,
    "recommend": True,
    "description": "Sản xuất vải xanh lá"
}


def main(device: Device, game_options: GameOptions):
    """
    Main script function for both CLI and direct execution

    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration

    Returns:
        Dict with execution results
    """

    # Create core helper with device.id
    core = Core(device.id)
    
    core.log("Script started")
    
    # Simulate some work with context-aware sleep
    core.log("Waiting", "1.0s")
    core.sleep(1.0)
    
    core.log("Script completed")
    
    return {
        "success": True,
        "message": f"{SCRIPT_META['name']} completed successfully"
    }


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Open Game Script")
    parser.add_argument("--device-id", required=True, help="Device ID")
    parser.add_argument("--options", required=True, help="Game options JSON")
    parser.add_argument("--loop-index", type=int, default=0, help="Loop index")
    
    args = parser.parse_args()
    
    try:
        # Parse game options
        options_data = json.loads(args.options)
        game_options = GameOptions(**options_data)
        
        # Create device object
        device = Device(id=args.device_id, name=f"Device {args.device_id}")
        
        # Execute script
        result = main(device, game_options)
        
        # Exit with appropriate code
        if result.get("success", False):
            sys.exit(0)
        else:
            print(f"Script failed: {result.get('message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)