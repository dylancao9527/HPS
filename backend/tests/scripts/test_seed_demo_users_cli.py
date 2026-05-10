import pytest

from scripts import seed_demo_users


class FakeApp:
    def app_context(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


def _fake_seed_result():
    return {
        "deleted_existing": 0,
        "created_count": 0,
        "users": [],
    }


def test_main_previews_without_writing_by_default(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        seed_demo_users,
        "create_app",
        lambda config: pytest.fail("preview mode must not create the Flask app"),
    )
    monkeypatch.setattr(
        seed_demo_users,
        "seed_demo_users",
        lambda **kwargs: pytest.fail("preview mode must not write demo users"),
    )

    seed_demo_users.main([])

    assert calls == []
    assert "预览模式" in capsys.readouterr().out


def test_main_seeds_without_reset_when_apply_is_explicit(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(seed_demo_users, "create_app", lambda config: FakeApp())
    monkeypatch.setattr(
        seed_demo_users,
        "seed_demo_users",
        lambda *, reset_existing, password: calls.append(
            {"reset_existing": reset_existing, "password": password}
        )
        or _fake_seed_result(),
    )
    monkeypatch.setattr(seed_demo_users.secrets, "token_urlsafe", lambda length: "generated")

    seed_demo_users.main(["--apply"])

    assert calls == [{"reset_existing": False, "password": "generatedA1!"}]
    assert "Demo@123456" not in capsys.readouterr().out


def test_reset_requires_explicit_confirmation():
    with pytest.raises(SystemExit) as exc_info:
        seed_demo_users.parse_args(["--reset-existing"])

    assert "--yes-i-understand" in str(exc_info.value)
