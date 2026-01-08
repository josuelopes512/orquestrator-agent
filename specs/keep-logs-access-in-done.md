## 1. Resumo

Corrigir a perda de acesso aos logs quando um card vai para a coluna "done". Atualmente, quando um card é movido para "done", o botão "View Logs" desaparece porque o estado de execução é limpo, impedindo que o usuário visualize o histórico de execução do card.

---

## 2. Objetivos e Escopo

### Objetivos
- [x] Manter o botão "View Logs" visível em cards na coluna "done"
- [x] Preservar o estado de execução quando o card é movido para "done"
- [x] Permitir acesso ao histórico completo de logs dos cards concluídos
- [x] Garantir que o estado de execução seja persistido e recuperável

### Fora do Escopo
- Modificação da estrutura de armazenamento de logs no backend
- Alteração do comportamento de cards em outras colunas
- Mudanças na interface do modal de logs

---

## 3. Implementação

### Arquivos a Serem Modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `frontend/src/components/Card/Card.tsx` | Modificar | Adicionar lógica para buscar histórico de logs quando não há executionStatus ativo |
| `frontend/src/hooks/useWorkflowAutomation.ts` | Modificar | Não limpar o estado de execução ao mover para "done" |
| `frontend/src/App.tsx` | Modificar | Preservar execution status para cards em "done" |
| `backend/src/repositories/card_repository.py` | Modificar | Garantir que activeExecution persista em cards "done" |

### Detalhes Técnicos

#### 1. Modificar Card.tsx para buscar logs de cards em "done"

```typescript
// Em Card.tsx, linha ~57
const hasLogs = executionStatus && executionStatus.logs && executionStatus.logs.length > 0;

// Adicionar verificação para cards em done sem executionStatus ativo
const [hasHistoricalLogs, setHasHistoricalLogs] = useState(false);

useEffect(() => {
  // Se o card está em done e não tem executionStatus, verificar se tem logs históricos
  if (card.columnId === 'done' && !executionStatus && fetchLogsHistory) {
    fetchLogsHistory(card.id).then(history => {
      if (history && history.history.length > 0) {
        setHasHistoricalLogs(true);
        setLogsHistory(history.history);
      }
    });
  }
}, [card.columnId, card.id, executionStatus, fetchLogsHistory]);

// Atualizar condição para mostrar botão de logs
const shouldShowLogs = hasLogs || (card.columnId === 'done' && hasHistoricalLogs);
```

#### 2. Modificar useWorkflowAutomation para preservar execução em done

```typescript
// Em useWorkflowAutomation.ts
// NÃO limpar o estado quando mover para done
const handleStageCompletion = (cardId: string, stage: WorkflowStage) => {
  // ... código existente ...

  if (stage === 'reviewing' && result.success) {
    // Mover para done mas MANTER o estado de execução
    onCardMove(cardId, 'done');
    setWorkflowStatuses(prev => {
      const next = new Map(prev);
      const current = next.get(cardId);
      if (current) {
        next.set(cardId, { ...current, stage: 'completed' });
      }
      return next;
    });
    // NÃO chamar clearWorkflowStatus aqui
  }
};
```

#### 3. Modificar App.tsx para manter execução de cards em done

```typescript
// Em App.tsx, no carregamento inicial
// Incluir cards em "done" ao carregar execuções

for (const card of loadedCards) {
  if (card.activeExecution) {
    // Carregar execução mesmo se o card estiver em done
    // Remover verificação que exclui cards em done
    executionsMap.set(card.id, {
      cardId: card.id,
      status: card.activeExecution.status,
      startedAt: card.activeExecution.startedAt,
      completedAt: card.activeExecution.completedAt,
      logs: [], // Logs serão carregados sob demanda
    });
  }
}
```

#### 4. Backend: Preservar activeExecution em cards done

```python
# Em card_repository.py
async def move_card(self, card_id: str, new_column_id: str):
    """Move card para nova coluna preservando execução"""
    # ... código existente ...

    # NÃO limpar activeExecution quando mover para done
    if new_column_id == "done":
        # Manter activeExecution para histórico
        pass  # Não fazer update(is_active=False)

    # ... resto do código ...
```

---

## 4. Testes

### Unitários
- [x] Testar que Card.tsx mostra botão de logs para cards em done com histórico
- [x] Verificar que fetchLogsHistory é chamado para cards em done sem executionStatus
- [x] Confirmar que logsHistory é carregado corretamente do backend

### Integração
- [x] Executar workflow completo e verificar que logs permanecem acessíveis em done
- [x] Testar reload da página com cards em done e confirmar acesso aos logs
- [x] Verificar que múltiplas execuções aparecem no histórico de logs

---

## 5. Considerações

- **Performance:** Carregar histórico de logs sob demanda para cards em done evita overhead desnecessário
- **Compatibilidade:** Manter retrocompatibilidade com cards existentes que já estão em done
- **UX:** Usuário terá acesso completo ao histórico sem perder funcionalidade existente