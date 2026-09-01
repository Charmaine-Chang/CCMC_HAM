import logging
from CCMC_HAM.i18n import get_locale
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import login_required, staff_required
from CCMC_HAM.shared.helpers import parse_date
from CCMC_HAM.constants import ROSTER_STATUSES, ROSTER_STATUSES_EN

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
rosters_bp = Blueprint('rosters', __name__)


@rosters_bp.route('/')
@staff_required
def index():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT r.*, e.title AS event_title, e.title_en AS event_title_en, g.group_name, g.group_name_en, u.first_name, u.last_name, u.username
            FROM rosters r
            LEFT JOIN events e ON r.event_id = e.event_id
            LEFT JOIN `groups` g ON r.group_id = g.group_id
            JOIN users u ON r.user_id = u.user_id
            WHERE r.service_date >= CURDATE()
            ORDER BY r.service_date ASC, r.task_name
        """)
        rosters = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"轮值加载失败: {e}")
        rosters = []
    return render_template('rosters/index.html', rosters=rosters, statuses=(ROSTER_STATUSES_EN if get_locale() == 'en' else ROSTER_STATUSES), active_page='rosters')


@rosters_bp.route('/mine')
@login_required
def mine():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT r.*, e.title AS event_title, e.title_en AS event_title_en, g.group_name, g.group_name_en
            FROM rosters r
            LEFT JOIN events e ON r.event_id = e.event_id
            LEFT JOIN `groups` g ON r.group_id = g.group_id
            WHERE r.user_id = %s AND r.service_date >= CURDATE()
            ORDER BY r.service_date ASC
        """, (session['user_id'],))
        rosters = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"我的轮值加载失败: {e}")
        rosters = []
    return render_template('rosters/mine.html', rosters=rosters, statuses=(ROSTER_STATUSES_EN if get_locale() == 'en' else ROSTER_STATUSES), active_page='roster_mine')


@rosters_bp.route('/new', methods=['GET', 'POST'])
@staff_required
def create():
    if request.method == 'POST':
        task_name = request.form.get('task_name', '').strip()
        service_date = parse_date(request.form.get('service_date'))
        user_id = request.form.get('user_id')
        event_id = request.form.get('event_id') or None
        group_id = request.form.get('group_id') or None
        notes = request.form.get('notes', '').strip()
        if not task_name or not service_date or not user_id:
            flash(_msg("msg_roster_fields_required"), "danger")
            return redirect(url_for('rosters.create'))
        try:
            cur = get_cursor()
            cur.execute("""
                INSERT INTO rosters (group_id, event_id, task_name, service_date, user_id, status, notes, created_by)
                VALUES (%s, %s, %s, %s, %s, 'pending', %s, %s)
            """, (group_id, event_id, task_name, service_date.date().isoformat(), user_id, notes, session['user_id']))
            get_db().commit()
            cur.close()
            flash(_msg("msg_roster_created"), "success")
            return redirect(url_for('rosters.index'))
        except Exception as e:
            logging.exception(f"保存轮值失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_roster_save_error"), "danger")

    try:
        cur = get_cursor()
        cur.execute("SELECT user_id, first_name, last_name, username FROM users WHERE status='Active' ORDER BY first_name, last_name")
        users = cur.fetchall()
        cur.execute("SELECT event_id, title, title_en, start_time FROM events WHERE is_published=1 AND start_time >= NOW() ORDER BY start_time LIMIT 30")
        events = cur.fetchall()
        cur.execute("SELECT group_id, group_name, group_name_en FROM `groups` WHERE status='active' ORDER BY group_name")
        groups = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"轮值表单加载失败: {e}")
        users, events, groups = [], [], []
    return render_template('rosters/form.html', users=users, events=events, groups=groups)


@rosters_bp.route('/<int:roster_id>/status', methods=['POST'])
@login_required
def update_status(roster_id):
    status = request.form.get('status')
    if status not in [s[0] for s in ROSTER_STATUSES]:
        flash(_msg("msg_roster_invalid_status"), "danger")
        return redirect(url_for('rosters.mine'))
    try:
        cur = get_cursor()
        cur.execute("SELECT user_id FROM rosters WHERE roster_id=%s", (roster_id,))
        row = cur.fetchone()
        is_staff = session.get('role_id') in (1, 2)
        if not row:
            flash(_msg("msg_roster_not_found"), "warning")
            return redirect(url_for('rosters.mine'))
        if row['user_id'] != session['user_id'] and not is_staff:
            flash(_msg("msg_roster_self_only"), "danger")
            return redirect(url_for('rosters.mine'))
        cur.execute("UPDATE rosters SET status=%s WHERE roster_id=%s", (status, roster_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_roster_status_updated"), "success")
    except Exception as e:
        logging.exception(f"更新轮值状态失败: {e}")
        flash(_msg("msg_update_failed"), "danger")
    return redirect(url_for('rosters.mine'))


@rosters_bp.route('/<int:roster_id>/delete', methods=['POST'])
@staff_required
def delete(roster_id):
    try:
        cur = get_cursor()
        cur.execute("DELETE FROM rosters WHERE roster_id=%s", (roster_id,))
        get_db().commit()
        cur.close()
        flash(_msg("msg_roster_deleted"), "success")
    except Exception as e:
        logging.exception(f"删除轮值失败: {e}")
        flash(_msg("msg_roster_delete_error"), "danger")
    return redirect(url_for('rosters.index'))
