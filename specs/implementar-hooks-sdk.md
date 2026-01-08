# Plano: Implementar Hooks do Claude Agent SDK

## Objetivo

Adicionar sistema de hooks para:
1. **Token Stats** - Capturar e exibir uso de tokens por card em tempo real
2. **Notificações** - Notificar frontend via WebSocket quando execução termina
3. **Auto-retry** - Re-executar automaticamente em caso de falhas transientes (conexão/timeout)

---

## Estado Atual

| Componente | Status |
|------------|--------|
| Campos de token no DB | **IMPLEMENTADO** - `input_tokens`, `output_tokens`, `total_tokens`, `model_used` |
| `update_token_usage()` no repository | **IMPLEMENTADO** - metodos adicionados |
| Captura de `ResultMessage.usage` | **IMPLEMENTADO** - nas 4 funcoes execute_* |
| WebSocket para execucao | **IMPLEMENTADO** - `/api/execution/ws/{card_id}` |
| Frontend TokenStats | **IMPLEMENTADO** - hook e exibicao no Card |

---

## Arquivos a Modificar

### Backend

| Arquivo | Ação |
|---------|------|
| `backend/src/models/execution.py` | Adicionar campos `input_tokens`, `output_tokens`, `total_tokens`, `model_used` |
| `backend/src/repositories/execution_repository.py` | Adicionar `update_token_usage()` e `get_token_stats_for_card()` |
| `backend/src/agent.py` | Capturar `ResultMessage.usage` nas 4 funções + integrar WebSocket |
| `backend/src/services/execution_ws.py` | **NOVO** - WebSocket manager para notificações |
| `backend/src/routes/execution_ws.py` | **NOVO** - Endpoint WebSocket `/api/execution/ws/{card_id}` |
| `backend/src/main.py` | Registrar nova rota WebSocket |
| `backend/src/routes/cards.py` | Incluir `tokenStats` na resposta de cards |
| `backend/src/schemas/card.py` | Adicionar schema `TokenStats` |

### Frontend

| Arquivo | Ação |
|---------|------|
| `frontend/src/types/index.ts` | Adicionar interface `TokenStats` |
| `frontend/src/hooks/useExecutionWebSocket.ts` | **NOVO** - Hook para conectar ao WebSocket |
| `frontend/src/hooks/useToast.ts` | **NOVO** - Sistema de notificações toast |
| `frontend/src/components/Toast/Toast.tsx` | **NOVO** - Componente de toast |
| `frontend/src/components/Card/Card.tsx` | Exibir `tokenStats` no card |
| `frontend/src/App.tsx` | Integrar toasts e WebSocket |

---

## Implementação Detalhada

### Fase 1: Database Schema (Backend)

**`backend/src/models/execution.py`** - Adicionar após linha 30:

```python
# Campos para token tracking
input_tokens = Column(Integer, nullable=True)
output_tokens = Column(Integer, nullable=True)
total_tokens = Column(Integer, nullable=True)
model_used = Column(String, nullable=True)
```

**`backend/src/repositories/execution_repository.py`** - Adicionar métodos:

```python
async def update_token_usage(
    self,
    execution_id: str,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    model_used: str = None
):
    """Atualiza token usage de uma execução"""
    values = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }
    if model_used:
        values["model_used"] = model_used

    await self.db.execute(
        update(Execution)
        .where(Execution.id == execution_id)
        .values(**values)
    )
    await self.db.commit()

async def get_token_stats_for_card(self, card_id: str) -> dict:
    """Retorna estatísticas agregadas de tokens para um card"""
    from sqlalchemy import func

    result = await self.db.execute(
        select(
            func.sum(Execution.input_tokens).label('total_input'),
            func.sum(Execution.output_tokens).label('total_output'),
            func.sum(Execution.total_tokens).label('total_tokens'),
            func.count(Execution.id).label('execution_count')
        ).where(Execution.card_id == card_id)
    )
    row = result.first()

    return {
        "inputTokens": row.total_input or 0,
        "outputTokens": row.total_output or 0,
        "totalTokens": row.total_tokens or 0,
        "executionCount": row.execution_count or 0
    }
```

---

### Fase 2: WebSocket Manager (Backend)

**`backend/src/services/execution_ws.py`** (NOVO):

