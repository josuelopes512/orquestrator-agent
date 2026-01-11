---
allowed-tools: Read, Glob, Grep, Edit, Write
description: Debugar e modificar automacoes de workflow
---

# Kanban Flow - Automation

Expert em automacoes de workflow do Kanban SDLC.

## Dominio

- useWorkflowAutomation hook
- Workflow stages (idle -> completed)
- Rollback em caso de erro
- Recovery apos refresh
- Execucao de comandos /plan, /implement, /test, /review

## Arquivos Principais

### Frontend - Automacao
- `frontend/src/hooks/useWorkflowAutomation.ts` - **CORE**: Toda logica de automacao
- `frontend/src/hooks/useAgentExecution.ts` - Polling e callbacks

### Frontend - API
- `frontend/src/api/cards.ts` - updateWorkflowState, fetchLogs

### Frontend - Types
- `frontend/src/types/index.ts` - WorkflowStage, WorkflowStatus

## Workflow Stages

```
idle
  |
  v (runWorkflow iniciado)
planning -> [erro] -> idle (rollback)
  |
  v (plan completo)
implementing -> [erro] -> planning (rollback)
  |
  v (implement completo)
testing -> [erro] -> implementing (rollback)
  |
  v (test completo)
reviewing -> [erro] -> testing (rollback)
  |
  v (review completo)
completed
```

## Fluxo de Automacao

```javascript
// Em useWorkflowAutomation.ts
runWorkflow(card) {
  1. Move para plan, stage='planning'
  2. Executa /plan
  3. Se sucesso: move para implement, stage='implementing'
  4. Se erro: rollback para backlog

  // Continua para cada etapa...
}
```

## Recovery Apos Refresh

1. App carrega `initialStatuses` da API
2. Hook sincroniza `workflowStatuses`
3. Se execution ainda running:
   - Registra callback para quando completar
   - Continua de onde parou
4. Se execution ja completou:
   - NAO continua automaticamente
   - Card fica na coluna certa

## Rollback Logic

```javascript
// Se etapa falhar
rollbackColumn = STAGE_TO_PREVIOUS_COLUMN[currentStage]
moveCard(card.id, rollbackColumn)
updateWorkflowState({ stage: 'error', error: message })
```

## Instrucoes

### 1. Debugar workflow parado
```
1. Verificar workflowStatus.stage atual
2. Verificar activeExecution.status
3. Verificar se ha erro em workflowStatus.error
4. Verificar polling em useAgentExecution
```

### 2. Debugar recovery nao funcionando
```
1. Verificar initialStatuses da API
2. Verificar sincronizacao no hook
3. Verificar se callback foi registrado
```

### 3. Adicionar nova etapa no workflow
```
1. Adicionar coluna em COLUMNS (types/index.ts)
2. Atualizar ALLOWED_TRANSITIONS
3. Adicionar stage em WorkflowStage
4. Atualizar runWorkflow no hook
5. Criar comando correspondente (/nova-etapa)
```

### 4. Modificar comportamento de rollback
```
1. Editar logica em useWorkflowAutomation.ts
2. Verificar STAGE_TO_PREVIOUS_COLUMN mapping
3. Testar cenarios de erro
```

## Integracao com Comandos

- `/plan` - Executa na etapa planning
- `/implement` - Executa na etapa implementing
- `/test-implementation` - Executa na etapa testing
- `/review` - Executa na etapa reviewing

## Argumentos

$ARGUMENTS
