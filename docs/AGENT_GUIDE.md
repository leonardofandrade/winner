🏗️ 1. Arquitetura Geral do Projeto
O projeto segue uma arquitetura limpa e modular:

Código
lotofacil_project/
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
├── predicoes/ (opcional)
│   ├── services/
│   ├── models/
│   ├── views/
│   └── urls/
│
└── docs/
    └── AGENT_GUIDE.md
📌 Princípios obrigatórios
Toda lógica de negócio deve estar na service layer.

Views DRF devem ser finas, chamando apenas services.

Models devem ser simples, sem lógica.

Repositórios encapsulam acesso ao banco.

Parsers não conhecem models.

Clients não conhecem models.

Commands chamam services.

Tasks chamam services.

IA deve ser modular e substituível.

🧱 2. Convenções de Código
✔️ Service Layer
Cada serviço deve:

Ser uma classe

Ter métodos pequenos e claros

Não acessar diretamente o ORM (usar repositórios)

Não fazer parsing ou download (usar parsers/clients)

Exemplo:

python
class ImportarLotofacilService(BaseService):
    def executar(self):
        conteudo = CaixaClient().baixar_arquivo()
        concursos = LotofacilParser().parse(conteudo)
        return ConcursoRepository().salvar_concursos(concursos)
✔️ Repository Layer
Encapsula ORM

Nunca contém lógica de negócio

✔️ Clients
Apenas HTTP

Sem lógica de negócio

Sem dependência de Django

✔️ Parsers
Recebem texto bruto

Retornam dicionários ou objetos Python simples

✔️ Tasks / Commands
Apenas chamam services

Nunca implementam lógica

🧪 3. Testes
Services devem ter testes unitários

Parsers devem ter testes com arquivos reais

Repositórios devem ter testes de integração

Views devem ter testes de API

🧩 4. Fases de Desenvolvimento
Os agentes devem seguir estritamente as fases abaixo.

FASE 1 — Setup do projeto
Criar projeto Django, app, estrutura de pastas e base service.

FASE 2 — Modelos e Serializers
Criar models, serializers e migrações.

FASE 3 — Client + Parser
Criar client HTTP e parser do arquivo da Caixa.

FASE 4 — Importação
Criar service de importação + repositório + command.

FASE 5 — Cálculo de resultados
Criar services de cálculo e processamento.

FASE 6 — API
Criar ViewSets e endpoints.

FASE 7 — IA
Criar heurísticas e preparar terreno para ML.

FASE 8 — UI
Criar interface web ou mobile.

🤖 5. Instruções para Agentes de IA
✔️ O que o agente pode fazer
Gerar código Python, Django, DRF

Criar services, repositórios, parsers, clients

Criar comandos e tasks

Criar endpoints

Criar prompts adicionais

Criar documentação

Criar testes

Criar heurísticas de IA

Criar planos de arquitetura

❌ O que o agente NÃO pode fazer
Colocar lógica de negócio em views, models ou commands

Acessar ORM diretamente fora de repositórios

Criar código sem seguir a arquitetura

Criar UI antes da fase 8

Criar ML antes da fase 7

Criar arquivos fora da estrutura definida

Criar lógica duplicada

🧠 6. Estilo de Código
Python 3.12+

Django 5+

DRF

Tipagem opcional, mas recomendada

Métodos pequenos

Classes coesas

Sem funções gigantes

Sem lógica escondida em signals

🔮 7. IA e Predições
A IA deve ser implementada em camadas:

Heurística simples (frequência, atraso, pares/ímpares)

Modelos estatísticos

Modelos ML

Modelos avançados (opcional)

A IA deve ser:

Modular

Substituível

Independente do Django ORM

🧭 8. Como o agente deve responder
Sempre que o agente receber uma solicitação, ele deve:

Verificar em qual fase o pedido se encaixa

Seguir a arquitetura

Criar apenas o que pertence à fase

Criar código limpo e modular

Não avançar fases sem instrução explícita

🏁 9. Mensagem final para agentes
Este projeto deve ser construído de forma incremental, modular e limpa.
Toda lógica deve estar em services.
Nada deve ser acoplado.
Cada fase deve ser concluída antes da próxima.

🎉 Pronto!