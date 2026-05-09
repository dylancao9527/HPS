from flask import Flask

from routes import weekly_report


def _app():
    return Flask(__name__)


def test_get_weekly_report_returns_current_user_summary(monkeypatch, fake_user):
    app = _app()
    calls = []

    class FakeWeeklyReportService:
        def build_summary(self, user_id):
            calls.append(user_id)
            return {
                "current_period": "2026-04-19 ~ 2026-04-25",
                "previous_period": "2026-04-12 ~ 2026-04-18",
                "overall_trend_text": "与前7天相比，风险较前7天下降。",
            }

    monkeypatch.setattr(
        weekly_report,
        "build_weekly_report_service",
        lambda: FakeWeeklyReportService(),
    )

    with app.test_request_context("/api/weekly-report"):
        response = weekly_report.get_weekly_report.__wrapped__(fake_user)

    assert response.get_json() == {
        "current_period": "2026-04-19 ~ 2026-04-25",
        "previous_period": "2026-04-12 ~ 2026-04-18",
        "overall_trend_text": "与前7天相比，风险较前7天下降。",
    }
    assert calls == [42]