```python
"""WebSocket manager para notificações de execução em tempo real"""
from typing import Dict, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime


class ExecutionWebSocketManager:
    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, card_id: str, websocket: WebSocket):
        await websocket.accept()
        if card_id not in self.connections:
            self.connections[card_id] = set()
        self.connections[card_id].add(websocket)

    def disconnect(self, card_id: str, websocket: WebSocket):
        if card_id in self.connections:
            self.connections[card_id].discard(websocket)

    async def broadcast(self, card_id: str, message: dict):
        if card_id not in self.connections:
            return

        dead = set()
        for ws in self.connections[card_id]:
            try:
                await ws.send_text(json.dumps(message))
            except:
                dead.add(ws)

        for ws in dead:
            self.connections[card_id].discard(ws)

    async def notify_complete(self, card_id: str, status: str, command: str,
                              token_stats: dict = None, error: str = None):
        await self.broadcast(card_id, {
            "type": "execution_complete",
            "cardId": card_id,
            "status": status,
            "command": command,
            "tokenStats": token_stats,
            "error": error,
            "timestamp": datetime.now().isoformat()
        })

    async def notify_log(self, card_id: str, log_type: str, content: str):
        await self.broadcast(card_id, {
            "type": "log",
            "cardId": card_id,
            "logType": log_type,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })


execution_ws_manager = ExecutionWebSocketManager()
```

**`backend/src/routes/execution_ws.py`** (NOVO):

```python
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..services.execution_ws import execution_ws_manager

router = APIRouter(tags=["execution"])

@router.websocket("/api/execution/ws/{card_id}")
async def execution_websocket(websocket: WebSocket, card_id: str):
    await execution_ws_manager.connect(card_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        execution_ws_manager.disconnect(card_id, websocket)
```

---

### Fase 3: Capturar Token Usage no agent.py

Modificar as 4 funções (`execute_plan`, `execute_implement`, `execute_test_implementation`, `execute_review`) para:

1. **Importar o WebSocket manager**:
```python
from .services.execution_ws import execution_ws_manager
```

2. **Capturar token usage no ResultMessage** (em cada função, após processar ResultMessage):
```python
elif isinstance(message, ResultMessage):
    if hasattr(message, "result") and message.result:
        result_text = message.result
        add_log(record, LogType.RESULT, message.result)

    # NOVO: Capturar token usage
    if hasattr(message, 'usage') and message.usage:
        usage = message.usage
        token_stats = {
            "input_tokens": getattr(usage, 'input_tokens', 0),
            "output_tokens": getattr(usage, 'output_tokens', 0),
            "total_tokens": getattr(usage, 'input_tokens', 0) + getattr(usage, 'output_tokens', 0),
        }

        add_log(record, LogType.INFO,
            f"Token usage - Input: {token_stats['input_tokens']}, "
            f"Output: {token_stats['output_tokens']}, "
            f"Total: {token_stats['total_tokens']}")

        if repo and execution_db:
            await repo.update_token_usage(
                execution_id=execution_db.id,
                input_tokens=token_stats["input_tokens"],
                output_tokens=token_stats["output_tokens"],
                total_tokens=token_stats["total_tokens"],
                model_used=model
            )
```

3. **Notificar via WebSocket ao completar** (antes do return):
```python
# NOVO: Notificar via WebSocket
await execution_ws_manager.notify_complete(
    card_id=card_id,
    status="success",  # ou "error"
    command="/plan",   # ou /implement, /test-implementation, /review
    token_stats=token_stats if token_stats.get("total_tokens", 0) > 0 else None
)
```

---

### Fase 4: Auto-Retry (Backend)

Criar wrapper de retry no `agent.py`:

```python
async def execute_with_retry(
    execute_fn,
    card_id: str,
    max_retries: int = 3,
    retry_delay: float = 2.0
) -> PlanResult:
    """Executa função com retry automático em erros transientes"""
    last_error = None

    for attempt in range(max_retries):
        try:
            result = await execute_fn()

            if result.success:
                return result

            # Só retry em erros de conexão/timeout
            if result.error and not _is_retryable(result.error):
                return result

            last_error = result.error

        except Exception as e:
            last_error = str(e)
            if not _is_retryable(str(e)):
                raise

        if attempt < max_retries - 1:
            delay = retry_delay * (2 ** attempt)
            print(f"[{card_id[:8]}] Retry {attempt + 1}/{max_retries} em {delay:.1f}s...")
            await asyncio.sleep(delay)

    return PlanResult(
        success=False,
        error=f"Falhou após {max_retries} tentativas: {last_error}",
        logs=[]
    )

def _is_retryable(error: str) -> bool:
    """Verifica se erro é transiente e pode ser retentado"""
    retryable = ["connection", "timeout", "rate limit", "overloaded", "503", "502"]
    return any(r in error.lower() for r in retryable)
```

