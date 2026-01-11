# Database Expert - Knowledge Base

## Tecnologia

- **Banco de Dados**: SQLite (multi-instância)
- **ORM**: SQLAlchemy 2.0+ (Async)
- **Driver**: aiosqlite
- **Pattern**: Repository Pattern com Services

## Arquivos Core

### Conexão e Configuração

| Arquivo | Responsabilidade |
|---------|-----------------|
| `backend/src/database.py` | AsyncEngine, Base ORM, gerenciamento de sessões |
| `backend/src/database_manager.py` | Multi-database por projeto, compatibilidade legacy |
| `backend/src/config/settings.py` | Configuração centralizada (database_url, paths) |

### Models (ORM)

| Arquivo | Tabela(s) | Descrição |
|---------|-----------|-----------|
| `backend/src/models/card.py` | `cards` | Cards do Kanban com workflow SDLC |
| `backend/src/models/execution.py` | `executions`, `execution_logs` | Execuções e logs de comandos |
| `backend/src/models/activity_log.py` | `activity_logs` | Auditoria de mudanças |
| `backend/src/models/metrics.py` | `project_metrics`, `execution_metrics` | Métricas de uso |
| `backend/src/models/user.py` | `users` | Autenticação |
| `backend/src/models/project.py` | `active_project` | Projeto ativo atual |
| `backend/src/models/project_history.py` | `project_history` | Histórico de projetos (DB separado) |

### Repositories (Data Access)

| Arquivo | Responsabilidade |
|---------|-----------------|
| `backend/src/repositories/card_repository.py` | CRUD de cards, validação de transições SDLC |
| `backend/src/repositories/execution_repository.py` | Persistência de execuções e logs |
| `backend/src/repositories/activity_repository.py` | Logging de atividades/auditoria |
| `backend/src/repositories/metrics_repository.py` | Armazenamento e consulta de métricas |

### Schemas (Pydantic)

| Arquivo | Descrição |
|---------|-----------|
| `backend/src/schemas/card.py` | CardCreate, CardUpdate, CardResponse, DiffStats, etc |
| `backend/src/schemas/auth.py` | Token e User schemas |

### Services

| Arquivo | Responsabilidade |
|---------|-----------------|
| `backend/src/services/migration_service.py` | Aplicação automática de migrations |
| `backend/src/services/metrics_collector.py` | Coleta de métricas de execução |
| `backend/src/services/metrics_aggregator.py` | Agregação de métricas por período |
| `backend/src/services/auto_cleanup_service.py` | Limpeza automática de cards completados |

### Migrations

| Arquivo | Mudança |
|---------|---------|
| `backend/migrations/001_add_archived_to_cards.sql` | Campo archived |
| `backend/migrations/002_add_model_config_to_cards.sql` | Campos model_* |
| `backend/migrations/003_add_execution_tables.sql` | Tabelas executions e execution_logs |
| `backend/migrations/004_add_images_to_cards.sql` | Campo images (JSON) |
| `backend/migrations/005_add_fix_card_fields.sql` | parent_card_id, is_fix_card |
| `backend/migrations/006_add_execution_workflow_fields.sql` | workflow_stage, tokens, cost |
| `backend/migrations/007_rename_inprogress_to_implement.sql` | Rename de coluna |
| `backend/migrations/008_add_diff_stats_to_cards.sql` | Campo diff_stats (JSON) |
| `backend/migrations/009_add_activity_logs_table.sql` | Tabela activity_logs |
| `backend/migrations/010_add_metrics_tables.sql` | Tabelas de métricas |
| `backend/migrations/011_add_completed_column.sql` | Campo completed_at |

### Scripts Utilitários

| Arquivo | Descrição |
|---------|-----------|
| `backend/scripts/migrate_databases.py` | Ferramenta de migração/backup de databases |

## Instâncias de Database

O sistema usa **3 databases SQLite** com propósitos distintos:

