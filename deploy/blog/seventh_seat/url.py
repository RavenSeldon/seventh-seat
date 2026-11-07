"""URL registration for the static Seventh Seat release only."""
from flask import Blueprint

from .views import publication

seventh_seat_bp = Blueprint("seventh_seat", __name__, url_prefix="/seventh-seat")

# Endpoint names carry the "seventhseat_" prefix for the reason documented in
# first_notice/url.py: create_app() aliases the bare part of every
# "<blueprint>.<name>" endpoint when that short name is free, so a plain
# "index" would capture url_for('index') from the blog's own templates.
seventh_seat_bp.add_url_rule(
    "", endpoint="seventhseat_without_slash", view_func=publication,
    defaults={"asset_path": ""},
)
seventh_seat_bp.add_url_rule(
    "/", endpoint="seventhseat_index", view_func=publication,
    defaults={"asset_path": ""},
)
seventh_seat_bp.add_url_rule(
    "/<path:asset_path>", endpoint="seventhseat_file", view_func=publication,
)
