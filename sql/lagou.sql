CREATE DATABASE IF NOT EXISTS `scrapy_spider` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `scrapy_spider`;

CREATE TABLE IF NOT EXISTS `lagou_job` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `page_url` VARCHAR(512) NOT NULL COMMENT '页面URL',
    `page_url_object_id` VARCHAR(128) NOT NULL COMMENT '页面URL的哈希值',
    `title` VARCHAR(100) NOT NULL COMMENT '标题',
    `salary` VARCHAR(20) NOT NULL COMMENT '薪资',
    `city` VARCHAR(20) NOT NULL COMMENT '所在城市',
    `years_of_working` VARCHAR(10) NOT NULL COMMENT '工作年限',
    `edu_requirement` VARCHAR(10) NOT NULL COMMENT '学历要求',
    `type` VARCHAR(10) COMMENT '职位类型',
    `publish_time` VARCHAR(20) NOT NULL COMMENT '发布时间',
    `tags` VARCHAR(200) COMMENT '标签',
    `advantage` VARCHAR(200) COMMENT '职位诱惑',
    `desc` LONGTEXT NOT NULL COMMENT '职位描述',
    `work_addr` VARCHAR(100) COMMENT '工作地点',
    `company_url` VARCHAR(512) COMMENT '公司在拉勾网的主页URL',
    `company_name` VARCHAR(100) COMMENT '公司名',
    `crawl_time` DATETIME NOT NULL COMMENT '爬取时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY (`page_url_object_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
