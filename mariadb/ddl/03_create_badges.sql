-- ==============================================================================
-- Akademus DDL: Tabelas de Badges & Associação com Usuários (User Badges)
-- ==============================================================================

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Tabela: badges (Catálogo de Badges Digitais disponíveis)
CREATE TABLE IF NOT EXISTS `badges` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(128) NOT NULL UNIQUE,
    `name` VARCHAR(255) NOT NULL,
    `description` TEXT NULL,
    `image_url` VARCHAR(512) NULL,
    `criteria_url` VARCHAR(512) NULL,
    `partner_id` INT NULL,
    `issuer_name` VARCHAR(128) NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_badges_code` (`code`),
    INDEX `idx_badges_partner` (`partner_id`),
    CONSTRAINT `fk_badges_partner` FOREIGN KEY (`partner_id`)
        REFERENCES `academic_partners` (`id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Tabela: user_badges (Badges emitidas e penduradas no perfil de um usuário)
CREATE TABLE IF NOT EXISTS `user_badges` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `badge_id` INT NOT NULL,
    `issued_at` DATE NOT NULL,
    `expires_at` DATE NULL,
    `credly_badge_id` VARCHAR(128) NULL,
    `evidence_url` VARCHAR(512) NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY `uk_user_badge` (`user_id`, `badge_id`, `issued_at`),
    INDEX `idx_user_badges_user` (`user_id`),
    INDEX `idx_user_badges_badge` (`badge_id`),
    CONSTRAINT `fk_user_badges_user` FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT `fk_user_badges_badge` FOREIGN KEY (`badge_id`)
        REFERENCES `badges` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

SET FOREIGN_KEY_CHECKS = 1;
