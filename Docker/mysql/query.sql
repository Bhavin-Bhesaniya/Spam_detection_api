CREATE DATABASE IF NOT EXISTS `spam_mail_detection_db`;

CREATE USER 'bhavin'@'%' IDENTIFIED WITH mysql_native_password BY 'Your_Pass';
GRANT ALL PRIVILEGES ON spam_mail_detection_db.* TO 'bhavin'@'%';
FLUSH PRIVILEGES;
