# Winner — AI Development Guide

Este documento define como qualquer agente de IA deve atuar no projeto Winner.

---

# 🔷 1. Linguagem e Estilo
- Código em inglês
- Comentários em português

---

# 🔷 2. Arquitetura Obrigatória
Inclui agora o módulo Telegram Bot:

- Service Layer
- Repository Layer
- Clients
- Parsers
- Tasks
- Commands
- API
- **Telegram Bot (handlers finos + services)**

---

# 🔷 3. Regras para o Telegram Bot

- Handlers devem ser finos
- Toda lógica deve estar em services
- Nada de lógica em commands
- Nada de lógica em handlers
- Nada de lógica no runner
- Bot deve usar python-telegram-bot 21+ (async)
- Bot deve chamar services Winner existentes

---

# 🔷 4. Roadmap Awareness
O agente deve seguir:

- Fase 7.5 antes da UI
- Não criar UI antes da fase 8

---

# 🔷 5. O que o agente pode fazer
- Criar handlers
- Criar services do bot
- Criar runner
- Criar command
- Criar repositórios
- Criar testes do bot

---

# 🔷 6. O que o agente NÃO pode fazer
- Colocar lógica no handler
- Colocar lógica no command
- Criar UI antes da fase 8
- Criar ML antes da fase 7