# CCMC_HAM 教会管理系统

**漢美頓懷恩堂 (Hamilton Chinese Methodist Church) Church Management System**

项目代号 **CCMC_HAM**，是一个基于 Flask + MySQL 架构的教会管理平台：内置**登录、角色权限（RBAC）、小组、看板、通知、资源库**等核心机制，以及**视频主页、行事历、活动宣传、新朋友录入、代祷事项、崇拜人数、服事轮值、统计报表**等教会专属功能。

> 当前仓库只包含 CCMC_HAM 教会管理系统，与原生态保育项目无关的内容已全部移除。

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.13、Flask 3.1 |
| 数据库 | MySQL 8.0、PyMySQL |
| 前端 | Jinja2、Bootstrap 5、Vanilla JS、Chart.js（报表） |
| 认证 | Flask-BCrypt、自定义 RBAC 装饰器 |
| 邮件 | smtplib（新朋友欢迎信，可配置 SMTP） |

---

## 功能一览

### 公开门户（不需要登录）
- **视频主页**：ccmc.nz 风格的全屏视频 Hero（支持 MP4 / YouTube 链接，可在后台"教会设置"中更换）
- 教会信息、主日崇拜（两场崇拜的时间与地点）、团契生活、事工活动
- 近期公开活动行事历、教会通知、公开代祷墙
- **新朋友登记**：在线表单 + 现场扫码二维码页；登记后自动发送欢迎邮件（含教会信息、团契介绍与联系人）
- 联系我们

### 登录后的角色权限
| 角色 | 权限 |
|---|---|
| 系统管理员 | 全部功能：成员与角色管理、教会设置、团契/事工管理、活动、通知、新朋友、崇拜人数、轮值、报表 |
| 执事 | 活动/通知/资源发布编辑、新朋友跟进、崇拜人数记录与报表、服事轮值管理、团契管理、代祷状态更新 |
| 服事人员 | 记录崇拜人数、查看/确认自己的轮值、查看行事历与通知、提交代祷 |
| 会友 | 查看行事历/通知/代祷/资源/团契、加入团契、查看自己的轮值、维护个人资料 |

### 管理模块
- **行事历**：月历视图 + 活动列表 + 活动详情；支持分类（主日崇拜/祷告会/团契/外展/事工/特别聚会）
- **活动宣传**：教会通知与活动推广发布、按团契归类
- **代祷事项**：提交、公开/保密、状态跟进（待代祷/代祷中/已蒙应允）
- **新朋友管理**：登记列表、状态跟进（新登记/已联络/已加入）、备注、CSV 导出
- **崇拜人数记录**：按日期/活动批量录入（招待员可直接粘贴名单）、出席报表
- **服事轮值**：按日期/活动/事工组安排（招待、司琴、读经、音控等），服事人员可确认
- **团契与事工**：团契信息管理、成员/组长管理、加入/退出团契
- **资源库**：诗歌、经文、见证、资料的发布与检索
- **统计报表**：新朋友按月/状态统计、崇拜人数趋势图、各团契小组人数占比
- **系统管理**：成员账号与角色/状态管理、教会信息/主页视频/SMTP 设置

---

## 快速开始

### 环境要求
- Python 3.13+
- MySQL 8.0（本地运行）

### 1. 安装依赖

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. 配置 MySQL

编辑 `CCMC_HAM/connect_local.py`，填入本地 MySQL 的用户名、密码：

```python
dbuser = "root"
dbpass = "你的密码"
dbhost = "127.0.0.1"
dbport = 3306
dbname = "ccmc_ham"
```

创建数据库并导入 schema 与种子数据（已导入过可跳过）：

```bash
mysql -u root -p -e "CREATE DATABASE ccmc_ham CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p --default-character-set=utf8mb4 ccmc_ham < sql/ccmc_create_database.sql
mysql -u root -p --default-character-set=utf8mb4 ccmc_ham < sql/ccmc_populate_database.sql
```

### 3. 运行

```bash
flask run          # 或 python app.py
```

打开 http://127.0.0.1:5005

### 演示账号（密码均为 `Password123!`）

| 用户名 | 角色 |
|---|---|
| `admin` | 系统管理员 |
| `coord_chen` | 执事 |
| `op_lin` | 服事人员 |
| `member_wang` | 会友 |

---

## 验证

```bash
python scripts/smoke_test.py    # 冒烟测试：公开页 + 各角色权限 + 增删改流程
```

测试产生的数据可通过 `scripts/cleanup_smoke.sql` 清理，或直接重新导入种子数据恢复初始状态。

---

## 目录结构

```
CCMC_HAM/                 # 教会管理系统（项目主包）
  auth/                   # 登录 / 注册 / 个人资料
  main/                   # 公开门户（视频主页、新朋友登记、二维码）
  dashboard/              # 角色看板
  events/                 # 行事历
  announcements/          # 活动宣传 / 通知
  prayer/                 # 代祷事项
  visitors/               # 新朋友管理
  attendance/             # 崇拜人数
  rosters/                # 服事轮值
  fellowships/            # 团契与事工
  resources/              # 诗歌 / 经文 / 见证 / 资料
  reports/                # 统计报表
  admin/                  # 成员权限与教会设置
  shared/                 # RBAC 装饰器等
  templates/ static/      # 模板与前端资源
sql/ccmc_*.sql            # 教会系统建库与种子数据
scripts/                  # 冒烟测试与清理脚本
```
