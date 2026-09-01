USE ccmc_ham;
DELETE FROM visitors WHERE email = 'smoke@example.com';
DELETE FROM events WHERE title = '冒烟测试活动';
DELETE FROM announcements WHERE title = '冒烟测试通知';
DELETE FROM prayer_requests WHERE title = '冒烟测试代祷';
DELETE FROM attendance WHERE attendee_name IN ('张三', '李四', '王五');
DELETE FROM rosters WHERE task_name = '招待' AND service_date = '2099-01-02';
DELETE FROM resources WHERE title = '冒烟测试资料';
DELETE FROM `groups` WHERE group_name = '冒烟测试团契';
DELETE FROM group_membership WHERE group_id NOT IN (SELECT group_id FROM `groups`);
SELECT (SELECT COUNT(*) FROM visitors) AS v,
       (SELECT COUNT(*) FROM events) AS e,
       (SELECT COUNT(*) FROM `groups`) AS g;
