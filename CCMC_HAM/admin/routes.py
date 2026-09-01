import logging
from CCMC_HAM.i18n import get_locale
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM import bcrypt
from CCMC_HAM.db import get_db, get_cursor, IntegrityError, DatabaseError
from CCMC_HAM.shared.decorators import admin_required
from CCMC_HAM.validators import is_valid_email
from CCMC_HAM.constants import ROLE_NAMES, ROLE_NAMES_EN

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/members')
@admin_required
def members():
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT u.*, r.role_name,
                   (SELECT COUNT(*) FROM group_membership gm WHERE gm.user_id = u.user_id AND gm.membership_status='active') AS group_count
            FROM users u JOIN roles r ON u.role_id = r.role_id
            ORDER BY u.role_id, u.username
        """)
        members = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.exception(f"成员列表加载失败: {e}")
        members = []
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.constants import ROLE_NAMES_EN
    role_names = ROLE_NAMES_EN if get_locale() == 'en' else ROLE_NAMES
    return render_template('admin/members.html', members=members, role_names=role_names, active_page='members')


@admin_bp.route('/members/add', methods=['GET', 'POST'])
@admin_required
def add_member():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        role_id = request.form.get('role_id', '4')
        password = request.form.get('password', '')
        if not username or not email or not password:
            flash(_msg("msg_required_username_email_password"), "danger")
            return render_template('admin/member_form.html', role_names=(ROLE_NAMES_EN if get_locale() == 'en' else ROLE_NAMES))
        if not is_valid_email(email):
            flash(_msg("msg_invalid_email"), "danger")
            return render_template('admin/member_form.html', role_names=(ROLE_NAMES_EN if get_locale() == 'en' else ROLE_NAMES))
        if len(password) < 8:
            flash(_msg("msg_password_min"), "danger")
            return render_template('admin/member_form.html', role_names=(ROLE_NAMES_EN if get_locale() == 'en' else ROLE_NAMES))
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            cur = get_cursor()
            cur.execute("""
                INSERT INTO users (username, first_name, last_name, email, phone, password_hash, role_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
            """, (username, first_name, last_name, email, phone, password_hash, role_id))
            get_db().commit()
            cur.close()
            flash(_msg("msg_member_created", username=username), "success")
            return redirect(url_for('admin.members'))
        except IntegrityError:
            get_db().rollback()
            flash(_msg("msg_username_or_email_exists"), "danger")
        except DatabaseError as e:
            get_db().rollback()
            flash(_msg("msg_create_member_failed", error=e), "danger")
    return render_template('admin/member_form.html', role_names=(ROLE_NAMES_EN if get_locale() == 'en' else ROLE_NAMES))


@admin_bp.route('/members/<int:user_id>/role', methods=['POST'])
@admin_required
def change_role(user_id):
    role_id = request.form.get('role_id')
    if role_id not in [str(r) for r in ROLE_NAMES]:
        flash(_msg("msg_invalid_role"), "danger")
        return redirect(url_for('admin.members'))
    if user_id == session['user_id']:
        flash(_msg("msg_cannot_change_own_role"), "warning")
        return redirect(url_for('admin.members'))
    try:
        cur = get_cursor()
        cur.execute("UPDATE users SET role_id=%s WHERE user_id=%s", (role_id, user_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_role_updated"), "success")
    except Exception as e:
        logging.exception(f"更新角色失败: {e}")
        flash(_msg("msg_update_failed"), "danger")
    return redirect(url_for('admin.members'))


@admin_bp.route('/members/<int:user_id>/status', methods=['POST'])
@admin_required
def change_status(user_id):
    status = request.form.get('status', 'Active')
    if status not in ('Active', 'Inactive', 'Suspended'):
        flash(_msg("msg_invalid_status"), "danger")
        return redirect(url_for('admin.members'))
    if user_id == session['user_id']:
        flash(_msg("msg_cannot_deactivate_self"), "warning")
        return redirect(url_for('admin.members'))
    try:
        cur = get_cursor()
        cur.execute("UPDATE users SET status=%s WHERE user_id=%s", (status, user_id))
        get_db().commit()
        cur.close()
        flash(_msg("msg_status_updated"), "success")
    except Exception as e:
        logging.exception(f"更新状态失败: {e}")
        flash(_msg("msg_update_failed"), "danger")
    return redirect(url_for('admin.members'))


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        keys = [
            'church_name', 'church_name_en', 'denomination', 'verse_text', 'verse_ref',
            'hero_video_url', 'welcome_message', 'pastor', 'phone', 'email', 'office_address',
            'service_1_name', 'service_1_time', 'service_1_location',
            'service_2_name', 'service_2_time', 'service_2_location',
            'smtp_host', 'smtp_port', 'smtp_user', 'smtp_password', 'smtp_from',
        ]
        try:
            cur = get_cursor()
            for key in keys:
                value = request.form.get(key, '').strip()
                cur.execute("""
                    INSERT INTO church_settings (setting_key, setting_value) VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE setting_value=VALUES(setting_value)
                """, (key, value))
            get_db().commit()
            cur.close()
            flash(_msg("msg_settings_saved"), "success")
            return redirect(url_for('admin.settings'))
        except Exception as e:
            logging.exception(f"保存设置失败: {e}")
            try:
                get_db().rollback()
            except Exception:
                pass
            flash(_msg("msg_save_settings_failed"), "danger")

    try:
        cur = get_cursor()
        cur.execute("SELECT setting_key, setting_value FROM church_settings")
        current = {row['setting_key']: row['setting_value'] for row in cur.fetchall()}
        cur.close()
    except Exception as e:
        logging.exception(f"读取设置失败: {e}")
        current = {}
    return render_template('admin/settings.html', current=current, active_page='settings')

