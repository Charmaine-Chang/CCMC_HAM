"""CCMC Hamilton 教会管理系统 - 冒烟测试
用法: python scripts/smoke_test.py
需要先运行 sql/ccmc_create_database.sql 与 sql/ccmc_populate_database.sql。
"""
import traceback
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.stdout.reconfigure(encoding='utf-8')

from CCMC_HAM import create_app

app = create_app({'TESTING': True})
client = app.test_client()

FAILURES = []


def check(label, response, expect_redirect_to=None):
    final_path = response.request.path
    ok = response.status_code == 200
    if expect_redirect_to and expect_redirect_to not in final_path:
        ok = False
    status = 'OK ' if ok else 'FAIL'
    print(f'[{status}] {label}: {response.status_code} -> {final_path} (len={len(response.data)})')
    if not ok:
        FAILURES.append(f'{label}: {response.status_code} -> {final_path}')
    return response


def get(label, path, expect=None):
    try:
        check(label, client.get(path, follow_redirects=True), expect)
    except Exception:
        FAILURES.append(f'{label}: 异常 {traceback.format_exc()}')


def post(label, path, data, expect=None):
    try:
        check(label, client.post(path, data=data, follow_redirects=True), expect)
    except Exception:
        FAILURES.append(f'{label}: 异常 {traceback.format_exc()}')


def login(username, password='Password123!'):
    check(f'login {username}', client.post('/auth/login', data={'username': username, 'password': password}, follow_redirects=True))


print('===== 公开页面 =====')
for p, label in [('/', 'home'), ('/welcome', 'welcome'), ('/qr', 'qr'),
                 ('/about', 'about'), ('/contact', 'contact'), ('/public-events', 'public-events')]:
    get(label, p)
get('login-page', '/auth/login')
get('register-page', '/auth/register')
post('visitor submit', '/welcome/submit', {
    'first_name': '冒烟', 'last_name': '测试', 'email': 'smoke@example.com',
    'phone': '021 000 9999', 'fellowship_interest': '青年团契', 'heard_from': '网站', 'notes': '自动测试'
})

print('===== 管理员 =====')
login('admin')
for p, label in [('/dashboard', 'dashboard'), ('/events', 'events'), ('/announcements', 'announcements'),
                 ('/prayer', 'prayer'), ('/fellowships', 'fellowships'), ('/resources', 'resources'),
                 ('/visitors', 'visitors'), ('/attendance/', 'attendance'), ('/attendance/report', 'attendance-report'),
                 ('/rosters', 'rosters'), ('/rosters/mine', 'roster-mine'), ('/reports', 'reports'),
                 ('/manage/members', 'members'), ('/manage/settings', 'settings')]:
    get(label, p)
post('create event', '/events/new', {
    'title': '冒烟测试活动', 'start_time': '2099-01-01T10:00', 'end_time': '2099-01-01T12:00',
    'category': 'special', 'group_id': '', 'location': '测试地点', 'description': '测试', 'is_published': '1'
})
post('create announcement', '/announcements/new', {
    'title': '冒烟测试通知', 'content': '测试内容', 'is_published': '1'
})
post('create prayer', '/prayer/new', {
    'title': '冒烟测试代祷', 'content': '测试内容', 'is_public': '1'
})
post('record attendance', '/attendance/submit', {
    'service_date': '2099-01-01', 'event_id': '', 'attendee_names': '张三\n李四, 王五'
})
post('create roster', '/rosters/new', {
    'task_name': '招待', 'service_date': '2099-01-02', 'user_id': '3', 'notes': '测试'
})
post('create fellowship', '/fellowships/new', {
    'group_name': '冒烟测试团契', 'group_type': 'fellowship', 'description': '测试', 'visibility': 'private'
})
post('create resource', '/resources/new', {
    'category': '资料', 'title': '冒烟测试资料', 'content': '测试', 'is_published': '1'
})

print('===== 执事 =====')
client.get('/auth/logout')
login('coord_chen')
get('coord events', '/events')
get('coord visitors', '/visitors')
get('coord members-denied', '/manage/members', expect='/dashboard')
get('coord settings-denied', '/manage/settings', expect='/dashboard')

print('===== 服事人员 =====')
client.get('/auth/logout')
login('op_lin')
get('op attendance', '/attendance/')
get('op roster-mine', '/rosters/mine')
get('op visitors-denied', '/visitors', expect='/dashboard')
get('op rosters-manage-denied', '/rosters', expect='/dashboard')

print('===== 会友 =====')
client.get('/auth/logout')
login('member_wang')
get('member dashboard', '/dashboard')
get('member events', '/events')
get('member prayer', '/prayer')
get('member attendance-denied', '/attendance/', expect='/dashboard')
get('member visitors-denied', '/visitors', expect='/dashboard')
post('member join fellowship', '/fellowships/3/join', {})

print()
if FAILURES:
    print(f'失败 {len(FAILURES)} 项:')
    for f in FAILURES:
        print(' -', f)
    raise SystemExit(1)
print('全部通过 ✅')
