# Winner

Winner é um sistema completo para gerenciamento, análise e previsão de resultados da Lotofácil.  
Ele permite:

- Importar concursos oficiais da Caixa (periodicamente ou sob demanda)
- Registrar jogos do usuário
- Calcular automaticamente acertos e prêmios
- Gerar sugestões de jogos usando heurísticas e IA
- Expor API REST (Django REST Framework)
- Evoluir futuramente para UI web ou mobile

O projeto segue arquitetura limpa, com:
- Service Layer
- Repository Layer
- Clients
- Parsers
- Tasks
- Commands
- API modular

Todo o código é escrito em **inglês**, com **comentários em português**.

---

## 🚀 Tecnologias

- Python 3.12+
- Django 6+
- Django REST Framework
- httpx (async client)
- SQLite (inicialmente)
- Estrutura preparada para Celery (futuro)
- Estrutura preparada para ML (futuro)

---

## 📂 Estrutura do Projeto

winner/
│
├── core/
│   ├── services/
│   ├── utils/
│   └── exceptions/
│
├── loterias/
│   ├── models/
│   ├── serializers/
│   ├── views/
│   ├── urls/
│   ├── services/
│   ├── repositories/
│   ├── clients/
│   ├── parsers/
│   ├── tasks/
│   └── management/commands/
│
├── predicoes/
│   ├── services/
│   ├── models/
│   ├── views/
│   └── urls/
│
└── docs/
├── AGENT_GUIDE.md
├── CODING_STYLE.md
├── COMMIT_GUIDE.md
└── ROADMAP.md

Código

---

## 🧭 Filosofia do Projeto

Winner segue princípios de:

- Clean Architecture  
- Baixo acoplamento  
- Alta coesão  
- Testabilidade  
- Extensibilidade  
- Separação clara de responsabilidades  

---

## 🧪 Testes

- Services → testes unitários  
- Parsers → testes com arquivos reais  
- Repositories → testes de integração  
- API → testes de endpoints  

---

## 📜 Licença

Projeto privado do Leonardo.  
Licença a definir.