import json

import pytest

from palworld_pal_editor.config import Config
from palworld_pal_editor.webui import app


def test_network_defaults_and_remote_opt_in(monkeypatch):
    monkeypatch.delenv("PAL_EDITOR_ALLOW_REMOTE", raising=False)
    monkeypatch.setattr(Config, "mode", "web")
    assert Config.get_bind_host() == "127.0.0.1"
    monkeypatch.setenv("PAL_EDITOR_ALLOW_REMOTE", "1")
    monkeypatch.setattr(Config, "password", "short")
    with pytest.raises(ValueError):
        Config.get_bind_host()
    monkeypatch.setattr(Config, "password", "a-long-test-password")
    assert Config.get_bind_host() == "0.0.0.0"


def test_saved_secret_cannot_restore_known_signing_key(tmp_path):
    key = Config.JWT_SECRET_KEY
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"JWT_SECRET_KEY": "X2Nvbm5sb3N0"}))
    Config.load_from_file(path)
    assert Config.JWT_SECRET_KEY == key
    assert "JWT_SECRET_KEY" not in Config.to_dict()


def test_config_log_redacts_password(monkeypatch):
    monkeypatch.setattr(Config, "password", "do-not-log-this-value")
    assert Config.password not in Config.__str__()
    assert "password" not in Config.to_dict()


def test_cross_site_login_and_rebinding_are_refused(monkeypatch):
    monkeypatch.delenv("PAL_EDITOR_ALLOW_REMOTE", raising=False)
    monkeypatch.setattr(Config, "password", None)
    client = app.test_client()
    assert client.post("/api/auth/login", json={"password": ""},
                       headers={"Origin": "https://attacker.example"}).status_code == 403
    assert client.get("/api/ready", base_url="http://attacker.example").status_code == 403


def test_tokens_signed_with_old_public_key_are_rejected(monkeypatch):
    from flask_jwt_extended import decode_token
    from jwt.exceptions import InvalidSignatureError
    import jwt
    with app.app_context():
        forged = jwt.encode({"sub": "webui"}, "X2Nvbm5sb3N0", algorithm="HS256")
        with pytest.raises(InvalidSignatureError):
            decode_token(forged)
