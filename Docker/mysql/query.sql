CREATE DATABASE IF NOT EXISTS `spam_mail_detection_db`;

CREATE USER 'bhavin'@'%' IDENTIFIED WITH caching_sha2_password BY 'SpamMysql@1234.';
GRANT ALL PRIVILEGES ON spam_mail_detection_db.* TO 'bhavin'@'%';
FLUSH PRIVILEGES;
