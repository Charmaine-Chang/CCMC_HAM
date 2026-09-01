import logging
from CCMC_HAM.i18n import get_locale
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import login_required, staff_required
from CCMC_HAM.shared.helpers import parse_datetime, month_grid
from CCMC_HAM.constants import EVENT_CATEGORIES, EVENT_CATEGORIES_EN

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
events_bp = Blueprint('events', __name__)


def _groups_for_select(cur, include_all=True):
    cur.execute("""
        SELECT group_id, group_name, group_name_en FROM `groups`
        WHERE status = 'active' ORDER BY group_name
    """)
    return cur.fetchall()


def _fetch_event(cur, event_id):
    cur.execute("""
        SELECT e.*, g.group_name, g.group_name_en, u.username AS creator_name
        FROM events e
        LEFT JOIN `groups` g ON e.group_id = g.group_id
        LEFT JOIN users u ON e.created_by = u.user_id
        WHERE e.event_id = %s
    """, (event_id,))
    return cur.fetchone()


@events_bp.route('/')
@login_required
def index():
    today = date.today()
    year = request.args.get('year', today.year, type=int)
    month = request.args.get('month', today.month, type=int)
    try:
        first = date(year, month, 1)
    except ValueError:
        first = date(today.year, today.month, 1)
        year, month = first.year, first.month

    try:
        cur = get_cursor()
        cur.execute("""
            SELECT e.*, g.group_name, g.group_name_en
            FROM events e
            LEFT JOIN `groups` g ON e.group_id = g.group_id
            WHERE e.is_published = 1
              AND e.start_time >= %s AND e.start_time < %s
            ORDER BY e.start_time
        """, (date(year, month, 1).isoformat(), date(year + 1 if month == 12 else year, 1 if month == 12 else month + 1, 1).isoformat()))
        month_events = cur.fetchall()
        cur.execute("""
            SELECT e.*, g.group_name, g.group_name_en
            FROM events e
            LEFT JOIN `groups` g ON e.group_id = g.group_id
            WHERE e.is_published = 1 AND e.start_time >= NOW()
            ORDER BY e.start_time ASC LIMIT 20
        """)
        upcoming = cur.fetchall()
        groups = _groups_for_select(cur)
        cur.close()
    except Exception as e:
        logging.exception(f"行事历加载失败: {e}")
        month_events, upcoming, groups = [], [], []

    by_day = {}
    for ev in month_events:
        day = ev['start_time'].day
        by_day.setdefault(day, []).append(ev)

    prev_month = date(year - 1 if month == 1 else year, 12 if month == 1 else month - 1, 1)
    next_month = date(year + 1 if month == 12 else year, 1 if month == 12 else month + 1, 1)
    return render_template(
        'events/index.html',
        weeks=month_grid(year, month),
        year=year,
        month=month,
        today=today,
        by_day=by_day,
        upcoming=upcoming,
        groups=groups,
        prev_month=prev_month,
        next_month=next_month,
        active_page='events',
    )


@events_bp.route('/<int:event_id>')
@login_required
def detail(event_id):
    try:
        cur = get_cursor()
        event = _fetch_event(cur, event_id)
        cur.execute("""
            SELECT COUNT(*) AS c FROM attendance WHERE event_id = %s
        """, (event_id,))
        attendance_count = cur.fetchone()['c']
        cur.close()
    except Exception as e:
        logging.exception(f"活动详情加载失败: {e}")
        event, attendance_count = None, 0
    if not event or not event['is_published']:
        flash(_msg("msg_event_not_found"), "warning")
        return redirect(url_for('events.index'))
    return render_template(
        'events/detail.html',
        event=event,
        attendance_count=attendance_count,
        active_page='events',
    )


@events_bp.route('/new', methods=['GET', 'POST'])
@staff_required
def create():
    return _edit(request, None)


@events_bp.route('/<int:event_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit(event_id):
    return _edit(request, event_id)


def _edit(req, event_id):
    try:
        cur = get_cursor()
        groups = _groups_for_select(cur)
        event = _fetch_event(cur, event_id) if event_id else None
        cur.close()
    except Exception:
        groups, event = [], None

    if req.method == 'POST':
        title = req.form.get('title', '').strip()
        description = req.form.get('description', '').strip()
        location = req.form.get('location', '').strip()
        start_time = parse_datetime(req.form.get('start_time'))
        end_time = parse_datetime(req.form.get('end_time'))
        category = req.form.get('category', 'other')
        group_id = req.form.get('group_id') or None
        is_published = 1 if req.form.get('is_published') else 0

        if not title or not start_time:
            flash(_msg("msg_event_required"), "danger")
            return render_template('events/form.html', event=event, groups=groups, categories=(EVENT_CATEGORIES_EN if get_locale() == 'en' else EVENT_CATEGORIES))
        if not end_time or end_time < start_time:
            end_time = start_time

        try:
            cur = get_cursor()
            if event_id:
                cur.execute("""
                    UPDATE events SET group_id=%s, title=%s, description=%s, location=%s,
                           start_time=%s, end_time=%s, category=%s, is_published=%s
                    WHERE event_id=%s
                """, (group_id, title, description, location, start_time, end_time, category, is_published, event_id))
                flash(_msg("msg_event_updated"), "success")
            else:
                cur.execute("""
                    INSERT INTO events (group_id, title, description, location, start_time, end_time, category, is_published, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (group_id, title, description, location, start_time, end_time, category, is_published, session['user_id']))
                event_id = cur.lastrowid
                flash(_msg("msg_event_created"), "success")
            get_db().commit()
            cur.close()
            return redirect(url_for('events.detail', event_id=event_id))
        except Exception as e:
            logging.exception(f"保存活动失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_event_save_error"), "danger")

    return render_template('events/form.html', event=event, groups=groups, categories=(EVENT_CATEGORIES_EN if get_locale() == 'en' else EVENT_CATEGORIES))


@events_bp.route('/<int:event_id>/delete', methods=['POST'])
@staff_required
def delete(event_id):
    try:
        cur = get_cursor()
        cur.execute("DELETE FROM events WHERE event_id=%s", (event_id,))
        get_db().commit()
        cur.close()
        flash(_msg("msg_event_deleted"), "success")
    except Exception as e:
        logging.exception(f"删除活动失败: {e}")
        try:
            get_db().rollback()
        except Exception:
            pass
        flash(_msg("msg_event_delete_error"), "danger")
    return redirect(url_for('events.index'))
