from extensions import db
from models import AdminUser, BPRecord, PredictionRecord, User
from services.account_contract import validate_password_strength
from services.export_service import get_training_export_stats
from utils.time_utils import utc_now_naive


class AdminUserService:
    def list_users(self, page, per_page):
        pagination = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        admins = AdminUser.query.order_by(AdminUser.created_at.desc()).all()

        return {
            "users": [user.to_dict() for user in pagination.items],
            "admins": [admin.to_dict() for admin in admins],
            "total": pagination.total,
            "admin_total": len(admins),
            "page": page,
            "pages": pagination.pages,
        }

    def update_account_password(self, account_id, data):
        account = self._get_account(account_id)
        if not account:
            return {"error": "用户不存在"}, 404

        new_username = data.get("username", "").strip()
        new_email = data.get("email", "").strip()
        new_password = data.get("password", "").strip()

        if (new_username and new_username != account.username) or (
            new_email and new_email != account.email
        ):
            return {"error": "管理员仅可修改密码，不能修改用户名或邮箱"}, 400

        if new_password:
            password_error = validate_password_strength(new_password)
            if password_error:
                return {"error": password_error}, 400
            account.set_password(new_password)
        else:
            return {"error": "请输入新密码"}, 400

        db.session.commit()
        return {"message": "用户密码已更新", "user": account.to_dict()}

    def delete_user(self, current_user, account_id):
        if self._is_admin_account_id(account_id):
            return {"error": "管理员账号不能在用户管理中删除"}, 400

        user_id = self._parse_integer_id(account_id)
        if user_id is None:
            return {"error": "用户不存在"}, 404

        user = db.session.get(User, user_id)
        if not user:
            return {"error": "用户不存在"}, 404

        db.session.delete(user)
        db.session.commit()
        return {"message": f"用户 {user.username} 已删除"}

    def batch_delete_users(self, current_user, ids):
        if not ids:
            return {"error": "请选择要删除的用户"}, 400

        if any(self._is_admin_account_id(user_id) for user_id in ids):
            return {"error": "管理员账号不能批量删除"}, 400

        ids = [
            parsed_id
            for user_id in ids
            if (parsed_id := self._parse_integer_id(user_id)) is not None
        ]
        users = User.query.filter(User.id.in_(ids)).all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        return {"message": f"已删除 {len(users)} 个用户"}

    def _get_account(self, account_id):
        if self._is_admin_account_id(account_id):
            admin_id = self._parse_integer_id(str(account_id).split(":", 1)[1])
            if admin_id is None:
                return None
            return db.session.get(AdminUser, admin_id)

        user_id = self._parse_integer_id(account_id)
        if user_id is None:
            return None
        return db.session.get(User, user_id)

    def _is_admin_account_id(self, account_id):
        return str(account_id).startswith("admin:")

    def _parse_integer_id(self, account_id):
        try:
            return int(account_id)
        except (TypeError, ValueError):
            return None


class AdminStatsService:
    def __init__(
        self,
        *,
        governance_service,
        now_provider=utc_now_naive,
        training_export_stats_provider=get_training_export_stats,
    ):
        self.governance_service = governance_service
        self.now_provider = now_provider
        self.training_export_stats_provider = training_export_stats_provider

    def get_stats(self):
        today_start = self.now_provider().replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        return {
            "total_users": User.query.count(),
            "total_bp_records": BPRecord.query.count(),
            "total_predictions": PredictionRecord.query.count(),
            "today_users": User.query.filter(User.created_at >= today_start).count(),
            "today_predictions": PredictionRecord.query.filter(
                PredictionRecord.created_at >= today_start
            ).count(),
            "training_export": self.training_export_stats_provider(),
            "governance": self.governance_service.get_summary(),
        }
