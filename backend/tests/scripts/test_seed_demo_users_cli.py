from types import SimpleNamespace

import pytest

from scripts import seed_demo_users


class FakeApp:
    def app_context(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeBPRecords:
    def __init__(self, count):
        self._count = count

    def count(self):
        return self._count


class FakeQuery:
    def __init__(self, users):
        self.users = users
        self.filter_arg = None

    def filter(self, query_filter):
        self.filter_arg = query_filter
        return self

    def all(self):
        return self.users


class FakeSession:
    def __init__(self):
        self.commits = 0
        self.deletes = []
        self.flushes = 0

    def commit(self):
        self.commits += 1

    def delete(self, user):
        self.deletes.append(user)

    def flush(self):
        self.flushes += 1


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


def test_main_prints_fixed_password_for_seeded_user(monkeypatch, capsys):
    monkeypatch.setattr(seed_demo_users, "create_app", lambda config: FakeApp())
    monkeypatch.setattr(
        seed_demo_users,
        "seed_demo_users",
        lambda *, reset_existing, password: {
            "deleted_existing": 0,
            "created_count": 1,
            "users": [
                {
                    "username": "shit",
                    "label": "固定登录样例",
                    "bp_record_days": 14,
                    "diagnosis": "不确定",
                    "note": "使用固定密码 A1111111，适合快速登录验证基础流程",
                    "password": "A1111111",
                }
            ],
        },
    )

    seed_demo_users.main(["--apply", "--password", "SharedPass123"])

    assert "固定密码: A1111111" in capsys.readouterr().out


def test_reset_requires_explicit_confirmation():
    with pytest.raises(SystemExit) as exc_info:
        seed_demo_users.parse_args(["--reset-existing"])

    assert "--yes-i-understand" in str(exc_info.value)


def test_demo_users_include_fixed_shit_login():
    spec = next(
        item for item in seed_demo_users.DEMO_USERS if item["username"] == "shit"
    )

    assert spec["password"] == "A1111111"
    assert spec["email"] == "shit@example.com"


def test_seed_demo_users_creates_missing_defined_users(monkeypatch):
    existing_user = SimpleNamespace(
        username="demo_showcase_low",
        profile=SimpleNamespace(nickname="低风险样例", diagnosis="No"),
        bp_records=FakeBPRecords(21),
    )
    query = FakeQuery([existing_user])
    session = FakeSession()
    created_specs = []
    specs = [
        {"username": "demo_showcase_low"},
        {"username": "shit", "password": "A1111111"},
    ]

    monkeypatch.setattr(seed_demo_users, "DEMO_USERS", specs)
    monkeypatch.setattr(seed_demo_users, "User", SimpleNamespace(query=query))
    monkeypatch.setattr(seed_demo_users, "db", SimpleNamespace(session=session))
    monkeypatch.setattr(seed_demo_users, "_demo_user_filter", lambda: "demo-filter")
    monkeypatch.setattr(seed_demo_users, "utc_now_naive", lambda: "now")
    monkeypatch.setattr(
        seed_demo_users,
        "_create_demo_user",
        lambda spec, now, password: created_specs.append(
            (spec["username"], now, password)
        )
        or {
            "username": spec["username"],
            "label": spec["username"],
            "bp_record_days": 0,
            "diagnosis": "不确定",
            "note": "新增的展示用户",
            **({"password": spec["password"]} if "password" in spec else {}),
        },
    )

    result = seed_demo_users.seed_demo_users(
        reset_existing=False,
        password="generatedA1!",
    )

    assert query.filter_arg == "demo-filter"
    assert created_specs == [("shit", "now", "generatedA1!")]
    assert result["created_count"] == 1
    assert [item["username"] for item in result["users"]] == [
        "demo_showcase_low",
        "shit",
    ]
    assert result["users"][1]["password"] == "A1111111"
    assert session.commits == 1
