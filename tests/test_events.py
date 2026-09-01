"""Event CRUD tests (staff-only routes)."""
import uuid


def test_admin_can_create_event(client, login):
    login('admin')
    title = f'Pytest Event {uuid.uuid4().hex[:6]}'
    resp = client.post(
        '/events/new',
        data={
            'title': title,
            'start_time': '2099-01-01T10:00',
            'end_time': '2099-01-01T12:00',
            'category': 'special',
            'group_id': '',
            'location': 'Test Location',
            'description': 'Created by pytest',
            'is_published': '1',
        },
    )
    assert resp.status_code == 302
    assert '/events/' in resp.headers['Location']

    # The new event should be visible on the calendar list page.
    resp = client.get('/events/')
    assert resp.status_code == 200
    assert title.encode() in resp.data