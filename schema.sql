CREATE TABLE `users` (
    `id` VARCHAR(255) NOT NULL,
    `name` VARCHAR(255),
    `email` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `username` VARCHAR(255) NOT NULL,
    `status` VARCHAR(255) DEFAULT 'active',
    `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `email` (`email`),
    UNIQUE KEY `username` (`username`)
);


CREATE TABLE `roles` (
    `id` INT PRIMARY KEY AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL UNIQUE,
    `description` VARCHAR(255)
);


CREATE TABLE `user_role` (
    `user_id` VARCHAR(255),
    `role_id` INT,
    PRIMARY KEY (`user_id`, `role_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
    FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`)
);


insert into roles(name, description) values ("customer", "Customer"), ("admin", "Admin");



CREATE TABLE `api_keys` (
    id INT NOT NULL AUTO_INCREMENT,
    `key` VARCHAR(255) NOT NULL,
    expiration DATETIME,
    user_id VARCHAR(255),
    PRIMARY KEY (id),
    UNIQUE (`key`),
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE `articles` (
    `article_id` VARCHAR(255) PRIMARY KEY,
    `user_id` VARCHAR(255),
    `language` VARCHAR(255),
    `main_keywords` VARCHAR(255),
    `urls` TEXT,
    `status` ENUM('active', 'inactive', 'draft') default 'draft',
    `keywords` TEXT NULL,
    `heading_data` json NULL,
    `parsed_prompt` text null,
    `created_at` datetime,
    `total_words` INT default '0'
    `cost` float default '0.0'
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `prompts` (
    `prompt_id` VARCHAR(255) PRIMARY KEY,
    `user_id` VARCHAR(255),
    `name` VARCHAR(255),
    `description` TEXT,
    `text_area` TEXT,
    `gpt_model` VARCHAR(255),
    `temperature` FLOAT,
    `max_length` INTEGER,
    `top_p` FLOAT,
    `frequency_penalty` FLOAT,
    `presence_penalty` FLOAT,
    `created_at` datetime,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `settings` (
    `setting_id` VARCHAR(255) PRIMARY KEY,
    `api_key` VARCHAR(255),
    `user_id` VARCHAR(255),
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
);

CREATE TABLE `process_tbl` (
	`id` VARCHAR (255) PRIMARY KEY,
    `section_id` VARCHAR (255),
    `status` ENUM('pending', 'progress', 'completed') default 'pending',
    `response` text null,
    `cost` float default 0,
    `created_at` datetime,
    `prompt_format` text null,
    `article_id` VARCHAR(255),
	FOREIGN KEY (`article_id`) REFERENCES `articles` (`article_id`),
    `prompt_id` VARCHAR(255),
	FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`prompt_id`),
);