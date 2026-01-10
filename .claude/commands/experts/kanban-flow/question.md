---
allowed-tools: Read, Glob, Grep
description: Responder perguntas sobre o fluxo do Kanban
---

# Kanban Flow - Question

Responda perguntas sobre o fluxo do Kanban focando **apenas** nos arquivos do knowledge base.

## Knowledge Base

${{./KNOWLEDGE.md}}

## Instrucoes

1. **NAO modifique arquivos** - apenas leia e responda
2. **Foque nos arquivos listados** no KNOWLEDGE.md
3. **Referencie o codigo real** com path:line_number
4. **Seja especifico** - cite trechos relevantes do codigo

## Arquivos Principais para Consultar

### Para perguntas sobre transicoes:
- `frontend/src/types/index.ts` - ALLOWED_TRANSITIONS, isValidTransition
- `backend/src/repositories/card_repository.py` - ALLOWED_TRANSITIONS, move()

### Para perguntas sobre automacao:
- `frontend/src/hooks/useWorkflowAutomation.ts` - runWorkflow, stages

### Para perguntas sobre ciclo de vida:
- `backend/src/models/card.py` - campos do card
- `backend/src/services/auto_cleanup_service.py` - cleanup logic

### Para perguntas sobre UI:
- `frontend/src/components/Board/Board.tsx`
- `frontend/src/components/Column/Column.tsx`
- `frontend/src/components/Card/Card.tsx`

## Formato de Resposta

```
## Resposta

[Explicacao clara e concisa]

### Codigo Relevante

`path/to/file.ts:123`
[trecho do codigo]

### Referencias Adicionais

- `outro/arquivo.py:45` - [descricao]
```

## Pergunta do Usuario

$ARGUMENTS
