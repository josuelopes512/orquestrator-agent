---
allowed-tools: Read, Glob, Grep, Edit
description: Sincronizar knowledge base do Kanban Flow expert
---

# Kanban Flow - Sync

Atualize o knowledge base quando o codigo mudar.

## Processo de Sync

### 1. Detectar Mudancas

Verifique se os arquivos do KNOWLEDGE.md ainda existem e se novos arquivos foram criados:

```
# Componentes UI
frontend/src/components/Board/
frontend/src/components/Column/
frontend/src/components/Card/

# Hooks
frontend/src/hooks/useWorkflow*.ts
frontend/src/hooks/useAgent*.ts

# API/Types
frontend/src/api/cards.ts
frontend/src/types/

# Models
backend/src/models/card.py
backend/src/models/activity*.py
backend/src/models/execution.py

# Repository
backend/src/repositories/card_repository.py
backend/src/repositories/activity_repository.py

# Routes
backend/src/routes/cards.py
backend/src/routes/activities.py

# Services
backend/src/services/auto_cleanup_service.py
backend/src/services/diff_analyzer.py
```

### 2. Atualizar KNOWLEDGE.md

Se encontrar:
- **Arquivos removidos**: Remover do KNOWLEDGE.md
- **Arquivos renomeados**: Atualizar paths
- **Novos arquivos relevantes**: Adicionar com descricao

### 3. Verificar Transicoes

Leia os arquivos de transicoes e verifique se ALLOWED_TRANSITIONS mudou:
- `frontend/src/types/index.ts`
- `backend/src/repositories/card_repository.py`

Se mudou, atualize a secao "Transicoes Permitidas" no KNOWLEDGE.md.

### 4. Atualizar Timestamp

Atualize "Ultima Atualizacao" no final do KNOWLEDGE.md.

## Execucao

1. Glob para encontrar arquivos atuais
2. Compare com lista no KNOWLEDGE.md
3. Leia arquivos core para verificar mudancas estruturais
4. Edite KNOWLEDGE.md com atualizacoes
5. Reporte mudancas encontradas

## Output Esperado

```
## Sync Report

### Arquivos Verificados: X
### Mudancas Encontradas: Y

#### Adicionados:
- path/novo/arquivo.ts - [descricao]

#### Removidos:
- path/antigo/arquivo.ts

#### Atualizados:
- ALLOWED_TRANSITIONS: [mudanca]

### KNOWLEDGE.md Atualizado: Sim/Nao
```
