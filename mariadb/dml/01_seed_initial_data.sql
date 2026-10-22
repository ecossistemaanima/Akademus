-- ==============================================================================
-- Akademus DML: Carga Inicial de Dados (Seed Data)
-- Sistema: MariaDB 10.11+ / 11.x
-- Conteúdo:
--   1. Papéis de Acesso (Roles)
--   2. Universidades e Instituições da Ânima Educação
--   3. Usuário Administrador Mestre (hpoyatos@gmail.com)
--   4. Associação N:N do Administrador com TODAS as universidades Ânima
-- ==============================================================================

-- 1. Inserção de Roles
INSERT INTO `roles` (`id`, `name`, `description`) VALUES
    (1, 'ADMINISTRADOR', 'Acesso total aos CRUDs de Universidades, Usuários e aprovações.'),
    (2, 'PROFESSOR', 'Docente universitário, cria avaliações e orienta projetos sem exigência de RA.'),
    (3, 'ALUNO', 'Estudante universitário com RA obrigatório.'),
    (4, 'PARCEIRO', 'Instrutores ou convidados de empresas e entidades parceiras.')
ON DUPLICATE KEY UPDATE `description` = VALUES(`description`);

-- 2. Inserção das Universidades e Faculdades da Ânima Educação
INSERT INTO `universities` (`id`, `code`, `name`, `short_name`, `is_active`) VALUES
    (1, 'USJT', 'Universidade São Judas Tadeu', 'São Judas', TRUE),
    (2, 'UAM', 'Universidade Anhembi Morumbi', 'Anhembi Morumbi', TRUE),
    (3, 'UNIBH', 'Centro Universitário de Belo Horizonte', 'UniBH', TRUE),
    (4, 'UNA', 'Centro Universitário UNA', 'UNA', TRUE),
    (5, 'UNIFACS', 'Universidade Salvador', 'UNIFACS', TRUE),
    (6, 'UNP', 'Universidade Potiguar', 'UnP', TRUE),
    (7, 'UNISUL', 'Universidade do Sul de Santa Catarina', 'UNISUL', TRUE),
    (8, 'UNISOCIESC', 'Centro Universitário Sociesc', 'UniSociesc', TRUE),
    (9, 'IBMR', 'Centro Universitário IBMR', 'IBMR', TRUE),
    (10, 'UNIRITTER', 'Centro Universitário Ritter dos Reis', 'UniRitter', TRUE),
    (11, 'FADERGS', 'Centro Universitário FADERGS', 'FADERGS', TRUE),
    (12, 'UNICURITIBA', 'Centro Universitário Curitiba', 'UniCuritiba', TRUE),
    (13, 'AGES', 'Centro Universitário AGES', 'AGES', TRUE),
    (14, 'UNIFG', 'Centro Universitário FG', 'UniFG', TRUE),
    (15, 'FPB', 'Faculdade Internacional da Paraíba', 'FPB', TRUE),
    (16, 'MILTON_CAMPOS', 'Faculdade de Direito Milton Campos', 'Milton Campos', TRUE),
    (17, 'FASEH', 'Faculdade de Saúde e Ecologia Humana', 'FASEH', TRUE),
    (18, 'INSPIRALI', 'Inspirali Educação Médica', 'Inspirali', TRUE)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`), `short_name` = VALUES(`short_name`);

-- 3. Inserção do Usuário Administrador Mestre: Prof. Henrique Poyatos
-- Senha temporária definida: Admin@Akademus2026! (ou via login Google com hpoyatos@gmail.com)
INSERT INTO `users` (`id`, `name`, `email`, `password_hash`, `ra`, `status`) VALUES
    (1, 'Prof. Henrique Poyatos', 'hpoyatos@gmail.com', 'scrypt:32768:8:1$0QImWGBGwOxvnzpL$becea7de824b7e006d903c815ab0ae77a651767a6409ac68e14164be52486be6dd5435198b4fcd41a15816d3b74b6920100259da70f3d96b816552d77e159c40', NULL, 'APPROVED')
ON DUPLICATE KEY UPDATE `status` = 'APPROVED', `name` = VALUES(`name`);

-- 4. Associação de Papéis ao Usuário Administrador Mestre (ADMINISTRADOR e PROFESSOR)
INSERT IGNORE INTO `user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id
FROM `users` u
CROSS JOIN `roles` r
WHERE u.email = 'hpoyatos@gmail.com' AND r.name IN ('ADMINISTRADOR', 'PROFESSOR');

-- 5. Associação do Usuário Administrador a TODAS as Universidades da Ânima Educação
INSERT IGNORE INTO `user_universities` (`user_id`, `university_id`)
SELECT u.id, uni.id
FROM `users` u
CROSS JOIN `universities` uni
WHERE u.email = 'hpoyatos@gmail.com';
