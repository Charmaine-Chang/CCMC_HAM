-- ============================================================================
-- CCMC Hamilton 教会管理系统 Seed Data
-- 汉美顿怀恩堂 (Hamilton Chinese Methodist Church)
-- Run AFTER ccmc_create_database.sql
-- 默认密码: Password123!
-- ============================================================================

-- 1. 角色
INSERT INTO roles (role_id, role_name) VALUES
(1, '系统管理员'),
(2, '执事'),
(3, '服事人员'),
(4, '会友');

-- 2. 教会设置
INSERT INTO church_settings (setting_key, setting_value) VALUES
('church_name', '漢美頓懷恩堂'),
('church_name_en', 'Hamilton Chinese Methodist Church'),
('denomination', '紐西蘭基督教華人衛理公會'),
('verse_text', '惟有你们是被拣选的族类，是有君尊的祭司，是圣洁的国度，是属神的子民，要叫你们宣扬那召你们出黑暗入奇妙光明者的美德。'),
('verse_ref', '彼得前书 2:9'),
('hero_video_url', ''),
('welcome_message', '欢迎来到漢美頓懷恩堂！无论您是第一次来访还是已经熟悉我们，我们都非常高兴能认识您。'),
('pastor', '何明道牧師'),
('phone', '022 352 9500'),
('email', 'pastor@hcmc.nz'),
('office_address', '22 Piwakawaka Court, Rototuna North, Hamilton 3210'),
('service_1_name', '主日崇拜 (Hillcrest Chapel)'),
('service_1_time', '每周日 下午 2:00'),
('service_1_location', '120 Masters Ave, Hillcrest, Hamilton'),
('service_2_name', ''),
('service_2_time', ''),
('service_2_location', ''),
('smtp_host', ''),
('smtp_port', '587'),
('smtp_user', ''),
('smtp_password', ''),
('youtube_url', ''),
('smtp_from', 'noreply@hcmc.nz');

-- 3. 用户 (密码均为 Password123!)
INSERT INTO users (username, first_name, last_name, phone, email, password_hash, role_id, status) VALUES
('admin', '系统', '管理员', '022 352 9500', 'admin@hcmc.nz', '$2b$12$VnnvK2V9Onm3XypDfSWiseo.hp0FymbzDowkfkZ4spmqDw5/JX5cS', 1, 'Active'),
('coord_chen', '陈', '执事', '021 000 0002', 'coordinator@hcmc.nz', '$2b$12$VnnvK2V9Onm3XypDfSWiseo.hp0FymbzDowkfkZ4spmqDw5/JX5cS', 2, 'Active'),
('op_lin', '林', '弟兄', '021 000 0003', 'operator@hcmc.nz', '$2b$12$VnnvK2V9Onm3XypDfSWiseo.hp0FymbzDowkfkZ4spmqDw5/JX5cS', 3, 'Active'),
('member_wang', '王', '姐妹', '021 000 0004', 'member@hcmc.nz', '$2b$12$VnnvK2V9Onm3XypDfSWiseo.hp0FymbzDowkfkZ4spmqDw5/JX5cS', 4, 'Active'),
('member_li', '李', '弟兄', '021 000 0005', 'member2@hcmc.nz', '$2b$12$VnnvK2V9Onm3XypDfSWiseo.hp0FymbzDowkfkZ4spmqDw5/JX5cS', 4, 'Active');

-- 4. 团契 / 事工小组
INSERT INTO `groups` (group_name, group_type, description, meeting_time, meeting_location, contact_phone, leader_user_id, visibility, status) VALUES
('乐龄团契', 'fellowship', '为尊贵的年长弟兄姐妹而设，活动涵盖社交聚会、户外活动、文化艺术活动等，并提供关怀与支持。', '每周五 上午 10:00', '120 Masters Ave, Hillcrest', '021 123 4567', 2, 'public', 'active'),
('成人团契', 'fellowship', '成人团契提供查经、祷告会、社交聚会以及参与教会和社会活动的机会，帮助成年信徒在信仰中找到归属感。', '每周六 晚上 7:30', '22 Piwakawaka Court, Rototuna North', '021 000 0002', 2, 'public', 'active'),
('青年团契', 'fellowship', '尊主为圣，传扬福音。活动包括查经、聚餐、全年圣经阅读挑战等，支持青年人的属灵与个人成长。', '每周五 晚上 7:30', '22 Piwakawaka Court, Rototuna North', '021 000 0004', 4, 'public', 'active'),
('少年团契', 'fellowship', '透过福音影响青少年，使他们成为基督耶稣的门徒。', '每周六 下午 2:00', '120 Masters Ave, Hillcrest', '021 000 0005', 5, 'public', 'active'),
('大学生查经小组', 'fellowship', '由牧师指导的查经小组，定期阅读、讨论和分享圣经，帮助大学生建立属灵支持与友谊。', '每周四 晚上 7:00', '22 Piwakawaka Court, Rototuna North', '021 000 0002', 2, 'public', 'active'),
('祷告会', 'ministry', '集体祷告、唱诗、读经和属灵分享，一同寻求上帝的同在。', '每周三 晚上 7:30', '22 Piwakawaka Court, Rototuna North', '022 352 9500', 1, 'public', 'active'),
('英语角', 'ministry', '免费英语课程，由本地老师教学，分为初级、中级和高级班。', '每周二 晚上 7:00', '120 Masters Ave, Hillcrest', '022 352 9500', 1, 'public', 'active'),
('儿童主日学', 'ministry', '以故事、游戏、歌曲和手工艺教导孩子基督教信仰、圣经故事和道德。', '主日崇拜时段', '120 Masters Ave, Hillcrest', '022 352 9500', 1, 'public', 'active'),
('少年主日学', 'ministry', '在周日教会聚会时间内进行，帮助青少年建立信仰基础并与同龄人一起成长。', '主日崇拜时段', '120 Masters Ave, Hillcrest', '022 352 9500', 1, 'public', 'active'),
('招待事工', 'ministry', '主日崇拜及特别聚会的接待与签到服事。', '主日崇拜时段', '两处崇拜地点', '022 352 9500', 1, 'private', 'active');

