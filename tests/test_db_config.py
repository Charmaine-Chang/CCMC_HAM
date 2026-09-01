"""Unit tests for database configuration resolution."""
from CCMC_HAM.db import get_db_config


def test_db_config_reads_env_overrides(monkeypatch):
    monkeypatch.setenv('DB_USER', 'ci_user')
    monkeypatch.setenv('DB_PASSWORD', 'secret')
    monkeypatch.setenv('DB_HOST', 'db.example.com')
    monkeypatch.setenv('DB_PORT', '3307')
    monkeypatch.setenv('DB_NAME', 'ci_db')

    cfg = get_db_config()

    assert cfg['user'] == 'ci_user'
    assert cfg['password'] == 'secret'
    assert cfg['host'] == 'db.example.com'
    assert cfg['port'] == 3307
    assert cfg['db'] == 'ci_db'