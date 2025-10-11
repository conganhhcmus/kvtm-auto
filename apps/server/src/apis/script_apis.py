from flask import Blueprint, jsonify

from libs.script_manager import ScriptManager

script_bp = Blueprint("script_bp", __name__)


@script_bp.route("/api/scripts", methods=["GET"])
def list_scripts():
    script_manager = ScriptManager("scripts")
    scripts = [script.to_dict() for script in script_manager.list_scripts()]
    return jsonify({"scripts": scripts, "total": len(scripts)})


@script_bp.route("/api/scripts/<script_id>", methods=["GET"])
def get_script(script_id):
    script_manager = ScriptManager("scripts")
    script = script_manager.get_script(script_id)
    if not script:
        return jsonify({"error": "Script not found"}), 404
    return jsonify(script.to_dict())
