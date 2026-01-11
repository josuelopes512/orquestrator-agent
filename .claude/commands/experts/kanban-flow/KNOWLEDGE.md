# Kanban Flow Expert - Knowledge Base

## Dominio

Expert em fluxo do Kanban: workflow de cards, transicoes de status, automacoes SDLC, ciclo de vida e regras de negocio.

## Arquivos Core

### Frontend - Componentes UI

| Path | Responsabilidade |
|------|------------------|
| `frontend/src/components/Board/Board.tsx` | Board principal com drag-drop |
| `frontend/src/components/Column/Column.tsx` | Coluna com droppable zone |
| `frontend/src/components/Card/Card.tsx` | Card draggable com status |
| `frontend/src/pages/KanbanPage.tsx` | Page container com DndContext |

### Frontend - Hooks de Automacao

| Path | Responsabilidade |
|------|------------------|
| `frontend/src/hooks/useWorkflowAutomation.ts` | **CORE**: Automacao SDLC, transicoes, recovery |
| `frontend/src/hooks/useAgentExecution.ts` | Polling de execucoes, callbacks |

### Frontend - API e Types

| Path | Responsabilidade |
|------|------------------|
| `frontend/src/api/cards.ts` | Cliente API: moveCard, updateWorkflowState |
| `frontend/src/types/index.ts` | **CORE**: Card, Column, ALLOWED_TRANSITIONS |

### Backend - Models

| Path | Responsabilidade |
|------|------------------|
| `backend/src/models/card.py` | **CORE**: Model Card com todos campos |
| `backend/src/models/activity_log.py` | Rastreamento de mudancas |
| `backend/src/models/execution.py` | Execucoes de cards |

### Backend - Schemas e Validacao

| Path | Responsabilidade |
|------|------------------|
| `backend/src/schemas/card.py` | **CORE**: CardMove, validacao SDLC |

### Backend - Repository

| Path | Responsabilidade |
|------|------------------|
| `backend/src/repositories/card_repository.py` | **CORE**: CRUD + SDLC validation |
| `backend/src/repositories/activity_repository.py` | Log de atividades |

### Backend - Routes

| Path | Responsabilidade |
|------|------------------|
| `backend/src/routes/cards.py` | Endpoints CRUD + move com validacao |
| `backend/src/routes/activities.py` | Endpoints de atividades |

### Backend - Services

| Path | Responsabilidade |
|------|------------------|
| `backend/src/services/auto_cleanup_service.py` | **CORE**: Move done -> completed |
| `backend/src/services/diff_analyzer.py` | Analise de diffs |

## Colunas do Kanban (SDLC)

```
backlog -> plan -> implement -> test -> review -> done -> completed -> archived
                                                    |
                                                    v
                                               cancelado (terminal)
```

## Transicoes Permitidas

```python
ALLOWED_TRANSITIONS = {
    "backlog": ["plan", "cancelado"],
    "plan": ["implement", "cancelado"],
    "implement": ["test", "cancelado"],
    "test": ["review", "cancelado"],
    "review": ["done", "cancelado"],
    "done": ["completed", "archived", "cancelado"],
    "completed": ["archived"],
    "archived": ["done"],
    "cancelado": [],  # Terminal
}
```

## Workflow Stages

```
idle -> planning -> implementing -> testing -> reviewing -> completed | error
```

## Regras de Negocio

1. **Novo card sempre em backlog** - Forcado no create
2. **Workflow e linear** - Nao pode pular etapas
3. **Card em execucao e read-only** - Disabled draggable
4. **Execucoes preservadas em done** - Historico acessivel
5. **Auto-cleanup apos 30min** - done -> completed
6. **Fix cards automaticos** - Criados em falha de teste

## Specs Relacionadas

- `specs/kanban-board.md`
- `specs/auto-fix-workflow-complete.md`
- `specs/workflow-recovery-after-refresh.md`
- `specs/bloquear-arrasto-cards-nao-finalizados.md`
- `specs/auto-limpeza-cards-done.md`

## Ultima Atualizacao

2026-01-10
