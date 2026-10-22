-- ==============================================================================
-- Akademus DDL: Adição de colunas para armazenamento de Avatar diretamente no banco
-- ==============================================================================

ALTER TABLE `users` 
    ADD COLUMN `avatar_data` MEDIUMBLOB NULL AFTER `google_picture`,
    ADD COLUMN `avatar_mime_type` VARCHAR(64) NULL AFTER `avatar_data`;
