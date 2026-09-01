import logging
from CCMC_HAM.i18n import get_locale
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import login_required, staff_required
from CCMC_HAM.constants import GROUP_TYPES, GROUP_TYPES_EN

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
fellowships_bp = Blueprint('fellowships', __name__)


@fellowships_bp.route('/')
@login_required
def index():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT g.*, u.first_name AS leader_first, u.last_name AS leader_last,
                   (SELECT COUNT(*) FROM group_membership gm WHERE gm.group_id = g.group_id AND gm.membership_status='active') AS member_count,
                   EXISTS(SELECT 1 FROM group_membership gm2 WHERE gm2.group_id = g.group_id AND gm2.user_id = %s) AS is_member
            FROM `groups` g
            LEFT JOIN users u ON g.leader_user_id = u.user_id
            WHERE g.status = 'active'
            ORDER BY g.group_type, g.group_name
        """, (session['user_id'],))
        groups = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"团契列表加载失败: {e}")
        groups = []
    return render_template('fellowships/index.html', groups=groups, group_types=dict(GROUP_TYPES_EN if get_locale() == 'en' else GROUP_TYPES), active_page='fellowships')


@fellowships_bp.route('/<int:group_id>')
@login_required
def detail(group_id):
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT g.*, u.first_name AS leader_first, u.last_name AS leader_last, u.phone AS leader_phone, u.email AS leader_email
            FROM `groups` g
            LEFT JOIN users u ON g.leader_user_id = u.user_id
            WHERE g.group_id = %s
        """, (group_id,))
        group = cur.fetchone()
        if not group:
            flash(_msg("msg_fellowship_not_found"), "warning")
            return redirect(url_for('fellowships.index'))
        cur.execute("""
            SELECT u.user_id, u.first_name, u.last_name, u.phone, u.email, gm.is_leader, gm.joined_at
            FROM group_membership gm
            JOIN users u ON gm.user_id = u.user_id
            WHERE gm.group_id = %s AND gm.membership_status = 'active'
            ORDER BY gm.is_leader DESC, u.first_name, u.last_name
        """, (group_id,))
        members = cur.fetchall()
        cur.execute("""
            SELECT e.event_id, e.title, e.title_en, e.start_time, e.location, e.location_en
            FROM events e WHERE e.group_id = %s AND e.is_published = 1 AND e.start_time >= NOW()
            ORDER BY e.start_time
        """, (group_id,))
        events = cur.fetchall()
        cur.execute("""
            SELECT membership_id FROM group_membership
            WHERE user_id = %s AND group_id = %s AND membership_status = 'active'
        """, (session['user_id'], group_id))
        is_member = cur.fetchone() is not None
        cur.execute("""
            SELECT user_id, first_name, last_name, username FROM users
            WHERE status = 'Active' ORDER BY first_name, last_name
        """)
        all_users = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"团契详情加载失败: {e}")
        group, members, events = None, [], []
        is_member, all_users = False, []
    if not group:
        return redirect(url_for('fellowships.index'))
    return render_template(
        'fellowships/detail.html',
        group=group,
        members=members,
        events=events,
        is_member=is_member,
        all_users=all_users,
        group_types=dict(GROUP_TYPES_EN if get_locale() == 'en' else GROUP_TYPES),
        active_page='fellowships',
    )


