import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import login_required, staff_required

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
announcements_bp = Blueprint('announcements', __name__)


@announcements_bp.route('/')
@login_required
def index():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT a.*, g.group_name, g.group_name_en, u.username
            FROM announcements a
            LEFT JOIN `groups` g ON a.group_id = g.group_id
            JOIN users u ON a.created_by = u.user_id
            WHERE a.is_published = 1
            ORDER BY a.created_at DESC
        """)
        announcements = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"通知加载失败: {e}")
        announcements = []
    return render_template('announcements/index.html', announcements=announcements, active_page='announcements')


@announcements_bp.route('/new', methods=['GET', 'POST'])
@staff_required
def create():
    return _edit(None)


@announcements_bp.route('/<int:announcement_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit(announcement_id):
    return _edit(announcement_id)


def _edit(announcement_id):
    announcement = None
    try:
        cur = get_cursor()
        cur.execute("SELECT group_id, group_name, group_name_en FROM `groups` WHERE status='active' ORDER BY group_name")
        groups = cur.fetchall()
        if announcement_id:
            cur.execute("SELECT * FROM announcements WHERE announcement_id=%s", (announcement_id,))
            announcement = cur.fetchone()
        cur.close()
    except Exception as e:
        logging.exception(f"通知编辑页加载失败: {e}")
        groups = []

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        group_id = request.form.get('group_id') or None
        is_published = 1 if request.form.get('is_published') else 0
        if not title:
            flash(_msg("msg_announcement_title_required"), "danger")
            return render_template('announcements/form.html', announcement=announcement, groups=groups)
        try:
            cur = get_cursor()
            if announcement_id:
                cur.execute("""
                    UPDATE announcements SET group_id=%s, title=%s, content=%s, is_published=%s
                    WHERE announcement_id=%s
                """, (group_id, title, content, is_published, announcement_id))
                flash(_msg("msg_announcement_updated"), "success")
            else:
                cur.execute("""
                    INSERT INTO announcements (group_id, title, content, is_published, created_by)
                    VALUES (%s, %s, %s, %s, %s)
                """, (group_id, title, content, is_published, session['user_id']))
                flash(_msg("msg_announcement_published"), "success")
            get_db().commit()
            cur.close()
            return redirect(url_for('announcements.index'))
        except Exception as e:
            logging.exception(f"保存通知失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_announcement_save_error"), "danger")

    return render_template('announcements/form.html', announcement=announcement, groups=groups)


@announcements_bp.route('/<int:announcement_id>/delete', methods=['POST'])
@staff_required
def delete(announcement_id):
    try:
        cur = get_cursor()
        cur.execute("DELETE FROM announcements WHERE announcement_id=%s", (announcement_id,))
        get_db().commit()
        cur.close()
        flash(_msg("msg_announcement_deleted"), "success")
    except Exception as e:
        logging.exception(f"删除通知失败: {e}")
        flash(_msg("msg_announcement_delete_error"), "danger")
    return redirect(url_for('announcements.index'))

