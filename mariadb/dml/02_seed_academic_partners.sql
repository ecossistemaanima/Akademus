-- ==============================================================================
-- Akademus DML: Carga Inicial de Parceiros Acadêmicos do Perfil Credly do Prof. Poyatos
-- ==============================================================================

INSERT INTO `academic_partners` (`code`, `name`, `category`, `website_url`, `description`, `is_active`) VALUES
    ('GOOGLE_CLOUD', 'Google Cloud', 'CLOUD_AI', 'https://cloud.google.com/edu', 'Capacitações acadêmicas em Inteligência Artificial Generativa (Gemini), Cloud Computing e Data Analytics.', TRUE),
    ('RED_HAT', 'Red Hat Academy', 'OPEN_SOURCE_LINUX', 'https://www.redhat.com/en/services/training/red-hat-academy', 'Treinamento oficial em Enterprise Linux, Containers, Kubernetes/OpenShift e automação com Ansible.', TRUE),
    ('CISCO', 'Cisco Networking Academy', 'NETWORKING_CYBER', 'https://www.netacad.com/', 'Formação acadêmica em Redes, Cibersegurança, Infraestrutura de Comunicação e IoT.', TRUE),
    ('AWS', 'Amazon Web Services (AWS Academy)', 'CLOUD_TECH', 'https://aws.amazon.com/training/awsacademy/', 'Treinamento de computação em nuvem, arquitetura distribuída e certificações globais AWS.', TRUE),
    ('SKILLABLE', 'Skillable', 'HANDS_ON_LABS', 'https://www.skillable.com/', 'Ambiente prático de laboratórios em nuvem e experiências práticas imersivas para estudantes.', TRUE),
    ('CERTIPROF', 'CertiProf', 'CERTIFICATIONS', 'https://certiprof.com/', 'Certificações profissionais internacionais em Cybersecurity, Scrum, Lifelong Learning e DevOps.', TRUE)
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`), `description` = VALUES(`description`);

-- Atualização das URLs de perfil profissional do Usuário Administrador (Prof. Henrique Poyatos)
UPDATE `users`
SET 
    `credly_url` = 'https://www.credly.com/users/hpoyatos/badges/credly',
    `linkedin_url` = 'https://www.linkedin.com/in/hpoyatos',
    `google_skills_boost_url` = 'https://www.cloudskillsboost.google/public_profiles/hpoyatos',
    `is_profile_public` = TRUE
WHERE `email` = 'hpoyatos@gmail.com';
