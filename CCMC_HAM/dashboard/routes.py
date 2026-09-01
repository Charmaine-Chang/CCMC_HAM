import logging
from datetime import date
from flask import Blueprint, render_template, session
from CCMC_HAM.db import get_cursor
from CCMC_HAM.shared.decorators import login_required
from CCMC_HAM.constants import ROLE_ADMIN, ROLE_COORDINATOR, ROLE_OPERATOR

dashboard_bp = Blueprint('dashboard', __name__)


def _run(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


@dashboard_bp.route('/')
@login_required
def index():
    role_id = session_role()
    try:
        cur = get_cursor()
        user_id = session['user_id']

        upcoming = _run(cur, """
            SELECT e.*, g.group_name, g.group_name_en FROM events e
            LEFT JOIN `groups` g ON e.group_id = g.group_id
            WHERE e.is_published = 1 AND e.start_time >= NOW()
            ORDER BY e.start_time ASC LIMIT 6
        """)
        announcements = _run(cur, """
            SELECT a.*, g.group_name, g.group_name_en FROM announcements a
            LEFT JOIN `groups` g ON a.group_id = g.group_id
            WHERE a.is_published = 1 ORDER BY a.created_at DESC LIMIT 5
        """)
        prayers = _run(cur, """
            SELECT p.*, u.username FROM prayer_requests p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.status != 'answered'
            ORDER BY p.created_at DESC LIMIT 6
        """)
        my_rosters = _run(cur, """
            SELECT r.*, e.title AS event_title, g.group_name
            FROM rosters r
            LEFT JOIN events e ON r.event_id = e.event_id
            LEFT JOIN `groups` g ON r.group_id = g.group_id
            WHERE r.user_id = %s AND r.service_date >= CURDATE()
            ORDER BY r.service_date ASC LIMIT 6
        """, (user_id,))

        stats = {}
        if role_id in (ROLE_ADMIN, ROLE_COORDINATOR):
            stats['visitors_new'] = _run(cur, "SELECT COUNT(*) AS c FROM visitors WHERE status='new'")[0]['c']
            stats['members'] = _run(cur, "SELECT COUNT(*) AS c FROM users WHERE status='Active'")[0]['c']
            stats['attendance_week'] = _run(cur, """
                SELECT COUNT(*) AS c FROM attendance
                WHERE service_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            """)[0]['c']
        if role_id in (ROLE_ADMIN, ROLE_COORDINATOR, ROLE_OPERATOR):
            stats['events_upcoming'] = len(upcoming)
            stats['pending_rosters'] = _run(cur, """
                SELECT COUNT(*) AS c FROM rosters
                WHERE service_date >= CURDATE() AND status = 'pending'
            """)[0]['c']
        cur.close()
    except Exception as e:
        logging.exception(f"看板加载失败: {e}")
        upcoming, announcements, prayers, my_rosters, stats = [], [], [], [], {}

    today = date.today().strftime('%Y-%m-%d')
    return render_template(
        'dashboard/dashboard.html',
        role_id=role_id,
        upcoming=upcoming,
        announcements=announcements,
        prayers=prayers,
        my_rosters=my_rosters,
        stats=stats,
        today=today,
        active_page='dashboard',
    )


def session_role():
    from flask import session
    return session.get('role_id', 4)
