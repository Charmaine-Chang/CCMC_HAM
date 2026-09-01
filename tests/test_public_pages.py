"""Public pages should be reachable without logging in."""
import pytest

PUBLIC_PATHS = [
    '/',
    '/welcome',
    '/about',
    '/contact',
    '/public-events',
    '/qr',
    '/auth/login',
    '/auth/register',
]


@pytest.mark.parametrize('path', PUBLIC_PATHS)
def test_public_pages_return_200(client, path):
    resp = client.get(path)
    assert resp.status_code == 200