@fellowships_bp.route('/<int:group_id>/join', methods=['POST'])
@login_required
def join(group_id):
    try:
        cur = get_cursor()
        cur.execute("SELECT group_id, visibility FROM `groups` WHERE group_id=%s AND status='active'", (group_id,))
        group = cur.fetchone()
        if not group:
            flash(_msg("msg_fellowship_not_found"), "warning")
            return redirect(url_for('fellowships.index'))
        cur.execute("""
            SELECT membership_id FROM group_membership
            WHERE user_id=%s AND group_id=%s
        """, (session['user_id'], group_id))
        if cur.fetchone():
            flash(_msg("msg_fellowship_already_member"), "info")
            return redirect(url_for('fellowships.detail', group_id=group_id))
        cur.execute("""
            INSERT INTO group_membership (user_id, group_id, is_leader, membership_status)
            VALUES (%s, %s, 0, 'active')
        """, (session['user_id'], group_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_fellowship_welcome"), "success")
    except Exception as e:
        logging.exception(f"加入团契失败: {e}")
        try:
            get_db().rollback()
        except Exception:
            pass
        flash(_msg("msg_fellowship_join_error"), "danger")
    return redirect(url_for('fellowships.detail', group_id=group_id))


@fellowships_bp.route('/<int:group_id>/leave', methods=['POST'])
@login_required
def leave(group_id):
    try:
        cur = get_cursor()
        cur.execute("""
            DELETE FROM group_membership WHERE user_id=%s AND group_id=%s AND is_leader=0
        """, (session['user_id'], group_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_fellowship_left"), "info")
    except Exception as e:
        logging.exception(f"退出团契失败: {e}")
        flash(_msg("msg_fellowship_leave_error"), "danger")
    return redirect(url_for('fellowships.detail', group_id=group_id))


@fellowships_bp.route('/new', methods=['GET', 'POST'])
@staff_required
def create():
    return _edit(None)


@fellowships_bp.route('/<int:group_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit(group_id):
    return _edit(group_id)


def _edit(group_id):
    group = None
    try:
        cur = get_cursor()
        cur.execute("SELECT user_id, first_name, last_name, username FROM users WHERE status='Active' ORDER BY first_name")
        users = cur.fetchall()
        if group_id:
            cur.execute("SELECT * FROM `groups` WHERE group_id=%s", (group_id,))
            group = cur.fetchone()
        cur.close()
    except Exception as e:
        logging.exception(f"团契表单加载失败: {e}")
        users = []

    if request.method == 'POST':
        group_name = request.form.get('group_name', '').strip()
        group_type = request.form.get('group_type', 'fellowship')
        description = request.form.get('description', '').strip()
        meeting_time = request.form.get('meeting_time', '').strip()
        meeting_location = request.form.get('meeting_location', '').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        leader_user_id = request.form.get('leader_user_id') or None
        visibility = request.form.get('visibility', 'public')
        if not group_name:
            flash(_msg("msg_fellowship_name_required"), "danger")
            return render_template('fellowships/form.html', group=group, users=users, group_types=(GROUP_TYPES_EN if get_locale() == 'en' else GROUP_TYPES))
        try:
            cur = get_cursor()
            if group_id:
                cur.execute("""
                    UPDATE `groups` SET group_name=%s, group_type=%s, description=%s, meeting_time=%s,
                           meeting_location=%s, contact_phone=%s, leader_user_id=%s, visibility=%s
                    WHERE group_id=%s
                """, (group_name, group_type, description, meeting_time, meeting_location, contact_phone, leader_user_id, visibility, group_id))
                flash(_msg("msg_fellowship_updated"), "success")
            else:
                cur.execute("""
                    INSERT INTO `groups` (group_name, group_type, description, meeting_time, meeting_location,
                                          contact_phone, leader_user_id, visibility, status, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'active', %s)
                """, (group_name, group_type, description, meeting_time, meeting_location, contact_phone, leader_user_id, visibility, session['user_id']))
                group_id = cur.lastrowid
                flash(_msg("msg_fellowship_created"), "success")
            get_db().commit()
            cur.close()
            return redirect(url_for('fellowships.detail', group_id=group_id))
        except Exception as e:
            logging.exception(f"保存团契失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_fellowship_save_error"), "danger")

    return render_template('fellowships/form.html', group=group, users=users, group_types=(GROUP_TYPES_EN if get_locale() == 'en' else GROUP_TYPES))


@fellowships_bp.route('/<int:group_id>/membership', methods=['POST'])
@staff_required
def manage_membership(group_id):
    action = request.form.get('action')
    user_id = request.form.get('user_id')
    is_leader = 1 if request.form.get('is_leader') else 0
    try:
        cur = get_cursor()
        if action == 'add':
            cur.execute("""
                INSERT INTO group_membership (user_id, group_id, is_leader, membership_status)
                VALUES (%s, %s, %s, 'active')
                ON DUPLICATE KEY UPDATE membership_status='active', is_leader=VALUES(is_leader)
            """, (user_id, group_id, is_leader))
            flash(_msg("msg_fellowship_member_added"), "success")
        elif action == 'remove':
            cur.execute("DELETE FROM group_membership WHERE user_id=%s AND group_id=%s", (user_id, group_id))
            flash(_msg("msg_fellowship_member_removed"), "success")
        get_db().commit()
        cur.close()
    except Exception as e:
        logging.exception(f"管理团契成员失败: {e}")
        try:
            get_db().rollback()
        except Exception:
            pass
        flash(_msg("msg_fellowship_action_error"), "danger")
    return redirect(url_for('fellowships.detail', group_id=group_id))
