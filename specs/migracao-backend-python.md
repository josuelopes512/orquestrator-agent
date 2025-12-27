# Migração do Backend para Python com FastAPI

## Resumo
Migrar o backend de TypeScript/Express para Python/FastAPI, usando a biblioteca `claude-agent-sdk` em Python. Todas as funcionalidades existentes devem ser mantidas.

## Análise do Backend Atual (TypeScript)

### Estrutura
- `backend/src/index.ts` - Servidor Express
- `backend/src/agent.ts` - Lógica do agente Claude

### Endpoints
1. `GET /health` - Health check
2. `GET /api/logs/:cardId` - Obter logs de um card específico
3. `GET /api/executions` - Obter todas as execuções
4. `POST /api/execute-plan` - Executar um plano

### Modelos de Dados
```typescript
interface ExecutionLog {
  timestamp: string;
  type: "info" | "tool" | "text" | "error" | "result";
  content: string;
}

interface ExecutionRecord {
  cardId: string;
  startedAt: string;
  completedAt?: string;
  status: "running" | "success" | "error";
  logs: ExecutionLog[];
  result?: string;
}
```

### Funcionalidades
- Armazena execuções em memória (Map)
- Executa Claude CLI via spawn com `--output-format stream-json`
- Processa saída JSON streaming
- Registra logs em tempo real

---

## Plano de Implementação

### Fase 1: Estrutura do Projeto Python
- [x] Criar estrutura de diretórios `backend-python/`
- [x] Criar `pyproject.toml` com dependências
- [x] Criar `requirements.txt` como alternativa

### Fase 2: Modelos de Dados (Pydantic)
- [x] Criar `models.py` com modelos Pydantic equivalentes
  - ExecutionLog
  - ExecutionRecord
  - PlanResult
  - ExecutePlanRequest (para validação do body)

### Fase 3: Módulo do Agente
- [x] Criar `agent.py` com lógica do agente
  - Armazenamento em memória (dict)
  - Função `execute_plan()` usando claude-agent-sdk
  - Funções `get_execution()` e `get_all_executions()`
  - Processamento de mensagens do SDK

### Fase 4: API FastAPI
- [x] Criar `main.py` com endpoints FastAPI
  - GET /health
  - GET /api/logs/{card_id}
  - GET /api/executions
  - POST /api/execute-plan
- [x] Configurar CORS
- [x] Configurar tratamento de erros

### Fase 5: Testes e Validação
- [x] Testar health check
- [x] Testar execução de plano
- [x] Testar obtenção de logs
- [x] Verificar compatibilidade com frontend

---

## Estrutura Final

```
backend-python/
├── pyproject.toml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── main.py          # FastAPI app
│   ├── agent.py         # Lógica do agente Claude
│   └── models.py        # Modelos Pydantic
└── README.md
```

## Dependências Python

```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
claude-agent-sdk>=0.1.0
pydantic>=2.0.0
```

## Mapeamento de Funcionalidades

| TypeScript | Python |
|------------|--------|
| Express | FastAPI |
| cors middleware | fastapi.middleware.cors |
| spawn('claude') | claude-agent-sdk query() |
| Map<string, ExecutionRecord> | dict[str, ExecutionRecord] |
| interface | Pydantic BaseModel |
| async/await | async/await |

## Notas de Implementação

1. **claude-agent-sdk**: Usar a função `query()` com `ClaudeAgentOptions` para executar prompts
2. **Streaming**: O SDK já retorna mensagens em streaming via async generator
3. **Working Directory**: Configurar via `cwd` nas opções do agente
4. **Logs**: Processar `AssistantMessage`, `TextBlock`, `ToolUseBlock` e `ResultMessage`
