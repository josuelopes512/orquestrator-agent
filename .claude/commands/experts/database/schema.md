---
description: Analisar e modificar schema do banco de dados
---

# Database Schema

Sub-comando para analise e modificacao de schema.

## Estrutura Atual

### Tabelas Principais

```
cards              - Cards do Kanban SDLC
executions         - Execucoes de comandos
execution_logs     - Logs de execucao
activity_logs      - Auditoria de atividades
project_metrics    - Metricas agregadas
execution_metrics  - Metricas por execucao
users              - Autenticacao
active_project     - Projeto atual
project_history    - Historico (DB separado)
applied_migrations - Rastreamento de migrations
```

### Relacionamentos

```
cards 1:N executions (card_id FK)
cards 1:N activity_logs (card_id FK CASCADE)
cards 1:N cards (parent_card_id - auto-referencial)
executions 1:N execution_logs (execution_id FK)
executions 1:1 execution_metrics (execution_id FK)
```

## Criando Novo Model

### Template Base

```python
# backend/src/models/novo_model.py
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.src.database import Base

class NovoModel(Base):
    __tablename__ = "nova_tabela"

    # Primary Key
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Campos
    titulo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)

    # Foreign Key (se necessario)
    card_id = Column(String, ForeignKey("cards.id", ondelete="CASCADE"))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    card = relationship("Card", back_populates="novos_models")
```

### Registrar no __init__.py

```python
# backend/src/models/__init__.py
from .novo_model import NovoModel
```

### Criar Migration

```sql
-- backend/migrations/NNN_create_nova_tabela.sql
CREATE TABLE IF NOT EXISTS nova_tabela (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    descricao TEXT,
    ativo INTEGER DEFAULT 1,
    card_id TEXT REFERENCES cards(id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_nova_tabela_card ON nova_tabela(card_id);
```

## Adicionando Campo a Tabela Existente

### 1. Migration SQL

```sql
-- backend/migrations/NNN_add_campo_to_tabela.sql
ALTER TABLE tabela ADD COLUMN novo_campo TEXT;
```

### 2. Atualizar Model

```python
# Adicionar no model existente
novo_campo = Column(String, nullable=True)
```

### 3. Atualizar Schema (se API)

```python
# backend/src/schemas/tabela.py
class TabelaResponse(BaseModel):
    novo_campo: str | None = None
```

## Tipos de Dados SQLite/SQLAlchemy

| SQLite | SQLAlchemy | Python |
|--------|------------|--------|
| TEXT | String/Text | str |
| INTEGER | Integer | int |
| REAL | Float | float |
| BLOB | LargeBinary | bytes |
| DATETIME | DateTime | datetime |
| JSON | JSON | dict/list |
| BOOLEAN (0/1) | Boolean | bool |

## Indices

```sql
-- Indice simples
CREATE INDEX idx_tabela_campo ON tabela(campo);

-- Indice composto
CREATE INDEX idx_tabela_campos ON tabela(campo1, campo2);

-- Indice unico
CREATE UNIQUE INDEX idx_tabela_email ON tabela(email);
```

## Instrucoes

Ao receber solicitacao de schema:

1. Analise a estrutura atual em KNOWLEDGE.md
2. Verifique relacionamentos existentes
3. Siga os padroes de nomenclatura (snake_case)
4. Crie migration + model + schema juntos
5. Documente relacionamentos

$ARGUMENTS
