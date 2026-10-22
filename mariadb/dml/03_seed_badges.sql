-- ==============================================================================
-- Akademus DML: Carga Inicial de Badges do Perfil Credly do Prof. Henrique Poyatos
-- ==============================================================================

-- 1. Inserção das Badges no Catálogo
INSERT INTO `badges` (`code`, `name`, `description`, `image_url`, `issuer_name`, `partner_id`, `is_active`) VALUES
    ('GOOGLE_GEMINI_APP', 'Create Your First Gemini Enterprise Application', 'Certifica habilidades práticas de desenvolvimento de aplicações corporativas com o Gemini da Google Cloud.', 'https://images.credly.com/images/3c923d13-42da-4765-995d-59f3030e042a/blob', 'Google Cloud', (SELECT id FROM academic_partners WHERE code = 'GOOGLE_CLOUD' LIMIT 1), TRUE),
    ('RH_ACADEMY_EDUCATOR_2026', '2026 Red Hat Academy - Program Educator', 'Instrutor credenciado para o programa acadêmico Red Hat Enterprise Linux e tecnologias Open Source em 2026.', 'https://images.credly.com/images/6e8e3a18-2082-47ff-8c2e-1445c36ac0c6/blob', 'Red Hat', (SELECT id FROM academic_partners WHERE code = 'RED_HAT' LIMIT 1), TRUE),
    ('RH_ACADEMY_EDUCATOR_2024', '2024 Red Hat Academy - Program Educator', 'Instrutor credenciado para o programa acadêmico Red Hat Enterprise Linux e tecnologias Open Source em 2024.', 'https://images.credly.com/images/74aaa0d0-8b75-4c8e-abb4-d0a016611268/image.png', 'Red Hat', (SELECT id FROM academic_partners WHERE code = 'RED_HAT' LIMIT 1), TRUE),
    ('CISCO_INSTRUCTOR_5_YEARS', 'Instructor 5 Years of Service', 'Reconhecimento institucional pelos 5 anos de dedicação como instrutor do Cisco Networking Academy.', 'https://images.credly.com/images/cd82123f-6dc4-4181-badb-7ab1bc6707cd/C05-743250-00_Cisco_Networking_Academy_Badge_Instructor_v4a-02-no-year.png', 'Cisco', (SELECT id FROM academic_partners WHERE code = 'CISCO' LIMIT 1), TRUE),
    ('CISCO_INSTRUCTOR_1_YEAR', 'Instructor 1 Year of Service', 'Reconhecimento de 1 ano de atuação no Cisco Networking Academy.', 'https://images.credly.com/images/4802acaa-a2f7-49be-9a8e-666fa3f42e41/C05-743250-00_Cisco_Networking_Academy_Badge_Instructor_v4a-01-no-year.png', 'Cisco', (SELECT id FROM academic_partners WHERE code = 'CISCO' LIMIT 1), TRUE),
    ('CISCO_LEARN_A_THON_2023', 'Networking Academy Learn-A-Thon 2023', 'Participação e liderança de estudantes na maratona Learn-A-Thon Cisco.', 'https://images.credly.com/images/b1395248-483c-48cd-b40d-7fe93837c37d/image.png', 'Cisco', (SELECT id FROM academic_partners WHERE code = 'CISCO' LIMIT 1), TRUE),
    ('AWS_ACADEMY_GRAD_CLOUD_FOUND', 'AWS Academy Graduate - Cloud Foundations - Training Badge', 'Formação técnica abrangente em conceitos fundamentais de nuvem AWS.', 'https://images.credly.com/images/e3541a0c-dd4a-4820-8052-5001006efc85/blob', 'Amazon Web Services Training and Certification', (SELECT id FROM academic_partners WHERE code = 'AWS' LIMIT 1), TRUE),
    ('AWS_CERTIFIED_CLOUD_PRACTITIONER', 'AWS Certified Cloud Practitioner', 'Certificação profissional comprovando visão geral abrangente da nuvem AWS, serviços centrais e segurança.', 'https://images.credly.com/images/00634f82-b07f-4bbd-a6bb-53de397fc3a6/image.png', 'Amazon Web Services Training and Certification', (SELECT id FROM academic_partners WHERE code = 'AWS' LIMIT 1), TRUE),
    ('SKILLABLE_25_STUDENTS', 'Instructor Recognition - 25 Students Reached', 'Reconhecimento de instrutor por alcançar 25 alunos em laboratórios imersivos na nuvem.', 'https://images.credly.com/images/39062840-39ce-47d5-9847-77cb60ccf5e9/LODS_Students_Reached_Badges_Role-03.png', 'Skillable', (SELECT id FROM academic_partners WHERE code = 'SKILLABLE' LIMIT 1), TRUE),
    ('SKILLABLE_10_STUDENTS', 'Instructor Recognition - 10 Students Reached', 'Reconhecimento por alcançar 10 alunos capacitados em labs.', 'https://images.credly.com/images/6f76e88a-752d-4932-a019-6d766a8b83d9/LODS_Students_Reached_Badges_Role-02.png', 'Skillable', (SELECT id FROM academic_partners WHERE code = 'SKILLABLE' LIMIT 1), TRUE),
    ('SKILLABLE_FIRST_CLASS', 'Instructor Recognition - First Class Delivered', 'Reconhecimento de primeira turma prática concluída.', 'https://images.credly.com/images/e9235cf3-519f-404b-ab34-181d98ea6c2a/image.png', 'Skillable', (SELECT id FROM academic_partners WHERE code = 'SKILLABLE' LIMIT 1), TRUE),
    ('CERTIPROF_CSFPC', 'Cyber Security Foundation Professional Certificate - CSFPC™ !', 'Certificação profissional internacional em fundamentos de segurança cibernética e mitigação de riscos.', 'https://images.credly.com/images/8a0fb550-4d51-41d0-be50-6c1f54526539/Cybersecurity-Foundation-Professional-Certificate-CSFPC.png', 'Certiprof', (SELECT id FROM academic_partners WHERE code = 'CERTIPROF' LIMIT 1), TRUE),
    ('CERTIPROF_LIFELONG_LEARNING', 'Lifelong Learning', 'Reconhecimento por mentalidade de evolução contínua e paixão pela educação.', 'https://images.credly.com/images/21e16d4d-d2df-46e6-9098-526caab49e63/blob', 'Certiprof', (SELECT id FROM academic_partners WHERE code = 'CERTIPROF' LIMIT 1), TRUE)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`), `description` = VALUES(`description`), `image_url` = VALUES(`image_url`);

-- 2. Pendurando as Badges no perfil do Prof. Henrique Poyatos (hpoyatos@gmail.com)
INSERT IGNORE INTO `user_badges` (`user_id`, `badge_id`, `issued_at`, `expires_at`, `evidence_url`)
SELECT 
    u.id, 
    b.id, 
    CASE b.code
        WHEN 'GOOGLE_GEMINI_APP' THEN '2026-10-22'
        WHEN 'RH_ACADEMY_EDUCATOR_2026' THEN '2026-05-30'
        WHEN 'RH_ACADEMY_EDUCATOR_2024' THEN '2024-08-01'
        WHEN 'CISCO_INSTRUCTOR_5_YEARS' THEN '2026-03-05'
        WHEN 'CISCO_INSTRUCTOR_1_YEAR' THEN '2023-07-25'
        WHEN 'CISCO_LEARN_A_THON_2023' THEN '2023-05-19'
        WHEN 'AWS_ACADEMY_GRAD_CLOUD_FOUND' THEN '2023-08-06'
        WHEN 'AWS_CERTIFIED_CLOUD_PRACTITIONER' THEN '2023-09-08'
        WHEN 'SKILLABLE_25_STUDENTS' THEN '2022-12-04'
        WHEN 'SKILLABLE_10_STUDENTS' THEN '2022-11-17'
        WHEN 'SKILLABLE_FIRST_CLASS' THEN '2022-11-17'
        WHEN 'CERTIPROF_CSFPC' THEN '2021-01-20'
        WHEN 'CERTIPROF_LIFELONG_LEARNING' THEN '2021-01-20'
        ELSE CURRENT_DATE
    END as issued_at,
    CASE b.code
        WHEN 'RH_ACADEMY_EDUCATOR_2026' THEN '2027-05-30'
        WHEN 'RH_ACADEMY_EDUCATOR_2024' THEN '2025-08-01'
        WHEN 'AWS_CERTIFIED_CLOUD_PRACTITIONER' THEN '2026-09-08'
        WHEN 'CERTIPROF_CSFPC' THEN '2023-01-20'
        WHEN 'CERTIPROF_LIFELONG_LEARNING' THEN '2023-01-20'
        ELSE NULL
    END as expires_at,
    'https://www.credly.com/users/hpoyatos/badges/credly' as evidence_url
FROM `users` u
CROSS JOIN `badges` b
WHERE u.email = 'hpoyatos@gmail.com';