-- 5. 团契成员
INSERT INTO group_membership (user_id, group_id, is_leader, membership_status) VALUES
(1, 1, 1, 'active'), (1, 2, 1, 'active'), (1, 3, 1, 'active'), (1, 4, 1, 'active'),
(1, 5, 1, 'active'), (1, 6, 1, 'active'), (1, 7, 1, 'active'), (1, 8, 1, 'active'),
(1, 9, 1, 'active'), (1, 10, 1, 'active'),
(2, 2, 1, 'active'), (2, 5, 1, 'active'),
(3, 10, 0, 'active'), (3, 2, 0, 'active'),
(4, 3, 1, 'active'),
(5, 4, 1, 'active'), (5, 2, 0, 'active');

-- 6. 行事历 (使用相对日期, 确保演示时有"近期"活动)
INSERT INTO events (group_id, title, description, location, start_time, end_time, category, is_published, created_by) VALUES
(NULL, '主日崇拜 (Hillcrest Chapel)', '主日崇拜：唱诗、祷告、证道。欢迎所有弟兄姐妹与朋友参加。', '120 Masters Ave, Hillcrest, Hamilton', DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY) + INTERVAL 14 HOUR, DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY) + INTERVAL 16 HOUR, 'worship', 1, 1),
(6, '周三祷告会', '一同为教会、城市与世界的需要祷告，分享感恩与代祷事项。', '22 Piwakawaka Court, Rototuna North', DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 19 HOUR, DATE_ADD(CURDATE(), INTERVAL 1 DAY) + INTERVAL 21 HOUR, 'prayer', 1, 1),
(7, '英语角 (初级班)', '免费英语课程，由本地老师教学。欢迎新朋友参加！', '120 Masters Ave, Hillcrest, Hamilton', DATE_ADD(CURDATE(), INTERVAL 2 DAY) + INTERVAL 19 HOUR, DATE_ADD(CURDATE(), INTERVAL 2 DAY) + INTERVAL 21 HOUR, 'ministry', 1, 1),
(3, '青年团契聚会', '查经、分享与团契时光。欢迎青年朋友加入！', '22 Piwakawaka Court, Rototuna North', DATE_ADD(CURDATE(), INTERVAL 5 DAY) + INTERVAL 19 HOUR, DATE_ADD(CURDATE(), INTERVAL 5 DAY) + INTERVAL 21 HOUR, 'fellowship', 1, 1),
(2, '成人团契聚会', '查经、祷告与彼此分享。', '22 Piwakawaka Court, Rototuna North', DATE_ADD(CURDATE(), INTERVAL 6 DAY) + INTERVAL 19 HOUR, DATE_ADD(CURDATE(), INTERVAL 6 DAY) + INTERVAL 21 HOUR, 'fellowship', 1, 1),
(1, '乐龄团契聚会', '社交聚会与关怀时光，欢迎年长弟兄姐妹参加。', '120 Masters Ave, Hillcrest', DATE_ADD(CURDATE(), INTERVAL 5 DAY) + INTERVAL 10 HOUR, DATE_ADD(CURDATE(), INTERVAL 5 DAY) + INTERVAL 12 HOUR, 'fellowship', 1, 1),
(NULL, '福音布道会（预告）', '年度福音布道会，欢迎邀请亲友参加。详细安排请留意教会通知。', '120 Masters Ave, Hillcrest, Hamilton', DATE_ADD(CURDATE(), INTERVAL 30 DAY) + INTERVAL 14 HOUR, DATE_ADD(CURDATE(), INTERVAL 30 DAY) + INTERVAL 17 HOUR, 'special', 1, 1);

