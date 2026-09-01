"""Login and role permission decorators."""
from functools import wraps
from flask import session, flash, redirect, url_for


def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash(_msg("msg_login_required"), "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def roles_required(*roles):
    """Require one of the given global roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash(_msg("msg_login_required"), "warning")
                return redirect(url_for('auth.login'))
            if session.get('role_id') not in roles:
                flash(_msg("msg_permission_denied"), "danger")
                return redirect(url_for('dashboard.index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return roles_required(1)(f)


def staff_required(f):
    return roles_required(1, 2)(f)


def ministry_required(f):
    return roles_required(1, 2, 3)(f)
