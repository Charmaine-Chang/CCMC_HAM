import csv
import io
import logging
from CCMC_HAM.i18n import get_locale
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.shared.decorators import staff_required
from CCMC_HAM.constants import VISITOR_STATUSES, VISITOR_STATUSES_EN

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
visitors_bp = Blueprint('visitors', __name__)


@visitors_bp.route('/')
@staff_required
def index():
    status_filter = request.args.get('status', '')
    try:
        cur = get_cursor()
        sql = """
            SELECT v.*, u.username AS recorder
            FROM visitors v
            LEFT JOIN users u ON v.created_by = u.user_id
        """
        params = []
        if status_filter:
            sql += " WHERE v.status = %s"
            params.append(status_filter)
        sql += " ORDER BY v.created_at DESC"
        cur.execute(sql, params)
        visitors = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"新朋友列表加载失败: {e}")
        visitors = []
    return render_template(
        'visitors/index.html',
        visitors=visitors,
        statuses=(VISITOR_STATUSES_EN if get_locale() == 'en' else VISITOR_STATUSES),
        status_filter=status_filter,
        active_page='visitors',
    )


@visitors_bp.route('/<int:visitor_id>/status', methods=['POST'])
@staff_required
def update_status(visitor_id):
    status = request.form.get('status')
    if status not in [s[0] for s in VISITOR_STATUSES]:
        flash(_msg("msg_visitor_status_invalid"), "danger")
        return redirect(url_for('visitors.index'))
    try:
        cur = get_cursor()
        cur.execute("UPDATE visitors SET status=%s WHERE visitor_id=%s", (status, visitor_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_visitor_status_updated"), "success")
    except Exception as e:
        logging.exception(f"更新新朋友状态失败: {e}")
        flash(_msg("msg_visitor_status_error"), "danger")
    return redirect(url_for('visitors.index'))


@visitors_bp.route('/export.csv')
@staff_required
def export_csv():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT visitor_id, first_name, last_name, email, phone, fellowship_interest,
                   heard_from, notes, status, created_at
            FROM visitors ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"导出新朋友失败: {e}")
        rows = []

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(['ID', '姓名', '姓氏', '邮箱', '电话', '感兴趣的团契', '如何认识教会', '备注', '状态', '登记时间'])
    status_names = dict(VISITOR_STATUSES)
    for r in rows:
        writer.writerow([
            r['visitor_id'], r['first_name'], r['last_name'], r['email'], r['phone'],
            r['fellowship_interest'], r['heard_from'], r['notes'],
            status_names.get(r['status'], r['status']), r['created_at'],
        ])
    output = buf.getvalue()
    return Response(
        '\ufeff' + output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment; filename=visitors.csv"},
    )