-- 7. 活动宣传 / 通知
INSERT INTO announcements (group_id, title, content, is_published, created_by) VALUES
(NULL, '欢迎新朋友！', '欢迎您来到漢美頓懷恩堂！请填写"欢迎新朋友"登记表，我们会尽快与您联系，并为您介绍教会的团契与活动。', 1, 1),
(NULL, '教会行事历上线', '教会管理系统已启用行事历功能。执事与组长可以在系统中安排活动与服事轮值，会友可查看最新活动安排。', 1, 1),
(NULL, '英文班招生中', '英语角新一期免费课程开始报名，分为初级、中级和高级班，欢迎报名参加。', 1, 2),
(2, '成人团契查经：腓立比书', '本季查经主题为《腓立比书》，欢迎弟兄姐妹一起研读圣经、彼此分享。', 1, 2);

-- 8. 代祷事项
INSERT INTO prayer_requests (user_id, title, content, is_public, status) VALUES
(2, '为教会新朋友事工祷告', '求主带领新朋友事工，让更多朋友透过教会认识主耶稣。', 1, 'praying'),
(4, '为家人健康祷告', '求主保守家人的身体健康，赐下平安。', 0, 'pending'),
(3, '为社区英语角祷告', '求主使用英语角，让老师们传扬主耶稣的爱，与学生建立深厚关系。', 1, 'praying');

-- 9. 新朋友
INSERT INTO visitors (first_name, last_name, email, phone, fellowship_interest, heard_from, notes, status) VALUES
('张', '姐妹', 'zhang@example.com', '021 111 2222', '青年团契', '朋友介绍', '想了解青年团契和主日崇拜时间。', 'new'),
('David', 'Smith', 'david.smith@example.com', '022 333 4444', '英语角', '网站', '来自英国，对英语角和查经小组感兴趣。', 'contacted'),
('刘', '弟兄', 'liu@example.com', '027 555 6666', '成人团契', '路过教会', '希望参加成人团契聚会。', 'joined');

-- 10. 崇拜出席记录 (过去几周)
INSERT INTO attendance (event_id, service_date, attendee_name, user_id, recorded_by) VALUES
(1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '陈执事', 2, 3), (1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '林弟兄', 3, 3),
(1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '王姐妹', 4, 3), (1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '李弟兄', 5, 3),
(1, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '张姐妹(新朋友)', NULL, 3),
(2, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '陈执事', 2, 3), (2, DATE_SUB(CURDATE(), INTERVAL 14 DAY), '王姐妹', 4, 3),
(2, DATE_SUB(CURDATE(), INTERVAL 14 DAY), 'David Smith', NULL, 3),
(1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '陈执事', 2, 3), (1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '林弟兄', 3, 3),
(1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '王姐妹', 4, 3), (1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '李弟兄', 5, 3),
(1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '刘弟兄', NULL, 3), (1, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '赵姐妹(新朋友)', NULL, 3),
(2, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '陈执事', 2, 3), (2, DATE_SUB(CURDATE(), INTERVAL 7 DAY), '林弟兄', 3, 3),
(2, DATE_SUB(CURDATE(), INTERVAL 7 DAY), 'David Smith', NULL, 3);

-- 11. 服事轮值 (下个主日)
INSERT INTO rosters (group_id, event_id, task_name, service_date, user_id, status, created_by) VALUES
(10, 1, '招待', DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY), 3, 'confirmed', 1),
(10, 1, '司琴', DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY), 4, 'pending', 1),
(10, 1, '投影', DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY), 5, 'pending', 1),
(10, 2, '招待', DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY), 2, 'confirmed', 1),
(8, NULL, '儿童主日学老师', DATE_ADD(CURDATE(), INTERVAL (7 - WEEKDAY(CURDATE())) % 7 + 2 DAY), 4, 'pending', 1);

-- 12. 资源库
INSERT INTO resources (category, title, content, is_featured, is_published, created_by) VALUES
('诗歌', '祢真偉大', '主啊我神，我每逢举目观看，祢手所造一切奇妙大工；看见星宿，又听到隆隆雷声，祢的大能遍满了宇宙中。', 1, 1, 1),
('经文', '腓立比书 4:6-7', '应当一无挂虑，只要凡事借着祷告、祈求和感谢，将你们所要的告诉神。神所赐出人意外的平安，必在基督耶稣里保守你们的心怀意念。', 1, 1, 1),
('见证', '信主见证：从疑惑到平安', '曾经对信仰有许多疑问，但透过教会的弟兄姐妹的关怀与祷告，我经历了神的平安……', 0, 1, 2),
('资料', '主日崇拜程序', '宣召 → 唱诗 → 祷告 → 读经 → 证道 → 回应 → 报告 → 祝福。', 0, 1, 1);

