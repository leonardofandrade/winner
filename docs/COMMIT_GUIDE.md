Padrão de Commits do Projeto Winner
Este documento define como todos os commits devem ser escritos, tanto por humanos quanto por agentes de IA.

O objetivo é:

manter histórico limpo

facilitar code review

permitir versionamento semântico

permitir automação futura (changelog, releases, CI/CD)

🧱 1. Convenção Base: Conventional Commits (adaptado)
Todos os commits devem seguir o formato:

Código
<type>(<scope>): <short summary>

<optional body>

<optional footer>
🏷️ 2. Tipos permitidos
Tipo	Uso
feat	nova funcionalidade
fix	correção de bug
refactor	melhoria interna sem mudar comportamento
perf	otimização de performance
docs	documentação
test	testes
build	dependências, build system
chore	tarefas diversas sem impacto no código
style	formatação, lint, sem mudança lógica


🎯 3. Scopes permitidos (Winner)
Os scopes devem refletir a arquitetura do projeto:

Scope	Significado
models	alterações em modelos
services	lógica de negócio
repositories	acesso ao banco
parsers	parsing de arquivos
clients	HTTP clients
tasks	tarefas agendadas
commands	management commands
api	views, serializers, routers
core	utilidades, base classes
predictions	IA / heurísticas
docs	documentação
config	settings, env, setup
| Scope | Significado |
|-------|-------------|
| telegram | módulo do bot |
| telegram-services | services do bot |
| telegram-handlers | handlers do bot |
| telegram-commands | commands do bot |


🧩 4. Regras obrigatórias
✔️ 1. Commits sempre em inglês
Para manter padrão internacional.

✔️ 2. Mensagens curtas e objetivas
Máximo 72 caracteres no título.

✔️ 3. Corpo do commit opcional, mas útil
Use quando houver contexto importante.

✔️ 4. Nunca commitar código gerado sem revisão
Mesmo que venha de IA.

✔️ 5. Commits devem refletir a arquitetura Winner
Nada de commits genéricos como “update” ou “fix”.

🧪 5. Exemplos de commits corretos
✔️ Novo service
Código
feat(services): add Lotofacil import service
✔️ Novo parser
Código
feat(parsers): implement Lotofacil result parser
✔️ Correção de bug no repositório
Código
fix(repositories): correct contest update logic
✔️ Ajuste de performance
Código
perf(services): optimize result calculation loop
✔️ Documentação
Código
docs: add architecture overview to AGENT_GUIDE.md
✔️ Testes
Código
test(services): add tests for ImportLotofacilService
✔️ Refatoração
Código
refactor(services): extract helper method for number matching
❌ 6. Exemplos de commits proibidos
❌ Mensagens vagas
Código
update files
fix stuff
changes
❌ Português no commit
Código
feat(services): adiciona serviço de importação
❌ Commits gigantes misturando tudo
Código
feat: add models, services, views and tests
❌ Commits que quebram a arquitetura Winner
Código
feat(models): add business logic inside model
🧠 7. Regras para agentes de IA
✔️ O agente deve:
gerar commits seguindo este padrão

escrever commits em inglês

usar scopes corretos

dividir mudanças grandes em commits pequenos

❌ O agente não deve:
criar commits fora do padrão

misturar múltiplas responsabilidades

criar commits automáticos sem revisão humana

🏁 8. Mensagem final
O histórico de commits do Winner deve ser tão limpo quanto sua arquitetura.
Commits pequenos, claros e consistentes garantem evolução saudável do projeto.