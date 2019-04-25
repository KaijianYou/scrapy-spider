CREATE DATABASE IF NOT EXISTS `scrapy_spider` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `scrapy_spider`;

CREATE TABLE IF NOT EXISTS `zhihu_question` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `page_url` VARCHAR(512) NOT NULL,
    `question_id` BIGINT NOT NULL,
    `topic` VARCHAR(200),
    `title` VARCHAR(200) NOT NULL,
    `content` LONGTEXT NOT NULL,
    `answer_num` INT NOT NULL,
    `comment_num` INT NOT NULL,
    `view_num` INT NOT NULL,
    `follower_num` INT NOT NULL,
    `crawl_time` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY (`question_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `zhihu_answer` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `page_url` VARCHAR(512) NOT NULL,
    `question_id` INT NOT NULL,
    `answer_id` INT NOT NULL,
    `author_id` INT,
    `content` LONGTEXT NOT NULL,
    `comment_num` INT,
    `upvote_num` INT,
    `create_time` DATETIME,
    `update_time` DATETIME,
    `crawl_time` DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY (`answer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
