import logging
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import login_required, ministry_required, staff_required
from CCMC_HAM.shared.helpers import parse_date, split_names

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
attendance_bp = Blueprint('attendance', __name__)


@attendance_bp.route('/')
@ministry_required
def record():
    today = date.today().isoformat()
    selected_date = request.args.get('service_date', today)
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT event_id, title, start_time FROM events
            WHERE is_published = 1 AND category = 'worship' AND start_time >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
            ORDER BY start_time DESC
        """)
        worship_events = cur.fetchall()
        cur.execute("""
            SELECT a.attendance_id, a.service_date, a.attendee_name, a.event_id, e.title
            FROM attendance a
            LEFT JOIN events e ON a.event_id = e.event_id
            WHERE a.service_date = %s
            ORDER BY a.event_id IS NULL, a.attendee_name
        """, (selected_date,))
        records = cur.fetchall()
        cur.execute("SELECT COUNT(*) AS c FROM attendance WHERE service_date = %s", (selected_date,))
        total = cur.fetchone()['c']
        cur.close()
    except Exception as e:
        logging.exception(f"出席记录加载失败: {e}")
        worship_events, records, total = [], [], 0
    return render_template(
        'attendance/record.html',
        worship_events=worship_events,
        records=records,
        total=total,
        selected_date=selected_date,
        active_page='attendance',
    )


@attendance_bp.route('/submit', methods=['POST'])
@ministry_required
def submit():
    service_date = parse_date(request.form.get('service_date'), date.today())
    event_id = request.form.get('event_id') or None
    names = split_names(request.form.get('attendee_names'))
    if not names:
        flash(_msg("msg_attendance_name_required"), "danger")
        return redirect(url_for('attendance.record', service_date=service_date.date().isoformat()))
    try:
        cur = get_cursor()
        for name in names:
            cur.execute("""
                INSERT INTO attendance (event_id, service_date, attendee_name, recorded_by)
                VALUES (%s, %s, %s, %s)
            """, (event_id, service_date.date().isoformat(), name, session['user_id']))
        get_db().commit()
        cur.close()
        flash(_msg("msg_attendance_saved", count=len(names)), "success")
    except Exception as e:
        logging.exception(f"提交出席失败: {e}")
        try:
            get_db().rollback()
        except Exception:
            pass
        flash(_msg("msg_attendance_submit_error"), "danger")
    return redirect(url_for('attendance.record', service_date=service_date.date().isoformat()))


@attendance_bp.route('/<int:attendance_id>/delete', methods=['POST'])
@staff_required
def delete(attendance_id):
    try:
        cur = get_cursor()
        cur.execute("DELETE FROM attendance WHERE attendance_id=%s", (attendance_id,))
        get_db().commit()
        cur.close()
        flash(_msg("msg_attendance_deleted"), "success")
    except Exception as e:
        logging.exception(f"删除出席失败: {e}")
        flash(_msg("msg_attendance_delete_error"), "danger")
    return redirect(url_for('attendance.record'))


@attendance_bp.route('/report')
@staff_required
def report():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT service_date, COUNT(*) AS count,
                   COUNT(DISTINCT event_id) AS events_used
            FROM attendance
            GROUP BY service_date
            ORDER BY service_date DESC
            LIMIT 20
        """)
        daily = cur.fetchall()
        cur.execute("""
            SELECT e.title, COUNT(a.attendance_id) AS count
            FROM attendance a
            JOIN events e ON a.event_id = e.event_id
            GROUP BY e.event_id, e.title
            ORDER BY count DESC
        """)
        by_event = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"出席报表加载失败: {e}")
        daily, by_event = [], []
    return render_template(
        'attendance/report.html',
        daily=daily,
        by_event=by_event,
        active_page='attendance_report',
    )

