---
description: Criar e gerenciar migrations de banco de dados
---

# Database Migrate

Sub-comando para gerenciamento de migrations SQL.

## Sistema de Migrations

- **Localizacao**: `backend/migrations/`
- **Formato**: `NNN_descricao.sql` (ex: `012_add_new_field.sql`)
- **Rastreamento**: Tabela `applied_migrations` no banco
- **Service**: `backend/src/services/migration_service.py`

## Migrations Existentes

| # | Arquivo | Descricao |
|---|---------|-----------|
| 001 | add_archived_to_cards | Campo archived |
| 002 | add_model_config_to_cards | Campos model_* |
| 003 | add_execution_tables | Tabelas executions/logs |
| 004 | add_images_to_cards | Campo images JSON |
| 005 | add_fix_card_fields | parent_card_id, is_fix_card |
| 006 | add_execution_workflow_fields | workflow, tokens, cost |
| 007 | rename_inprogress_to_implement | Rename coluna |
| 008 | add_diff_stats_to_cards | Campo diff_stats JSON |
| 009 | add_activity_logs_table | Tabela activity_logs |
| 010 | add_metrics_tables | Tabelas de metricas |
| 011 | add_completed_column | Campo completed_at |

## Criando Nova Migration

### Passo 1: Determinar Proximo Numero

```bash
ls backend/migrations/*.sql | tail -1
# Resultado: 011_add_completed_column.sql
# Proximo: 012
```

### Passo 2: Criar Arquivo SQL

```sql
-- backend/migrations/012_descricao_da_mudanca.sql

-- Adicionar coluna
ALTER TABLE tabela ADD COLUMN novo_campo TEXT;

-- Criar indice (se necessario)
CREATE INDEX IF NOT EXISTS idx_tabela_campo ON tabela(campo);

-- Atualizar dados existentes (se necessario)
UPDATE tabela SET novo_campo = 'valor_default' WHERE novo_campo IS NULL;
```

### Passo 3: Atualizar Model

Adicione o campo correspondente no model SQLAlchemy:

```python
# backend/src/models/tabela.py
novo_campo = Column(String, nullable=True)
```

### Passo 4: Atualizar Schema (se exposto na API)

```python
# backend/src/schemas/tabela.py
novo_campo: str | None = None
```

## Verificar Migrations Pendentes

```python
from backend.src.services.migration_service import MigrationService

service = MigrationService(db_path="backend/auth.db")
pending = await service.get_pending_migrations()
```

## Aplicar Migrations

As migrations sao aplicadas automaticamente na inicializacao.
Para aplicar manualmente:

```python
await service.apply_migration("012_nova_migration.sql")
```

## Boas Praticas

1. **Nunca altere migrations ja aplicadas** - crie nova migration
2. **Use IF NOT EXISTS** para indices e tabelas
3. **Sempre adicione campos como nullable** ou com default
4. **Teste em banco local antes** de commitar

## Instrucoes

Ao receber solicitacao de migration:

1. Identifique a mudanca necessaria
2. Determine o proximo numero sequencial
3. Crie o arquivo SQL seguindo o padrao
4. Atualize model e schema correspondentes
5. Documente a mudanca

$ARGUMENTS
