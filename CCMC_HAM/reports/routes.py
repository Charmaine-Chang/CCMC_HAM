import logging
from flask import Blueprint, render_template
from CCMC_HAM.db import get_cursor
from CCMC_HAM.shared.decorators import staff_required

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/')
@staff_required
def index():
    try:
        cur = get_cursor()
        # 新朋友统计
        cur.execute("""
            SELECT DATE_FORMAT(created_at, '%Y-%m') AS ym, COUNT(*) AS count
            FROM visitors GROUP BY ym ORDER BY ym DESC LIMIT 12
        """)
        visitors_by_month = cur.fetchall()
        cur.execute("""
            SELECT status, COUNT(*) AS count FROM visitors GROUP BY status
        """)
        visitors_by_status = cur.fetchall()

        # 崇拜人数统计
        cur.execute("""
            SELECT service_date, COUNT(*) AS count
            FROM attendance GROUP BY service_date ORDER BY service_date DESC LIMIT 12
        """)
        attendance_daily = cur.fetchall()
        for row in attendance_daily:
            row['label'] = row['service_date'].strftime('%m-%d')
        cur.execute("""
            SELECT e.category, COUNT(DISTINCT a.service_date) AS dates, COUNT(*) AS total
            FROM attendance a JOIN events e ON a.event_id = e.event_id
            GROUP BY e.category
        """)
        attendance_by_category = cur.fetchall()

        # 团契人数
        cur.execute("""
            SELECT g.group_name, g.group_name_en, g.group_type,
                   COUNT(gm.membership_id) AS member_count
            FROM `groups` g
            LEFT JOIN group_membership gm ON g.group_id = gm.group_id AND gm.membership_status='active'
            WHERE g.status='active'
            GROUP BY g.group_id, g.group_name, g.group_type
            ORDER BY g.group_type, g.group_name
        """)
        group_counts = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"报表加载失败: {e}")
        visitors_by_month, visitors_by_status = [], []
        attendance_daily, attendance_by_category = [], []
        group_counts = []

    return render_template(
        'reports/index.html',
        visitors_by_month=visitors_by_month,
        visitors_by_status=visitors_by_status,
        attendance_daily=attendance_daily,
        attendance_by_category=attendance_by_category,
        group_counts=group_counts,
        active_page='reports',
    )
