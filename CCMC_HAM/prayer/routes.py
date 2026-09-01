import logging
from CCMC_HAM.i18n import get_locale
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import login_required, staff_required
from CCMC_HAM.constants import PRAYER_STATUSES, PRAYER_STATUSES_EN

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
prayer_bp = Blueprint('prayer', __name__)


@prayer_bp.route('/')
@login_required
def index():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT p.*, u.username, u.first_name, u.last_name
            FROM prayer_requests p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY CASE p.status WHEN 'answered' THEN 1 ELSE 0 END, p.created_at DESC
        """)
        requests = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"代祷加载失败: {e}")
        requests = []
    return render_template('prayer/index.html', requests=requests, statuses=(PRAYER_STATUSES_EN if get_locale() == 'en' else PRAYER_STATUSES), active_page='prayer')


@prayer_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_public = 1 if request.form.get('is_public') else 0
        if not title or not content:
            flash(_msg("msg_prayer_required"), "danger")
            return render_template('prayer/form.html')
        try:
            cur = get_cursor()
            cur.execute("""
                INSERT INTO prayer_requests (user_id, title, content, is_public, status)
                VALUES (%s, %s, %s, %s, 'pending')
            """, (session['user_id'], title, content, is_public))
            get_db().commit()
            cur.close()
            flash(_msg("msg_prayer_submitted"), "success")
            return redirect(url_for('prayer.index'))
        except Exception as e:
            logging.exception(f"保存代祷失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_prayer_submit_error"), "danger")
    return render_template('prayer/form.html')


@prayer_bp.route('/<int:request_id>/status', methods=['POST'])
@staff_required
def update_status(request_id):
    status = request.form.get('status')
    if status not in [s[0] for s in PRAYER_STATUSES]:
        flash(_msg("msg_prayer_status_invalid"), "danger")
        return redirect(url_for('prayer.index'))
    try:
        cur = get_cursor()
        cur.execute("UPDATE prayer_requests SET status=%s WHERE request_id=%s", (status, request_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_prayer_status_updated"), "success")
    except Exception as e:
        logging.exception(f"更新代祷状态失败: {e}")
        flash(_msg("msg_prayer_status_update_error"), "danger")
    return redirect(url_for('prayer.index'))

