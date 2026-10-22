# Akademus 🎓🎮

> Plataforma complementar de apoio à docência universitária, viabilizando um ambiente saudável, organizado e gamificado para avaliações contínuas e facilitação de treinamentos acadêmicos com parceiros.

---

## 🏛️ Origem do Nome & Conceito

O nome **Akademus** surge da fusão harmônica entre o saber clássico e o universo lúdico:
- **Akadēmeia (Ἀκαδήμεια):** Raiz grega do jardim e bosque onde Platão fundou sua Academia, berço do conhecimento, reflexão crítica e aprendizagem coletiva.
- **Ludus / Games:** O sufixo evoca a dinâmica dos jogos (*games*), fundamentando o princípio de que o processo pedagógico se torna substancialmente mais engajador, imersivo e interessante quando submetido a uma abordagem lúdica e estruturada.

A plataforma integra mecanismos de **gamificação** diretamente às atividades e avaliações contínuas, transformando rotinas de estudo e desafios teóricos em jornadas de conquista, colaboração e evolução.

---

## 🎯 Proposta & Objetivos

- **Apoio à Docência Universitária:** Ferramental moderno para gestão pedagógica e acompanhamento próximo da evolução dos estudantes.
- **Avaliações Contínuas:** Ambiente estruturado para atividades periódicas, feedbacks rápidos e mensuração transparente do aprendizado.
- **Treinamentos Acadêmicos com Parceiros:** Ponte prática entre o currículo acadêmico e iniciativas do mercado, permitindo capacitações integradas e projetos colaborativos.
- **Espaço Seguro e Focado:** Foco no bem-estar discente e docente, reduzindo o ruído dispersivo e estresse típico de redes abertas.

---

## 💬 Independência das Big Techs & Comunidade Própria

Diante dos rumos recentes das grandes redes sociais — cada vez mais pautadas por algoritmos opacos, interesses comerciais e monetização da atenção —, o **Akademus** adota uma postura firme de soberania digital:

- **Comunicação Soberana:** A plataforma integra um ambiente de conversação e interação em tempo real baseado no ecossistema open-source **[Revolt](https://revolt.chat/) / Stout** (uma alternativa robusta e independente ao Discord).
- **Segurança e Moderação Inteligente:** O espaço nasce protegido contra intrusos, spam e comportamentos nocivos às diretrizes da comunidade. A guardiã dessa ordem é a **JocastaBOT**, uma bot dedicada a automatizar boas-vindas, gerenciar permissões, aplicar as regras de convivência e mediar atividades pedagógicas.

---

## 🏗️ Arquitetura & Infraestrutura

Neste estágio inicial, a infraestrutura adota uma abordagem pragmática, modular e escalável:

| Componente | Descrição |
| :--- | :--- |
| **Ambiente Dev (`development`)** | **Gentoo Linux** local (`localhost` k3s control-plane) com runner GitHub Actions |
| **Ambiente Prod (`main`)** | **Debian Linux** (`lothlorien`) |
| **Borda, Túneis & Domínio** | **Cloudflare** roteando `akademus.tux.me.uk` para o cluster local |
| **Orquestração** | Pods e microsserviços em **Kubernetes (k3s)** (namespace `akademus` e `stoat`) |
| **Backend & API** | **Python** com framework **Flask** (orientado a **TDD**) |
| **Banco de Dados** | **MariaDB** com persistência em PVCs locais (`local-path`) |
| **Gestão de Segredos** | **K3s Secrets** locais isolados (zero credenciais commitadas no Git) |
| **Chat & Mensageria** | Instância dedicada de Revolt / Stout |
| **Automação & Moderação** | JocastaBOT |

Para mais detalhes da arquitetura e especificações técnicas, consulte a pasta [documentation/](file:///home/hpoyatos/CodeProjects/Akademus/documentation/index.md).

---

## ⚡ Desenvolvimento: Vibe Coding & IA

O desenvolvimento do Akademus adota a metodologia de **Vibe Coding**, unindo iteração rápida, experimentação contínua e prototipagem assistida por IA de ponta:

- **Harness & IDE:** [Google Antigravity IDE](https://antigravity.google/)
- **Modelo de Linguagem (LLM):** **Gemini** (Google DeepMind)
- **Metodologia:** Engenharia de software ágil guiada por intenção, onde design de arquitetura, testes e código fluem com automação inteligente e refinamento sob demanda.

---

## 📄 Licença

Este projeto é distribuído sob os termos da licença disponível no arquivo [LICENSE](file:///home/hpoyatos/CodeProjects/Akademus/LICENSE).
