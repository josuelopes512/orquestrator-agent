---
description: Responde perguntas sobre banco de dados consultando o knowledge base do agent
allowed-tools: Read, Glob, Grep
---

# Question: Database Expert

## Proposito

Responder perguntas sobre banco de dados (SQLite/SQLAlchemy) de forma focada, consultando apenas os arquivos relevantes do knowledge base deste agent.

## Diferenca do /question Global

- **/question global**: Consulta toda a codebase
- **/database/question**: Consulta apenas arquivos de banco de dados

## Knowledge Base

Consulte `KNOWLEDGE.md` para lista completa. Arquivos principais:

### Conexao e Configuracao
- `backend/src/database.py`
- `backend/src/database_manager.py`
- `backend/src/config/settings.py`

### Models (ORM)
- `backend/src/models/card.py`
- `backend/src/models/execution.py`
- `backend/src/models/activity_log.py`
- `backend/src/models/metrics.py`
- `backend/src/models/user.py`
- `backend/src/models/project.py`
- `backend/src/models/project_history.py`

### Repositories
- `backend/src/repositories/card_repository.py`
- `backend/src/repositories/execution_repository.py`
- `backend/src/repositories/activity_repository.py`
- `backend/src/repositories/metrics_repository.py`

### Schemas (Pydantic)
- `backend/src/schemas/card.py`
- `backend/src/schemas/auth.py`

### Services
- `backend/src/services/migration_service.py`
- `backend/src/services/metrics_collector.py`
- `backend/src/services/metrics_aggregator.py`
- `backend/src/services/auto_cleanup_service.py`

### Migrations
- `backend/migrations/*.sql`

## Instrucoes

1. **Leia o KNOWLEDGE.md** para entender o escopo completo
2. **Identifique arquivos relevantes** para a pergunta:
   - Pergunta sobre models? -> Consulte `backend/src/models/`
   - Pergunta sobre queries? -> Consulte `backend/src/repositories/`
   - Pergunta sobre migrations? -> Consulte `backend/migrations/`
   - Pergunta sobre conexao? -> Consulte `backend/src/database*.py`
3. **Consulte apenas esses arquivos** usando Read, Glob, Grep
4. **Responda com base no codigo real** encontrado
5. **Referencie os arquivos** que fundamentam a resposta (path:line)

## Restricoes

- **NAO MODIFICAR** nenhum arquivo
- **NAO CRIAR** novos arquivos
- **APENAS LER** e responder
- **FOCAR** nos arquivos do knowledge base de database

## Formato de Resposta

1. Resposta direta a pergunta
2. Referencias aos arquivos consultados (ex: `backend/src/models/card.py:45`)
3. Trechos de codigo relevantes (se aplicavel)
4. Conexoes com outros arquivos da area (models -> repositories -> services)

## Exemplos de Perguntas

- "Como funciona o model de Card?"
- "Quais campos tem a tabela executions?"
- "Como sao feitas as queries de metricas?"
- "Qual o padrao de migration?"
- "Como funciona o multi-database?"

## Pergunta

$ARGUMENTS
