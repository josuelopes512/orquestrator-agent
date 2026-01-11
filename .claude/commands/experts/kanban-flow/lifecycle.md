---
allowed-tools: Read, Glob, Grep, Edit, Write
description: Analisar ciclo de vida de cards no Kanban
---

# Kanban Flow - Lifecycle

Expert no ciclo de vida dos cards no Kanban.

## Dominio

- Estados do card (colunas)
- Campos temporais (created_at, completed_at)
- Auto-cleanup service
- Fix cards e parent relationships
- Finalizacao de cards

## Arquivos Principais

### Models e Schemas
- `backend/src/models/card.py` - Todos os campos do card
- `backend/src/schemas/card.py` - is_finalized, DiffStats, etc

### Services
- `backend/src/services/auto_cleanup_service.py` - Move done -> completed

### Repository
- `backend/src/repositories/card_repository.py` - create, move, create_fix_card

### Activity Tracking
- `backend/src/models/activity_log.py` - ActivityType enum
- `backend/src/repositories/activity_repository.py` - log_activity

## Estados do Card

| Estado | Descricao | Finalizado? |
|--------|-----------|-------------|
| backlog | Aguardando execucao | Nao |
| plan | Planejamento em andamento | Nao |
| implement | Implementacao em andamento | Nao |
| test | Testes em andamento | Nao |
| review | Review em andamento | Nao |
| done | Workflow completado | Sim |
| completed | Limpo pelo auto-cleanup | Sim |
| archived | Arquivado | Sim |
| cancelado | Cancelado | Sim |

## Campos Temporais

- `created_at`: Quando criado
- `updated_at`: Ultima modificacao
- `completed_at`: Quando moveu para "done" (usado pelo auto-cleanup)

## Auto-Cleanup Logic

```python
# Em auto_cleanup_service.py
cleanup_after_minutes = 30  # Default

# Cards em "done" com completed_at > 30min
# sao movidos para "completed" automaticamente
```

## Fix Cards

Criados automaticamente quando teste falha:
- `parent_card_id`: Referencia ao card original
- `is_fix_card`: True
- `test_error_context`: Stack trace do erro

## Instrucoes

### 1. Entender ciclo de vida
```
Ler card.py para campos
Ler auto_cleanup_service.py para timings
Explicar fluxo completo
```

### 2. Debugar card preso
```
Verificar column_id atual
Verificar completed_at (se em done)
Verificar se auto-cleanup esta rodando
```

### 3. Modificar ciclo de vida
```
Avaliar impacto em:
- Model (card.py)
- Schema (card.py)
- Repository (card_repository.py)
- Auto-cleanup (auto_cleanup_service.py)
```

## Argumentos

$ARGUMENTS
