from CCMC_HAM import bcrypt
from CCMC_HAM.db import get_db, get_cursor_context, IntegrityError, DatabaseError
from CCMC_HAM.constants import ROLE_MEMBER
def _svc_msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text



def register_member(username, first_name, last_name, email, phone, password):
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    try:
        with get_cursor_context() as cur:
            cur.execute("""
                INSERT INTO users (username, first_name, last_name, email, phone, password_hash, role_id, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Active')
            """, (username, first_name, last_name, email, phone, password_hash, ROLE_MEMBER))
            get_db().commit()
            return True, None
    except IntegrityError as e:
        get_db().rollback()
        msg = str(e).lower()
        if 'email' in msg:
            return False, _svc_msg("msg_email_taken")
        if 'username' in msg:
            return False, _svc_msg("msg_username_taken")
        return False, _svc_msg("msg_account_exists")
    except DatabaseError as e:
        get_db().rollback()
        return False, _svc_msg("msg_register_error", error=e)


def change_password(user_id, current_hash, current_password, new_password, confirm_password):
    if not bcrypt.check_password_hash(current_hash, current_password):
        return False, _svc_msg("msg_current_password_incorrect")
    if current_password == new_password:
        return False, _svc_msg("msg_new_password_same")
    if new_password != confirm_password:
        return False, _svc_msg("msg_password_mismatch")
    if len(new_password) < 8:
        return False, _svc_msg("msg_password_min")
    new_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    try:
        with get_cursor_context() as cur:
            cur.execute("UPDATE users SET password_hash=%s WHERE user_id=%s", (new_hash, user_id))
            get_db().commit()
        return True, None
    except DatabaseError:
        get_db().rollback()
        return False, _svc_msg("msg_password_update_error")

