"""CCMC Hamilton church management system - application factory."""
import logging
import os
from datetime import date as _date
from flask import Flask, g, session
from flask_bcrypt import Bcrypt
from flask_babel import Babel
from .constants import (
    ROLE_NAMES, ROLE_NAMES_EN,
    ROLE_ADMIN, ROLE_COORDINATOR, ROLE_OPERATOR, ROLE_MEMBER,
    CATEGORY_LABELS, CATEGORY_LABELS_EN,
    GROUP_TYPES, GROUP_TYPES_EN,
    VISITOR_STATUSES, VISITOR_STATUSES_EN,
    PRAYER_STATUSES, PRAYER_STATUSES_EN,
    ROSTER_STATUSES, ROSTER_STATUSES_EN,
)

bcrypt = Bcrypt()
babel = Babel()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', os.urandom(24).hex()),
        MAX_CONTENT_LENGTH=16 * 1024 * 1024,
    )
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    bcrypt.init_app(app)

    # ---- Configure Babel language ----
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

    def get_locale_for_babel():
        from .i18n import get_locale
        return get_locale()

    babel.init_app(app, locale_selector=get_locale_for_babel)

    from . import db
    db.init_app(app)

    # Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from .main import main_bp
    app.register_blueprint(main_bp)
    from .dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    from .events import events_bp
    app.register_blueprint(events_bp, url_prefix='/events')
    from .announcements import announcements_bp
    app.register_blueprint(announcements_bp, url_prefix='/announcements')
    from .prayer import prayer_bp
    app.register_blueprint(prayer_bp, url_prefix='/prayer')
    from .visitors import visitors_bp
    app.register_blueprint(visitors_bp, url_prefix='/visitors')
    from .attendance import attendance_bp
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    from .rosters import rosters_bp
    app.register_blueprint(rosters_bp, url_prefix='/rosters')
    from .fellowships import fellowships_bp
    app.register_blueprint(fellowships_bp, url_prefix='/fellowships')
    from .resources import resources_bp
    app.register_blueprint(resources_bp, url_prefix='/resources')
    from .reports import reports_bp
    app.register_blueprint(reports_bp, url_prefix='/reports')
    from .admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/manage')

    # ---- Context processor: role and label helpers ----
    @app.context_processor
    def inject_constants():
        from .i18n import get_locale
        lang = get_locale()
        cat_labels = CATEGORY_LABELS_EN if lang == 'en' else CATEGORY_LABELS
        group_labels = dict(GROUP_TYPES_EN if lang == 'en' else GROUP_TYPES)
        role_labels = ROLE_NAMES_EN if lang == 'en' else ROLE_NAMES
        visitor_labels = dict(VISITOR_STATUSES_EN if lang == 'en' else VISITOR_STATUSES)
        prayer_labels = dict(PRAYER_STATUSES_EN if lang == 'en' else PRAYER_STATUSES)
        roster_labels = dict(ROSTER_STATUSES_EN if lang == 'en' else ROSTER_STATUSES)
        return dict(
            ROLE_ADMIN=ROLE_ADMIN,
            ROLE_COORDINATOR=ROLE_COORDINATOR,
            ROLE_OPERATOR=ROLE_OPERATOR,
            ROLE_MEMBER=ROLE_MEMBER,
            ROLE_NAMES=role_labels,
            category_label=lambda c: cat_labels.get(c, c),
            group_type_label=lambda c: group_labels.get(c, c),
            visitor_status_label=lambda c: visitor_labels.get(c, c),
            prayer_status_label=lambda c: prayer_labels.get(c, c),
            roster_status_label=lambda c: roster_labels.get(c, c),
            now_year=_date.today().year,
        )

    # ---- Context processor: church settings ----
    @app.context_processor
    def inject_settings():
        settings = getattr(g, 'church_settings', None)
        if settings is None:
            settings = {}
            try:
                from .db import get_cursor
                cur = get_cursor()
                cur.execute("SELECT setting_key, setting_value FROM church_settings")
                settings = {row['setting_key']: row['setting_value'] for row in cur.fetchall()}
                cur.close()
            except Exception as e:
                logging.warning("Failed to read church_settings: %s", e)
                try:
                    from .db import get_db
                    get_db().rollback()
                except Exception:
                    pass
            g.church_settings = settings

        from .i18n import get_locale
        lang = get_locale()

        def get_setting(key, default=''):
            if lang == 'en':
                return settings.get(key + '_en') or settings.get(key, default)
            return settings.get(key, default)

        return dict(settings=settings, get_setting=get_setting)

    # ---- Context processor: current user ----
    @app.context_processor
    def inject_current_user():
        from .i18n import get_locale
        lang = get_locale()
        role_labels = ROLE_NAMES_EN if lang == 'en' else ROLE_NAMES
        if 'user_id' in session:
            return dict(
                current_user_name=session.get('display_name', session.get('username', '')),
                current_role_name=role_labels.get(session.get('role_id'), ''),
            )
        return dict(current_user_name='', current_role_name='')

    # ---- Context processor: language support ----
    @app.context_processor
    def inject_language_info():
        from .i18n import LANGUAGES, get_locale
        from .translations import TRANSLATIONS, t
        current_lang = get_locale()
        return dict(
            current_language=current_lang,
            languages=LANGUAGES,
            t=lambda key: t(key, current_lang),
            trans=TRANSLATIONS[current_lang],
            get_i18n_text=lambda obj, key: (obj.get(f'{key}_en') if current_lang == 'en' and obj.get(f'{key}_en') else obj.get(key, '')),
        )

    # ---- Before request: refresh session role ----
    @app.before_request
    def refresh_session():
        if 'user_id' not in session or app.config.get('TESTING'):
            return
        from flask import request
        if request.endpoint in ('auth.login', 'auth.register', 'static', None):
            return
        try:
            from .db import get_cursor
            cur = get_cursor()
            cur.execute(
                "SELECT role_id, status FROM users WHERE user_id = %s",
                (session['user_id'],),
            )
            row = cur.fetchone()
            cur.close()
            if not row or row['status'] != 'Active':
                session.clear()
                return
            if row['role_id'] != session.get('role_id'):
                session['role_id'] = row['role_id']
                session['is_super_admin'] = (row['role_id'] == ROLE_ADMIN)
        except Exception as e:
            logging.warning("Failed to refresh session: %s", e)

    # ---- Template filters ----
    @app.template_filter('date_nz')
    def date_nz(value, fmt='%d/%m/%Y %H:%M'):
        if not value:
            return ''
        if isinstance(value, str):
            return value
        return value.strftime(fmt)

    @app.template_filter('date_only')
    def date_only(value):
        if not value:
            return ''
        if isinstance(value, str):
            return value[:10]
        return value.strftime('%Y-%m-%d')

    @app.template_filter('photo_src')
    def photo_src(value):
        if not value:
            return ''
        if value.startswith('http://') or value.startswith('https://'):
            return value
        from flask import url_for
        return url_for('static', filename=value)

    @app.template_filter('hero_video_url')
    def hero_video_url(value):
        if not value:
            return ''
        value = value.strip()
        if 'youtube.com/watch' in value or 'youtu.be/' in value:
            video_id = ''
            if 'youtu.be/' in value:
                video_id = value.split('youtu.be/')[-1].split('?')[0]
            elif 'v=' in value:
                video_id = value.split('v=')[-1].split('&')[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}&controls=0&showinfo=0&rel=0"
        return value

    @app.template_filter('is_youtube')
    def is_youtube(value):
        return bool(value and ('youtube.com' in value or 'youtu.be' in value))

    return app
