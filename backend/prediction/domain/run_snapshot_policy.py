def build_prediction_run_snapshot(current_user, profile, latest_bp):
    return {
        "bp_record_count": current_user.bp_records.count(),
        "latest_bp_record_id": latest_bp.id if latest_bp else None,
        "latest_bp_recorded_at": latest_bp.recorded_at.isoformat()
        if latest_bp and latest_bp.recorded_at
        else None,
        "profile_updated_at": profile.updated_at.isoformat()
        if profile and profile.updated_at
        else None,
    }
