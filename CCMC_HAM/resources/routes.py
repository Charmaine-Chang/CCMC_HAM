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
resources_bp = Blueprint('resources', __name__)

RESOURCE_CATEGORIES = ['诗歌', '经文', '见证', '资料', '其他']


@resources_bp.route('/')
@login_required
def index():
    category = request.args.get('category', '').strip()
    query = request.args.get('q', '').strip()
    try:
        cur = get_cursor()
        sql = """
            SELECT r.*, u.username FROM resources r
            JOIN users u ON r.created_by = u.user_id
            WHERE r.is_published = 1
        """
        params = []
        if category:
            sql += " AND r.category = %s"
            params.append(category)
        if query:
            sql += " AND (r.title LIKE %s OR r.content LIKE %s)"
            params.extend([f"%{query}%", f"%{query}%"])
        sql += " ORDER BY r.is_featured DESC, r.created_at DESC"
        cur.execute(sql, params)
        resources = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"资源加载失败: {e}")
        resources = []
    return render_template(
        'resources/index.html',
        resources=resources,
        categories=RESOURCE_CATEGORIES,
        category=category,
        query=query,
        active_page='resources',
    )


@resources_bp.route('/new', methods=['GET', 'POST'])
@staff_required
def create():
    return _edit(None)


@resources_bp.route('/<int:resource_id>/edit', methods=['GET', 'POST'])
@staff_required
def edit(resource_id):
    return _edit(resource_id)


def _edit(resource_id):
    resource = None
    try:
        cur = get_cursor()
        if resource_id:
            cur.execute("SELECT * FROM resources WHERE resource_id=%s", (resource_id,))
            resource = cur.fetchone()
        cur.close()
    except Exception as e:
        logging.exception(f"资源表单加载失败: {e}")

    if request.method == 'POST':
        category = request.form.get('category', '资料')
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        is_featured = 1 if request.form.get('is_featured') else 0
        is_published = 1 if request.form.get('is_published') else 0
        if not title:
            flash(_msg("msg_resource_title_required"), "danger")
            return render_template('resources/form.html', resource=resource, categories=RESOURCE_CATEGORIES)
        try:
            cur = get_cursor()
            if resource_id:
                cur.execute("""
                    UPDATE resources SET category=%s, title=%s, content=%s, is_featured=%s, is_published=%s
                    WHERE resource_id=%s
                """, (category, title, content, is_featured, is_published, resource_id))
                flash(_msg("msg_resource_updated"), "success")
            else:
                cur.execute("""
                    INSERT INTO resources (category, title, content, is_featured, is_published, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (category, title, content, is_featured, is_published, session['user_id']))
                flash(_msg("msg_resource_saved"), "success")
            get_db().commit()
            cur.close()
            return redirect(url_for('resources.index'))
        except Exception as e:
            logging.exception(f"保存资源失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_resource_save_error"), "danger")

    return render_template('resources/form.html', resource=resource, categories=RESOURCE_CATEGORIES)


@resources_bp.route('/<int:resource_id>/delete', methods=['POST'])
@staff_required
def delete(resource_id):
    try:
        cur = get_cursor()
        cur.execute("DELETE FROM resources WHERE resource_id=%s", (resource_id,))
        get_db().commit()
        cur.close()
        flash(_msg("msg_resource_deleted"), "success")
    except Exception as e:
        logging.exception(f"删除资源失败: {e}")
        flash(_msg("msg_resource_delete_error"), "danger")
    return redirect(url_for('resources.index'))

