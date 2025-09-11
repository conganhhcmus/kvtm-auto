"""
Example script for KVTM Auto
Demonstrates simple script usage with new logging format
"""

import time

from ..libs.adb import adb
from ._core import KeyCode
from ._core import write_log, log_script_started, log_waiting, check_should_stop

SCRIPT_META = {
    "id": "example_script",
    "name": "Example Script",
    "order": 1,
    "recommend": True,
    "description": "Example script demonstrating simple core module usage"
}


def main(device, game_options, context):
    """
    Main script function for both CLI and direct execution
    
    Args:
        device: Device model containing device information
        game_options: GameOptions model containing game configuration
        context: ScriptContext object for logging and control (None for CLI)
    
    Returns:
        Dict with execution results
    """
    
    log_script_started(device.id, "Example Script")
    
    # Check if we should stop (for direct execution)
    if check_should_stop(context):
        return {"success": False, "message": "Script stopped by user"}
    
    write_log(device.id, "Running Script ....")
    
    # Simulate some work with context-aware sleep
    log_waiting(device.id, 1.0, context)
    
    # Check stop signal again
    if check_should_stop(context):
        return {"success": False, "message": "Script stopped by user"}
    
    write_log(device.id, "Script completed")
    
    return {
        "success": True,
        "message": "Example script completed successfully"
    }


if __name__ == "__main__":
    import sys
    import json
    import argparse
    from ..models.device import Device
    from ..models.script import GameOptions
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Example Script")
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
        result = main(device, game_options, None)
        
        # Exit with appropriate code
        if result.get("success", False):
            sys.exit(0)
        else:
            print(f"Script failed: {result.get('message', 'Unknown error')}", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Script execution failed: {e}", file=sys.stderr)
        sys.exit(1)