"""Visitor registration flow tests."""
import uuid


def test_visitor_submission_creates_record(client):
    email = f'visitor_{uuid.uuid4().hex[:8]}@example.com'
    resp = client.post(
        '/welcome/submit',
        data={
            'first_name': 'Test',
            'last_name': 'Visitor',
            'email': email,
            'phone': '021 555 0123',
            'fellowship_interest': '青年团契',
            'heard_from': '网站',
            'notes': 'created by pytest',
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert resp.request.path == '/welcome/thanks'


def test_visitor_requires_first_name(client):
    resp = client.post(
        '/welcome/submit',
        data={'first_name': '', 'last_name': '', 'email': 'x@example.com'},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert resp.request.path == '/welcome'


def test_visitor_rejects_invalid_email(client):
    resp = client.post(
        '/welcome/submit',
        data={'first_name': 'Bad', 'last_name': 'Email', 'email': 'not-an-email'},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert resp.request.path == '/welcome'


def test_admin_can_see_registered_visitor(client, login):
    email = f'admin_visitor_{uuid.uuid4().hex[:8]}@example.com'
    client.post(
        '/welcome/submit',
        data={
            'first_name': 'Admin',
            'last_name': 'Sees',
            'email': email,
            'phone': '021 555 0123',
        },
    )
    login('admin')
    resp = client.get('/visitors/')
    assert resp.status_code == 200
    assert email.encode() in resp.data