| Path | Quando é usado | Conteúdo |
|------|----------------|----------|
| `backend/auth.db` | Desenvolvimento do próprio sistema (sem load project) | cards, executions, users, metrics - histórico completo do orquestrador |
| `projeto/.claude/database.db` | Projeto externo carregado (com load project) | cards, executions, metrics isolados daquele projeto |
| `backend/.project_data/project_history.db` | Sempre (global) | Histórico de projetos acessados |

### Importante: auth.db vs database.db

- **`auth.db` e `database.db` têm tabelas IDÊNTICAS** - ambos usam a mesma `Base` do SQLAlchemy
- **`auth.db` NÃO é apenas fallback** - é o banco principal quando você está desenvolvendo o próprio orquestrador
- **`project_history.db` tem Base separada** - contém apenas a tabela `project_history`

### Qual banco é usado?

```
┌─────────────────────────────────────────────────────────┐
│  Situação                        │  Database usado      │
├──────────────────────────────────┼──────────────────────┤
│  Desenvolvendo o orquestrador    │  backend/auth.db     │
│  (sem "load project")            │                      │
├──────────────────────────────────┼──────────────────────┤
│  Projeto externo carregado       │  projeto/.claude/    │
│  (com "load project")            │  database.db         │
├──────────────────────────────────┼──────────────────────┤
│  Histórico de projetos           │  project_history.db  │
│  (sempre global)                 │                      │
└──────────────────────────────────┴──────────────────────┘
```

### Lógica de seleção (database.py)

```python
def get_session():
    try:
        return db_manager.get_current_session()  # projeto carregado
    except RuntimeError:
        return async_session_maker  # usa auth.db (sem projeto)
```

## Tabelas Principais

### cards
```
id, title, description, column_id, spec_path, model_plan, model_implement,
model_test, model_review, images (JSON), archived, created_at, updated_at,
parent_card_id, is_fix_card, test_error_context, branch_name, worktree_path,
base_branch, diff_stats (JSON), completed_at
```

### executions
```
id, card_id (FK), status (enum), command, title, started_at, completed_at,
duration, result, is_active, workflow_stage, workflow_error, input_tokens,
output_tokens, total_tokens, model_used, execution_cost
```

### execution_logs
```
id, execution_id (FK), timestamp, type (enum), content, sequence
```

### activity_logs
```
id, card_id (FK), activity_type (enum), timestamp, from_column, to_column,
old_value, new_value, user_id, description
```

### project_metrics
```
id, project_id, total_input_tokens, total_output_tokens, total_tokens,
avg_execution_time_ms, total_cost_usd, cost_by_model (JSON), cards_completed,
success_rate, metrics_date, metrics_hour, created_at, updated_at
```

### execution_metrics
```
id, execution_id (FK), card_id (FK), project_id, command, model_used,
started_at, completed_at, duration_ms, input_tokens, output_tokens, cost
```

## Enums Importantes

### ColumnId (colunas do Kanban)
```
backlog, plan, implement, test, review, done, completed, archived, cancelado
```

### ExecutionStatus
```
IDLE, RUNNING, SUCCESS, ERROR
```

### ActivityType
```
CREATED, MOVED, COMPLETED, ARCHIVED, UPDATED, EXECUTED, COMMENTED
```

### ModelType
```
claude-opus-4-5, claude-sonnet-4-5, claude-haiku-4-5, gemini-*
```

## Padrões de Código

### Criando novo Model
```python
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.src.database import Base

class NovoModel(Base):
    __tablename__ = "nova_tabela"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    # campos...
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Criando novo Repository
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class NovoRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self) -> list[Model]:
        result = await self.db.execute(select(Model))
        return result.scalars().all()
```

### Criando Migration
```sql
-- backend/migrations/NNN_descricao.sql
ALTER TABLE tabela ADD COLUMN novo_campo TEXT;
CREATE INDEX idx_tabela_campo ON tabela(campo);
```

## Dependências

- `sqlalchemy[asyncio]>=2.0`
- `aiosqlite`
- `pydantic-settings`