---

### Fase 5: Frontend - Types e WebSocket Hook

**`frontend/src/types/index.ts`** - Adicionar:

```typescript
export interface TokenStats {
  inputTokens: number;
  outputTokens: number;
  totalTokens: number;
  executionCount: number;
}

// Atualizar Card interface
export interface Card {
  // ... campos existentes ...
  tokenStats?: TokenStats;
}
```

**`frontend/src/hooks/useExecutionWebSocket.ts`** (NOVO):

```typescript
import { useEffect, useRef, useCallback, useState } from 'react';

interface ExecutionCompleteMessage {
  type: 'execution_complete';
  cardId: string;
  status: 'success' | 'error';
  command: string;
  tokenStats?: { input_tokens: number; output_tokens: number; total_tokens: number };
  error?: string;
}

export function useExecutionWebSocket(
  cardId: string | null,
  onComplete?: (msg: ExecutionCompleteMessage) => void
) {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!cardId) return;

    const ws = new WebSocket(`ws://localhost:3001/api/execution/ws/${cardId}`);

    ws.onopen = () => setIsConnected(true);
    ws.onclose = () => setIsConnected(false);
    ws.onmessage = (e) => {
      const msg = JSON.parse(e.data);
      if (msg.type === 'execution_complete' && onComplete) {
        onComplete(msg);
      }
    };

    wsRef.current = ws;
    return () => ws.close();
  }, [cardId, onComplete]);

  return { isConnected };
}
```

---

### Fase 6: Frontend - Toast e Exibição

**`frontend/src/hooks/useToast.ts`** (NOVO):

```typescript
import { useState, useCallback } from 'react';

export interface Toast {
  id: string;
  type: 'success' | 'error' | 'info';
  title: string;
  message?: string;
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Date.now().toString();
    setToasts(prev => [...prev, { ...toast, id }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 5000);
  }, []);

  return { toasts, addToast };
}
```

**`frontend/src/components/Card/Card.tsx`** - Adicionar exibição de tokens:

```tsx
{card.tokenStats && card.tokenStats.totalTokens > 0 && (
  <div className={styles.tokenStats}>
    <span className={styles.tokenIcon}>🪙</span>
    <span>{card.tokenStats.totalTokens.toLocaleString()} tokens</span>
  </div>
)}
```

---

## Ordem de Implementacao

```
1. [x] Fase 1: Database (model + repository)
   └─ Campos de token adicionados ao model Execution
   └─ Metodos update_token_usage e get_token_stats_for_card implementados

2. [x] Fase 2: WebSocket Manager
   └─ services/execution_ws.py criado
   └─ routes/execution_ws.py criado
   └─ Rota registrada no main.py

3. [x] Fase 3: Token Capture no agent.py
   └─ Captura de ResultMessage.usage nas 4 funcoes execute_*
   └─ Notificacao via WebSocket ao completar

4. [x] Fase 4: Auto-Retry
   └─ Wrapper execute_with_retry implementado
   └─ Funcao _is_retryable para detectar erros transientes

5. [x] Fase 5: Frontend Types e Hooks
   └─ Interface TokenStats adicionada em types/index.ts
   └─ Campo tokenStats adicionado a interface Card
   └─ Hook useExecutionWebSocket criado
   └─ Hook useToast criado

6. [x] Fase 6: Frontend UI
   └─ Exibicao de TokenStats no componente Card
   └─ CSS para tokenStats adicionado
```

---

## Compatibilidade

- **Polling continua funcionando** - WebSocket é adicional
- **Campos de token são nullable** - Não quebra dados existentes
- **Auto-retry é transparente** - Mesmo retorno `PlanResult`

---

## Arquivos Críticos

- `backend/src/agent.py` (linhas 1150-2184) - 4 funções execute
- `backend/src/models/execution.py` - Adicionar campos
- `backend/src/repositories/execution_repository.py` - Adicionar métodos
- `backend/src/routes/chat.py` - Referência para padrão WebSocket
- `frontend/src/hooks/useAgentExecution.ts` - Referência para polling atual
- `frontend/src/components/Card/Card.tsx` - Onde exibir tokens
