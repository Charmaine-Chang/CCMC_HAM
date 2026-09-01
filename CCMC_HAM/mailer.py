"""邮件发送工具 - 新朋友欢迎邮件"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.header import Header

logger = logging.getLogger(__name__)


def settings_value(settings, key, default=''):
    if not settings:
        return default
    row = settings.get(key)
    return row if row is not None else default


def send_visitor_welcome(email_to, visitor_name, settings, fellowships):
    """给新朋友发送欢迎邮件：教会信息 + 团契信息 + 联系方式。
    未配置 SMTP 时仅记录日志，不阻断访客登记。"""
    if not email_to:
        return False

    smtp_host = settings_value(settings, 'smtp_host', '')
    church_name = settings_value(settings, 'church_name', '漢美頓懷恩堂')
    church_name_en = settings_value(settings, 'church_name_en', 'Hamilton Chinese Methodist Church')
    pastor = settings_value(settings, 'pastor', '')
    phone = settings_value(settings, 'phone', '')
    email = settings_value(settings, 'email', '')
    office_address = settings_value(settings, 'office_address', '')
    s1 = settings_value(settings, 'service_1_name', '')
    s1t = settings_value(settings, 'service_1_time', '')
    s1l = settings_value(settings, 'service_1_location', '')
    s2 = settings_value(settings, 'service_2_name', '')
    s2t = settings_value(settings, 'service_2_time', '')
    s2l = settings_value(settings, 'service_2_location', '')

    lines = [
        f"亲爱的{visitor_name or '朋友'}，",
        "",
        f"欢迎您来到 {church_name}（{church_name_en}）！很高兴透过登记表认识您。",
        "",
        "【主日崇拜】",
        f"• {s1}：{s1t}，地点：{s1l}",
        f"• {s2}：{s2t}，地点：{s2l}",
        "",
        "【团契小组】",
    ]
    for g in (fellowships or []):
        info = f"• {g.get('group_name', '')}"
        if g.get('meeting_time'):
            info += f"（{g.get('meeting_time')}）"
        if g.get('meeting_location'):
            info += f"，地点：{g.get('meeting_location')}"
        lines.append(info)
    lines += [
        "",
        "【联系我们】",
        f"主理牧師：{pastor}",
        f"电话：{phone}",
        f"电邮：{email}",
        f"通讯地址：{office_address}",
        "",
        "欢迎您随时与我们联系，期待在教会与您相见！",
        "",
        "以马内利，",
        f"{church_name}",
    ]

    body = "\n".join(lines)
    msg = MIMEText(body, 'plain', 'utf-8')
    msg['Subject'] = Header(f"欢迎来到 {church_name}", 'utf-8')
    msg['From'] = settings_value(settings, 'smtp_from', 'noreply@example.com')
    msg['To'] = email_to

    if not smtp_host:
        logger.info("SMTP 未配置，跳过发送欢迎邮件至 %s", email_to)
        return False

    try:
        port = int(settings_value(settings, 'smtp_port', '587'))
        with smtplib.SMTP(smtp_host, port, timeout=20) as server:
            server.starttls()
            user = settings_value(settings, 'smtp_user', '')
            password = settings_value(settings, 'smtp_password', '')
            if user:
                server.login(user, password)
            server.send_message(msg)
        return True
    except Exception as e:
        logger.warning("发送欢迎邮件失败: %s", e)
        return False

