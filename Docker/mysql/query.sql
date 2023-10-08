CREATE DATABASE IF NOT EXISTS 'spam_mail_detection_db';
GO
USE 'spam_mail_detection_db';
GO
CREATE USER 'bhavin'@'localhost' IDENTIFIED BY 'SpamMysql@1234.';
GO
GRANT ALL PRIVILEGES ON spam_mail_detection_db.* TO 'bhavin'@'localhost';
GO
FLUSH PRIVILEGES;
GO