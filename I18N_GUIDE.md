# 中英双语系统实现指南

## 已实现的功能

### 1. **核心基础设施**
- ✅ Flask-Babel 4.0.0 集成
- ✅ 语言检测和切换机制（Session/Cookie/浏览器语言）
- ✅ 导航栏语言切换器（中文/English）
- ✅ 自动语言保持（Session 记住用户选择）

### 2. **数据库支持**
数据库中以下表已添加英文字段：
- `groups`: `group_name_en`, `description_en`
- `events`: `title_en`, `description_en`
- `announcements`: `title_en`, `content_en`
- `prayer_requests`: `title_en`, `content_en`
- `resources`: `title_en`, `description_en`

### 3. **模板支持**
- 导航栏添加了语言切换下拉菜单
- 模板中可使用 `get_i18n_text()` 函数获取对应语言的文本
- 支持英文字段自动回退到中文

### 4. **路由配置**
- 新增 `/set-language/<language>` 路由用于切换语言
- 主页、团契、活动等页面已支持双语字段查询

## 使用方式

### 前端用户
导航栏右上角的全球图标 🌐 可以切换语言：
- **中文** (zh): 简体中文
- **English** (en): 英文

选择后会自动刷新页面并显示对应语言的内容。

### 后端开发
在模板中获取多语言文本：
```jinja2
{# 自动选择对应语言的文本 #}
{{ get_i18n_text(group, 'group_name') }}
{{ get_i18n_text(event, 'title') }}

{# 或者手动选择 #}
{% if current_language == 'en' %}
    {{ group.group_name_en or group.group_name }}
{% else %}
    {{ group.group_name }}
{% endif %}
```

在 Python 代码中：
```python
from CCMC_HAM.i18n import get_locale, set_language

# 获取当前语言
current_lang = get_locale()  # 返回 'zh' 或 'en'

# 设置语言（通常在用户选择时调用）
set_language('en')
```

## 翻译工作流程

### 添加新的双语内容
1. 在相应的表中添加 `<字段>_en` 列
2. 在 SQL 查询中选择中英两个字段
3. 在模板中使用 `get_i18n_text()` 函数

### 现有数据的英文翻译
1. 连接到数据库
2. 为各表的英文字段填充翻译内容
3. 示例：
```sql
UPDATE groups 
SET group_name_en = 'Young Adults Fellowship', 
    description_en = 'A fellowship for young adults in the church'
WHERE group_id = 1;
```

## 主要文件

| 文件 | 描述 |
|------|------|
| `CCMC_HAM/i18n.py` | 国际化配置和工具函数 |
| `CCMC_HAM/__init__.py` | Flask 应用初始化，集成 Babel |
| `CCMC_HAM/main/routes.py` | 主路由，包含语言切换端点 |
| `templates/base.html` | 基础模板，包含语言切换菜单 |

## 配置说明

在 `CCMC_HAM/__init__.py` 中：
```python
app.config['BABEL_DEFAULT_LOCALE'] = 'zh'  # 默认语言
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'  # 默认时区
```

在 `CCMC_HAM/i18n.py` 中定义支持的语言：
```python
LANGUAGES = {
    'zh': '中文',
    'en': 'English'
}
```

## 后续改进建议

1. **翻译文件** - 使用 gettext 和 `.po` 文件管理 UI 字符串翻译
2. **数据库内容** - 为所有用户可见的内容添加英文字段
3. **时间格式** - 根据语言自动调整日期/时间格式
4. **方向支持** - 如果添加 RTL 语言（如阿拉伯文），需要配置 CSS
5. **SEO** - 为不同语言版本的页面配置 hreflang 标签

## 测试

1. 打开 http://127.0.0.1:5000
2. 点击导航栏右上角的语言菜单
3. 选择 "English" 切换到英文
4. 验证导航菜单等 UI 元素是否显示英文
5. 验证数据库内容（如果已翻译）是否显示对应语言

## 常见问题

**Q: 为什么有些内容还是显示中文？**
A: 因为数据库中的英文字段还没有填充翻译内容。需要管理员在后台添加英文翻译。

**Q: 如何为新页面添加多语言支持？**
A: 
1. 在数据库表中添加 `<字段>_en` 列
2. 在 SQL 查询中选择两个字段
3. 在模板中使用 `get_i18n_text()` 函数

**Q: 语言设置如何持久化？**
A: 使用 Flask Session 保存用户选择。用户浏览不同页面时会保持选择的语言。
