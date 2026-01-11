---
description: Consultar e analisar dados do banco de dados
---

# Database Query

Sub-comando para consultas e analise de dados.

## Arquivos Relevantes

- `backend/src/repositories/*.py` - Metodos de consulta existentes
- `backend/src/database.py` - Sessao e conexao
- `backend/src/models/*.py` - Estrutura das tabelas

## Tipos de Consulta

### 1. Consultas Existentes

Use os repositorios ja implementados:

```python
# Cards
CardRepository(db).get_all()
CardRepository(db).get_by_id(card_id)

# Execucoes
ExecutionRepository(db).get_by_id(execution_id)
ExecutionRepository(db).get_logs(execution_id)

# Atividades
ActivityRepository(db).get_recent_activities(limit=50)

# Metricas
MetricsRepository(db).get_project_metrics(project_id, period="7d")
MetricsRepository(db).get_token_usage(granularity="day")
```

### 2. Queries Customizadas

Para consultas nao cobertas pelos repositorios:

```python
from sqlalchemy import select, func
from backend.src.models.card import Card

# Exemplo: contar cards por coluna
async def count_by_column(db: AsyncSession):
    result = await db.execute(
        select(Card.column_id, func.count(Card.id))
        .group_by(Card.column_id)
    )
    return result.all()
```

### 3. Consultas Diretas (Debug)

Para debug, use sqlite3 diretamente:

```bash
# Database principal
sqlite3 backend/auth.db ".tables"
sqlite3 backend/auth.db "SELECT * FROM cards LIMIT 5"

# Database de projeto
sqlite3 .claude/database.db ".schema cards"
```

## Instrucoes

Ao receber solicitacao de consulta:

1. Verifique se ja existe metodo no repository
2. Se nao existir, crie query usando SQLAlchemy select()
3. Para debug rapido, sugira comando sqlite3
4. Sempre use async/await com AsyncSession

$ARGUMENTS
