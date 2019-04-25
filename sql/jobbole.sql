CREATE DATABASE IF NOT EXISTS `scrapy_spider` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `scrapy_spider`;

CREATE TABLE IF NOT EXISTS `jobbole_article` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `page_url` VARCHAR(512) NOT NULL,
    `page_url_object_id` VARCHAR(128) NOT NULL,
    `cover_url` VARCHAR(512),
    `title` VARCHAR(200) NOT NULL,
    `create_time` DATE,
    `tags` VARCHAR(200),
    `content` LONGTEXT NOT NULL,
    `comment_num` INT,
    `upvote_num` INT,
    `collection_num` INT,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
