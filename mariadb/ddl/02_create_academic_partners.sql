-- ==============================================================================
-- Akademus DDL: Tabela de Parceiros Acadêmicos & Atualização da Tabela de Usuários
-- ==============================================================================

-- 1. Criação da Tabela: academic_partners
CREATE TABLE IF NOT EXISTS `academic_partners` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `code` VARCHAR(64) NOT NULL UNIQUE,
    `name` VARCHAR(255) NOT NULL,
    `category` VARCHAR(64) NOT NULL DEFAULT 'CLOUD_TECH',
    `website_url` VARCHAR(512) NULL,
    `logo_url` VARCHAR(512) NULL,
    `description` TEXT NULL,
    `is_active` BOOLEAN NOT NULL DEFAULT TRUE,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX `idx_partners_code` (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Alteração da Tabela users para incluir URLs profissionais e controle de privacidade
ALTER TABLE `users`
    ADD COLUMN IF NOT EXISTS `credly_url` VARCHAR(512) NULL AFTER `google_picture`,
    ADD COLUMN IF NOT EXISTS `linkedin_url` VARCHAR(512) NULL AFTER `credly_url`,
    ADD COLUMN IF NOT EXISTS `google_skills_boost_url` VARCHAR(512) NULL AFTER `linkedin_url`,
    ADD COLUMN IF NOT EXISTS `bio` TEXT NULL AFTER `google_skills_boost_url`,
    ADD COLUMN IF NOT EXISTS `is_profile_public` BOOLEAN NOT NULL DEFAULT FALSE AFTER `bio`;
