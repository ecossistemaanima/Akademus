# 💬 Stout / Revolt (Mensageria e Conversação Soberana)

Este documento documenta o ambiente de conversação independente integrado ao **Akademus**.

---

## 🎯 Objetivo

Oferecer um canal em tempo real para alunos, docentes e parceiros, descentralizado das plataformas dominadas por algoritmos predatórios (Big Techs). 

Baseado na pilha open-source **[Revolt](https://revolt.chat/) / Stout**:
- Comunicação por texto, voz e canais temáticos organizados por matéria/projeto.
- API aberta e amigável para bots e automações pedagógicas.
- Hospedagem própria com total controle dos dados e da privacidade dos usuários.

---

## 📂 Diretório de Configuração (`/stout`)

A pasta `/stout` é destinada aos manifestos, arquivos de configuração e definições de implantação da instância de Revolt/Stout:

```text
stout/
├── README.md                 # Instruções de setup do serviço
├── config/                   # Configurações de variáveis de ambiente e micro-serviços Revolt
└── k8s/                      # Manifestos Kubernetes (Deployments, Services, ConfigMaps, Ingress)
```

---

## 🤖 Papel da JocastaBOT no Stout

A moderação e dinamização do ambiente ocorrem de forma automatizada:
1. **Entrada e Verificação:** Apenas usuários autenticados via Akademus recebem os cargos e acessos aos canais corretos.
2. **Defesa Ativa:** Bloqueio de comportamentos que infrinjam as regras da comunidade acadêmica.
3. **Notificações Acadêmicas:** Avisos automáticos sobre novas avaliações, prazos de tarefas e dinâmicas de gamificação.
