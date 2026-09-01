import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from CCMC_HAM.db import get_db, get_cursor
from CCMC_HAM.validators import is_valid_email
from CCMC_HAM.mailer import send_visitor_welcome
from CCMC_HAM.i18n import LANGUAGES, set_language

def _msg(key, **kwargs):
    from CCMC_HAM.i18n import get_locale
    from CCMC_HAM.translations import t
    text = t(key, get_locale())
    if kwargs:
        text = text.format(**kwargs)
    return text

main_bp = Blueprint('main', __name__)


@main_bp.route('/set-language/<language>')
def set_language_route(language):
    """切换语言 / Switch language"""
    if set_language(language):
        session.modified = True
    referrer = request.referrer or url_for('main.home')
    return redirect(referrer)


def _load_settings():
    try:
        cur = get_cursor()
        cur.execute("SELECT setting_key, setting_value FROM church_settings")
        settings = {row['setting_key']: row['setting_value'] for row in cur.fetchall()}
        cur.close()
        return settings
    except Exception as e:
        logging.warning("读取设置失败: %s", e)
        return {}


def _upcoming_events(limit=6):
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT e.*, g.group_name, g.group_name_en
            FROM events e
            LEFT JOIN `groups` g ON e.group_id = g.group_id
            WHERE e.is_published = 1 AND e.start_time >= NOW()
            ORDER BY e.start_time ASC
            LIMIT %s
        """, (limit,))
        events = cur.fetchall()
        cur.close()
        return events
    except Exception as e:
        logging.warning("读取活动失败: %s", e)
        return []


@main_bp.route('/')
def home():
    settings = _load_settings()
    events = _upcoming_events(8)

    try:
        cur = get_cursor()
        cur.execute("""
            SELECT group_id, group_name, group_name_en, group_type, description, description_en, 
                   meeting_time, meeting_time_en, meeting_location, meeting_location_en, contact_phone, primary_color
            FROM `groups`
            WHERE status = 'active' AND visibility = 'public'
            ORDER BY group_type, group_name
        """)
        groups = cur.fetchall()

        cur.execute("""
            SELECT a.announcement_id, a.title, a.title_en, a.content, a.content_en, a.image_url, a.created_at
            FROM announcements a
            WHERE a.is_published = 1
            ORDER BY a.created_at DESC
            LIMIT 3
        """)
        announcements = cur.fetchall()

        cur.execute("""
            SELECT p.title, p.title_en, p.content, p.content_en, p.created_at, u.username
            FROM prayer_requests p
            JOIN users u ON p.user_id = u.user_id
            WHERE p.is_public = 1
            ORDER BY p.created_at DESC
            LIMIT 3
        """)
        prayers = cur.fetchall()
        cur.close()
    except Exception as e:
        logging.warning("主页数据加载失败: %s", e)
        groups, announcements, prayers = [], [], []

    fellowships = [g for g in groups if g['group_type'] == 'fellowship']
    ministries = [g for g in groups if g['group_type'] != 'fellowship']
    return render_template(
        'public/home.html',
        settings=settings,
        events=events,
        groups=groups,
        fellowships=fellowships,
        ministries=ministries,
        announcements=announcements,
        prayers=prayers,
        active_page='home',
    )


@main_bp.route('/welcome')
def welcome():
    """新朋友登记入口页（含二维码）。"""
    settings = _load_settings()
    try:
        cur = get_cursor()
        cur.execute("""
            SELECT group_id, group_name, group_name_en, meeting_time, meeting_time_en, meeting_location, meeting_location_en, contact_phone
            FROM `groups`
            WHERE status = 'active' AND visibility = 'public' AND group_type = 'fellowship'
            ORDER BY group_name
        """)
        fellowships = cur.fetchall()
        cur.close()
    except Exception:
        fellowships = []
    return render_template('public/welcome.html', settings=settings, fellowships=fellowships)


@main_bp.route('/welcome/submit', methods=['POST'])
def welcome_submit():
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    fellowship_interest = request.form.get('fellowship_interest', '').strip()
    heard_from = request.form.get('heard_from', '').strip()
    notes = request.form.get('notes', '').strip()

    if not first_name:
        flash(_msg("msg_visitor_name_required"), "danger")
        return redirect(url_for('main.welcome'))
    if email and not is_valid_email(email):
        flash(_msg("msg_visitor_email_invalid"), "danger")
        return redirect(url_for('main.welcome'))

    try:
        cur = get_cursor()
        cur.execute("""
            INSERT INTO visitors
                (first_name, last_name, email, phone, fellowship_interest, heard_from, notes, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'new')
        """, (first_name, last_name, email, phone, fellowship_interest, heard_from, notes))
        get_db().commit()
        visitor_id = cur.lastrowid
        cur.close()

        settings = _load_settings()
        fellowships = []
        if email:
            try:
                cur = get_cursor()
                cur.execute("""
                    SELECT group_name, group_name_en, meeting_time, meeting_time_en, meeting_location, meeting_location_en, contact_phone
                    FROM `groups`
                    WHERE status='active' AND visibility='public' AND group_type='fellowship'
                    ORDER BY group_name
                """)
                fellowships = cur.fetchall()
                cur.close()
            except Exception:
                pass
            send_visitor_welcome(email, f"{first_name}{last_name}".strip(), settings, fellowships)

        flash(_msg("msg_visitor_thanks", name=first_name), "success")
        return redirect(url_for('main.welcome_thanks', visitor_id=visitor_id))
    except Exception as e:
        logging.exception(f"访客登记失败: {e}")
        try:
            get_db().rollback()
        except Exception:
            pass
        flash(_msg("msg_visitor_submit_error"), "danger")
        return redirect(url_for('main.welcome'))


@main_bp.route('/welcome/thanks')
def welcome_thanks():
    visitor_id = request.args.get('visitor_id', type=int)
    settings = _load_settings()
    return render_template('public/welcome_thanks.html', visitor_id=visitor_id, settings=settings)


@main_bp.route('/qr')
def qr_code():
    """新朋友登记二维码页面（可用于周日崇拜现场扫码）。"""
    settings = _load_settings()
    return render_template('public/qr.html', settings=settings)


@main_bp.route('/about')
def about():
    settings = _load_settings()
    return render_template('public/about.html', settings=settings, active_page='about')


@main_bp.route('/contact')
def contact():
    settings = _load_settings()
    return render_template('public/contact.html', settings=settings, active_page='contact')


@main_bp.route('/public-events')
def public_events():
    events = _upcoming_events(50)
    return render_template('public/events.html', events=events, active_page='events')

