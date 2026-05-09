"""
==============================================================================
Flask 应用入口 (app.py)
==============================================================================
职责：
  1. 创建 Flask 应用实例，加载配置
  2. 初始化数据库扩展（Flask-SQLAlchemy + Flask-Migrate）
  3. 注册所有 Blueprint 路由
  4. 自动创建管理员账号（首次启动时）
  5. 单服务模式下 serve 前端静态文件

数据库迁移（在 backend/ 目录下执行）：
  uv run flask db migrate -m "描述"
  uv run flask db upgrade
  uv run flask db downgrade

启动方式：
  开发模式:  uv run flask --app app:create_app --debug run --host 0.0.0.0 --port 5000
             （+ 前端 pnpm dev 分开运行）
  单服务模式: cd frontend && pnpm build
             cd ../backend && uv run flask --app app:create_app run --host 0.0.0.0 --port 5000
==============================================================================
"""

import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from sqlalchemy import inspect
from config import Config
from extensions import db, migrate
from prediction.infrastructure.prophet_asset_maintenance import register_prophet_asset_commands

# 前端构建产物目录
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


def create_app(config_override=None):
    app = Flask(__name__, static_folder=None)  # 禁用默认 static，手动处理
    app.config.from_object(Config)
    if config_override:
        app.config.update(config_override)
    CORS(app)

    # ---- 初始化扩展 ----
    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    register_prophet_asset_commands(app)

    # ---- 注册 API 路由 ----
    from routes import (
        admin_bp,
        auth_bp,
        bp_records_bp,
        dev_tools_bp,
        health_tasks_bp,
        predictions_bp,
        profile_bp,
        weekly_report_bp,
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(bp_records_bp)
    app.register_blueprint(health_tasks_bp)
    app.register_blueprint(weekly_report_bp)
    app.register_blueprint(predictions_bp)
    app.register_blueprint(admin_bp)
    if app.config.get("ENABLE_LOCAL_MOCK_EMAIL_SERVICE", False):
        app.register_blueprint(dev_tools_bp)

    @app.route("/api/health", methods=["GET"])
    def health_check():
        from flask import jsonify

        return jsonify({"status": "ok"})

    # ---- 前端静态文件 serving（单服务模式） ----
    # pnpm build 会把产物放在 backend/static/ 目录下
    if os.path.isdir(STATIC_DIR):

        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_frontend(path):
            """
            SPA catch-all：
            - 静态资源（js/css/图片）直接返回文件
            - 其他路径返回 index.html（由 React Router 处理）
            """
            # 如果请求的是 API 路径，不应该走到这里（Blueprint 已注册）
            file_path = os.path.join(STATIC_DIR, path)
            if path and os.path.isfile(file_path):
                return send_from_directory(STATIC_DIR, path)
            # 所有非文件路径返回 index.html（SPA 路由）
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.isfile(index_path):
                return send_from_directory(STATIC_DIR, "index.html")
            return "Frontend not built. Run: cd frontend && pnpm build", 404

    with app.app_context():
        import models  # noqa: 确保所有模型注册到 SQLAlchemy metadata

        # 如果 migrations/ 目录不存在（首次部署），用 create_all 兜底建表
        migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
        if not os.path.exists(migrations_dir):
            db.create_all()
            print("[OK] Database tables created (no migrations dir, used create_all)")
        else:
            print(
                "[OK] Migrations dir exists, use 'flask db upgrade' to apply schema changes"
            )

        has_admin_users_table = inspect(db.engine).has_table("admin_users")
        if app.config.get("INIT_ADMIN_ON_STARTUP", True) and has_admin_users_table:
            _init_admin(app)

    return app


def _init_admin(app):
    """
    自动创建超级管理员。
    如果已存在则跳过。配置来自 config.py 中的 ADMIN_* 字段。
    """
    from models import AdminUser

    admin_username = app.config["ADMIN_USERNAME"]
    admin_password = app.config["ADMIN_PASSWORD"]
    admin_email = app.config["ADMIN_EMAIL"]

    try:
        existing = AdminUser.query.filter_by(username=admin_username).first()
        if not existing:
            admin = AdminUser()
            admin.username = admin_username
            admin.email = admin_email
            admin.set_password(admin_password)
            db.session.add(admin)
            db.session.commit()
            print(f"[OK] Admin account created: {admin_username}")
        else:
            print(f"[OK] Admin account exists: {admin_username}")
    except Exception as e:
        print(f"[WARN] Admin init skipped: {e}")
        db.session.rollback()


if __name__ == "__main__":
    app = create_app()
    print("=" * 50)
    print("  Hypertension Prediction API Server")
    print("  http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host="0.0.0.0", port=5000)
