import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from CCMC_HAM import bcrypt
from CCMC_HAM.db import get_db, get_cursor_context, DatabaseError, IntegrityError
from CCMC_HAM.constants import ROLE_ADMIN, ROLE_COORDINATOR, ROLE_OPERATOR, ROLE_MEMBER, ROLE_NAMES
from CCMC_HAM.shared.decorators import login_required
from CCMC_HAM.validators import is_valid_email
from .auth_service import register_member, change_password

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text

auth_bp = Blueprint('auth', __name__)

ALLOWED_PHOTO_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


@auth_bp.after_app_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    return response


def _allowed_photo(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_PHOTO_EXTENSIONS


def dashboard_for_role(role_id):
    return url_for('dashboard.index')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        try:
            with get_cursor_context() as cur:
                cur.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(%s)", (username,))
                user = cur.fetchone()
                if user and bcrypt.check_password_hash(user['password_hash'], password):
                    if user['status'] != 'Active':
                        flash(_msg("msg_login_account_inactive"), "danger")
                        return render_template('auth/login.html', prefilled_username=username)
                    session.permanent = False
                    session['user_id'] = user['user_id']
                    session['username'] = user['username']
                    session['role_id'] = user['role_id']
                    session['is_super_admin'] = (user['role_id'] == ROLE_ADMIN)
                    session['display_name'] = f"{user['first_name'] or ''}{user['last_name'] or ''}".strip() or user['username']
                    flash(_msg("msg_welcome_back", name=session["display_name"]), "success")
                    return redirect(url_for('dashboard.index'))
                flash(_msg("msg_login_failed"), "danger")
        except DatabaseError as e:
            current_app.logger.error(f"登录数据库错误: {e}")
            flash(_msg("msg_login_error"), "danger")
        return render_template('auth/login.html', prefilled_username=username)

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('password_confirm', '')

        def redisplay(message):
            flash(message, "danger")
            return render_template('auth/register.html', form_data=request.form)

        if not username or not email or not password:
            return redisplay(_msg("msg_registration_fields_required"))
        if not is_valid_email(email):
            return redisplay(_msg("msg_invalid_email"))
        if password != confirm:
            return redisplay(_msg("msg_password_mismatch"))
        if len(password) < 8:
            return redisplay(_msg("msg_password_min"))

        ok, msg = register_member(username, first_name, last_name, email, phone, password)
        if not ok:
            return redisplay(msg)
        flash(_msg("msg_register_success"), "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form_data={})


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash(_msg("msg_logout_success"), "success")
    return redirect(url_for('main.home'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    try:
        with get_cursor_context() as cur:
            cur.execute("SELECT * FROM users WHERE user_id = %s", (session['user_id'],))
            user = cur.fetchone()
            if not user:
                flash(_msg("msg_user_not_found"), "danger")
                return redirect(url_for('auth.login'))

            cur.execute("""
                SELECT g.group_id, g.group_name, g.group_name_en, g.group_type, gm.is_leader, gm.membership_status
                FROM group_membership gm
                JOIN `groups` g ON gm.group_id = g.group_id
                WHERE gm.user_id = %s AND gm.membership_status = 'active'
                ORDER BY g.group_name
            """, (session['user_id'],))
            my_groups = cur.fetchall()

            if request.method == 'POST':
                action = request.form.get('action')
                if action == 'update_profile':
                    first_name = request.form.get('first_name', '').strip()
                    last_name = request.form.get('last_name', '').strip()
                    email = request.form.get('email', '').strip()
                    phone = request.form.get('phone', '').strip()
                    preferred_language = request.form.get('preferred_language', 'zh')
                    if not email or not is_valid_email(email):
                        flash(_msg("msg_invalid_email"), "danger")
                        return redirect(url_for('auth.profile'))
                    try:
                        cur.execute("""
                            UPDATE users SET first_name=%s, last_name=%s, email=%s, phone=%s, preferred_language=%s
                            WHERE user_id=%s
                        """, (first_name, last_name, email, phone, preferred_language, session['user_id']))
                        get_db().commit()
                        display = f"{first_name}{last_name}".strip() or session.get('username', '')
                        session['display_name'] = display
                        flash(_msg("msg_profile_updated"), "success")
                    except IntegrityError:
                        get_db().rollback()
                        flash(_msg("msg_email_taken"), "danger")
                    return redirect(url_for('auth.profile'))

                if action == 'update_photo':
                    file = request.files.get('profile_photo')
                    if file and file.filename:
                        secured = secure_filename(file.filename)
                        if not secured or not _allowed_photo(secured):
                            flash(_msg("msg_photo_invalid"), "danger")
                            return redirect(url_for('auth.profile'))
                        ext = secured.rsplit(".", 1)[1].lower()
                        unique = f"user_{session['user_id']}_{uuid.uuid4().hex}.{ext}"
                        upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'profiles')
                        os.makedirs(upload_dir, exist_ok=True)
                        file.save(os.path.join(upload_dir, unique))
                        cur.execute(
                            "UPDATE users SET profile_photo=%s WHERE user_id=%s",
                            (f"uploads/profiles/{unique}", session['user_id']),
                        )
                        get_db().commit()
                        flash(_msg("msg_photo_updated"), "success")
                    elif request.form.get('remove_photo'):
                        cur.execute("UPDATE users SET profile_photo=NULL WHERE user_id=%s", (session['user_id'],))
                        get_db().commit()
                        flash(_msg("msg_photo_removed"), "info")
                    return redirect(url_for('auth.profile'))

                if action == 'change_password':
                    ok, msg = change_password(
                        session['user_id'],
                        user['password_hash'],
                        request.form.get('current_password', ''),
                        request.form.get('new_password', ''),
                        request.form.get('confirm_password', ''),
                    )
                    flash(msg, "success" if ok else "danger")
                    return redirect(url_for('auth.profile'))

            return render_template('auth/profile.html', user=user, my_groups=my_groups)
    except DatabaseError as e:
        current_app.logger.error(f"Profile error: {e}")
        flash(_msg("msg_profile_load_error"), "danger")
        return redirect(url_for('main.home'))

