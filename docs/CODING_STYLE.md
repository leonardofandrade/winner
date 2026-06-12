# Winner — Coding Style Guide

---

## 🧩 Telegram Bot

### Handlers
- Devem ser finos
- Apenas delegam para services

### Services
- Toda lógica do bot
- Podem chamar services do domínio loterias

### Runner
- Apenas inicia polling

### Commands
- Apenas chamam o runner

### Repositórios
- Para armazenar TelegramUser
