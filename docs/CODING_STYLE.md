# Winner — Coding Style Guide

Este documento define como o código deve ser escrito no projeto Winner.

---

## 🧩 Regras Gerais

- Código em **inglês**
- Comentários em **português**
- Métodos pequenos e coesos
- Classes com responsabilidade única
- Nada de lógica em models, views ou commands
- Service Layer obrigatória
- Repository Layer obrigatória

---

## 🧱 Models (Django 6+)

- Usar JSONField com default
- Usar QuerySets customizados quando fizer sentido
- Sem lógica de negócio

---

## 🧱 Services

- Classes com métodos claros
- Sem acesso direto ao ORM
- Usar repositories
- Podem ser async

---

## 🧱 Repositories

- Encapsulam ORM
- Nunca contêm lógica de negócio
- Podem ser async

---

## 🧱 Clients

- Usar httpx (async)
- Sem dependência de Django

---

## 🧱 Parsers

- Recebem texto bruto
- Retornam dicionários Python
- Não conhecem models

---

## 🧪 Testes

- Services → unitários
- Parsers → arquivos reais
- Repositories → integração
- API → endpoints

