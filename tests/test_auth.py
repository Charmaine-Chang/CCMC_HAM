"""Authentication and role-based access control tests."""
import uuid


def test_login_success_redirects_to_dashboard(client):
    resp = client.post('/auth/login', data={'username': 'admin', 'password': 'Password123!'})
    assert resp.status_code == 302
    assert '/dashboard/' in resp.headers['Location']


def test_login_wrong_password_redisplays_form(client):
    resp = client.post(
        '/auth/login',
        data={'username': 'admin', 'password': 'wrong-password'},
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_login_unknown_user_redisplays_form(client):
    resp = client.post(
        '/auth/login',
        data={'username': 'nobody', 'password': 'Password123!'},
        follow_redirects=True,
    )
    assert resp.status_code == 200


def test_logout_redirects_home(client, login):
    login('admin')
    resp = client.get('/auth/logout')
    assert resp.status_code == 302
    assert resp.headers['Location'] == '/'


def test_admin_can_access_admin_pages(client, login):
    login('admin')
    assert client.get('/manage/members').status_code == 200
    assert client.get('/manage/settings').status_code == 200


def test_member_cannot_access_admin_pages(client, login):
    login('member_wang')
    resp = client.get('/manage/members', follow_redirects=True)
    assert resp.status_code == 200
    assert '/manage/members' not in resp.request.path
    assert '/dashboard/' in resp.request.path


def test_member_cannot_create_event(client, login):
    login('member_wang')
    resp = client.post(
        '/events/new',
        data={
            'title': 'Should Fail',
            'start_time': '2099-01-01T10:00',
            'end_time': '2099-01-01T12:00',
            'category': 'special',
            'group_id': '',
            'location': 'X',
            'description': 'x',
            'is_published': '1',
        },
        follow_redirects=True,
    )
    assert '/dashboard/' in resp.request.path


def test_register_new_member_and_login(client):
    username = f'newuser_{uuid.uuid4().hex[:8]}'
    resp = client.post(
        '/auth/register',
        data={
            'username': username,
            'first_name': 'Test',
            'last_name': 'User',
            'email': f'{username}@example.com',
            'phone': '021 555 0123',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
        },
    )
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']

    resp = client.post(
        '/auth/login',
        data={'username': username, 'password': 'Password123!'},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert '/dashboard/' in resp.request.path