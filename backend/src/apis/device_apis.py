from flask import Blueprint, jsonify

from libs.device_manager import DeviceManager

device_bp = Blueprint("device_bp", __name__)


@device_bp.route("/api/devices", methods=["GET"])
def list_devices():
    device_manager = DeviceManager()
    devices = device_manager.list_devices()
    return jsonify([device.to_dict() for device in devices])


@device_bp.route("/api/devices/<device_id>", methods=["GET"])
def get_device(device_id):
    device_manager = DeviceManager()
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    return jsonify(device.to_dict())


@device_bp.route("/api/devices/<device_id>/logs", methods=["GET"])
def get_device_logs(device_id):
    device_manager = DeviceManager()
    device = device_manager.get_device(device_id)
    if not device:
        return jsonify({"error": "Device not found"}), 404
    return jsonify(device.get_logs(100))  # Return array directly
