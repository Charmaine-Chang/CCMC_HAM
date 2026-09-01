"""CCMC Hamilton church management system - constants."""

# Roles
ROLE_ADMIN = 1        # Administrator
ROLE_COORDINATOR = 2  # Coordinator
ROLE_OPERATOR = 3     # Service operator
ROLE_MEMBER = 4       # Member

ROLE_NAMES = {
    ROLE_ADMIN: '系统管理员',
    ROLE_COORDINATOR: '执事',
    ROLE_OPERATOR: '服事人员',
    ROLE_MEMBER: '会友',
}

ROLE_NAMES_EN = {
    ROLE_ADMIN: 'Administrator',
    ROLE_COORDINATOR: 'Coordinator',
    ROLE_OPERATOR: 'Service Operator',
    ROLE_MEMBER: 'Member',
}

EVENT_CATEGORIES = [
    ('worship', '主日崇拜'),
    ('prayer', '祷告会'),
    ('fellowship', '团契聚会'),
    ('outreach', '外展布道'),
    ('ministry', '事工活动'),
    ('special', '特别聚会'),
    ('other', '其他'),
]

EVENT_CATEGORIES_EN = [
    ('worship', 'Sunday Worship'),
    ('prayer', 'Prayer Meeting'),
    ('fellowship', 'Fellowship Gathering'),
    ('outreach', 'Outreach & Evangelism'),
    ('ministry', 'Ministry Activity'),
    ('special', 'Special Gathering'),
    ('other', 'Other'),
]

CATEGORY_LABELS = {value: label for value, label in EVENT_CATEGORIES}
CATEGORY_LABELS_EN = {value: label for value, label in EVENT_CATEGORIES_EN}

GROUP_TYPES = [
    ('fellowship', '团契'),
    ('ministry', '事工'),
    ('worship', '崇拜'),
]

GROUP_TYPES_EN = [
    ('fellowship', 'Fellowship'),
    ('ministry', 'Ministry'),
    ('worship', 'Worship'),
]

VISITOR_STATUSES = [
    ('new', '新登记'),
    ('contacted', '已联络'),
    ('joined', '已加入'),
    ('declined', '暂不参与'),
]

VISITOR_STATUSES_EN = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('joined', 'Joined'),
    ('declined', 'Declined'),
]

PRAYER_STATUSES = [
    ('pending', '待代祷'),
    ('praying', '代祷中'),
    ('answered', '已蒙应允'),
]

PRAYER_STATUSES_EN = [
    ('pending', 'Pending'),
    ('praying', 'Praying'),
    ('answered', 'Answered'),
]

ROSTER_STATUSES = [
    ('pending', '待确认'),
    ('confirmed', '已确认'),
    ('completed', '已完成'),
]

ROSTER_STATUSES_EN = [
    ('pending', 'Pending'),
    ('confirmed', 'Confirmed'),
    ('completed', 'Completed'),
]
