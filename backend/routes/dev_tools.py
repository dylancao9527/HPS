from flask import Blueprint, jsonify, request

from services.mock_email_service import get_latest_email


dev_tools_bp = Blueprint("dev_tools", __name__, url_prefix="/api/dev")


@dev_tools_bp.route("/mock-emails/latest", methods=["GET"])
def get_latest_mock_email():
    email = request.args.get("email", "").strip()
    scene = request.args.get("scene", "").strip() or None
    message = get_latest_email(recipient=email, scene=scene)
    return jsonify({"message": message})
