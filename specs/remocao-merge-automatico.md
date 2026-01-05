# Remoção do Merge Automático no Pipeline

## 1. Resumo

Remover a funcionalidade de merge automático do pipeline após a conclusão da etapa de REVIEW. Atualmente, quando um card completa a revisão, o sistema tenta fazer merge da branch worktree para a branch principal. A alteração simplificará o fluxo, fazendo com que o card vá diretamente para DONE após a revisão, sem tentativa de merge ou resolução de conflitos.

---

## 2. Objetivos e Escopo

### Objetivos
- [x] Remover chamadas de merge automático após REVIEW
- [x] Simplificar transição REVIEW → DONE
- [x] Manter worktrees para isolamento (não remover a funcionalidade)
- [x] Limpar código relacionado a merge e resolução de conflitos

### Fora do Escopo
- Remoção da funcionalidade de worktrees (permanece para isolamento)
- Alteração na criação de branches
- Modificação das etapas PLAN/IMPLEMENT/TEST

---

## 3. Implementação

### Arquivos a Serem Modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `frontend/src/hooks/useWorkflowAutomation.ts` | Modificar | Remover `handleCompletedReview` e lógica de merge |
| `backend/src/main.py` | Modificar | Remover endpoints de merge (`/api/cards/{card_id}/merge`) |
| `backend/src/conflict_resolver.py` | Deletar | Arquivo não será mais necessário |
| `backend/src/git_workspace.py` | Modificar | Remover métodos de merge, manter apenas worktree |
| `backend/src/models/card.py` | Modificar | Remover campo `merge_status` |
| `frontend/src/types/index.ts` | Modificar | Remover tipos relacionados a merge |
| `frontend/src/components/BranchIndicator/*` | Modificar | Simplificar indicador removendo status de merge |

### Detalhes Técnicos

#### 3.1 Frontend - Simplificar Hook de Workflow

**Modificar `frontend/src/hooks/useWorkflowAutomation.ts`:**

```typescript
// REMOVER a função handleCompletedReview inteira

// Simplificar o fluxo após review:
const reviewResult = await executeReview(card);
if (!reviewResult.success) {
  // Rollback: voltar para test
  await cardsApi.moveCard(card.id, 'test');
  onCardMove(card.id, 'test');
  await updateStatus('error', 'test', reviewResult.error);
  return;
}

// Após review bem-sucedido, ir direto para DONE
await cardsApi.moveCard(card.id, 'done');
onCardMove(card.id, 'done');
await updateStatus('completed', 'done');
```

#### 3.2 Backend - Remover Endpoints de Merge

**Modificar `backend/src/main.py`:**

```python
# REMOVER os seguintes endpoints:
# - POST /api/cards/{card_id}/merge
# - POST /api/cleanup-orphan-worktrees (opcional, pode manter para limpeza)

# REMOVER imports:
# from .conflict_resolver import ConflictResolver
# (manter GitWorkspaceManager pois ainda é usado para criar worktrees)

# REMOVER funções:
# - merge_card_workspace()
# - resolve_conflicts_background()
```

#### 3.3 Backend - Simplificar GitWorkspaceManager

**Modificar `backend/src/git_workspace.py`:**

```python
# REMOVER os seguintes métodos:
# - merge_worktree()
# - get_conflict_diff()
# - resolve_conflict()

# MANTER apenas:
# - create_worktree() - ainda necessário para isolamento
# - cleanup_worktree() - para limpeza
# - list_active_worktrees() - para listagem
# - cleanup_orphan_worktrees() - para manutenção
# - recover_state() - para recuperação
# - Métodos auxiliares de git (_run_git_command, _get_default_branch, etc)

# REMOVER dataclasses e imports não utilizados:
# - MergeResult
# - Lock global para merge
```

#### 3.4 Backend - Remover Campo merge_status

**Modificar `backend/src/models/card.py`:**

```python
class Card(Base):
    # ... campos existentes ...

    # Manter campos de worktree (ainda usados):
    branch_name = Column(String, nullable=True)
    worktree_path = Column(String, nullable=True)

    # REMOVER:
    # merge_status = Column(String, default="none")
```

#### 3.5 Frontend - Remover Tipos de Merge

**Modificar `frontend/src/types/index.ts`:**

```typescript
// REMOVER:
// export type MergeStatus = 'none' | 'merging' | 'resolving' | 'merged' | 'failed';

export interface Card {
  // ... campos existentes ...
  branchName?: string;       // MANTER (ainda usado para indicar branch)
  worktreePath?: string;      // MANTER (ainda usado para isolamento)
  // REMOVER: mergeStatus
}

// REMOVER interface ActiveBranch ou simplificar removendo mergeStatus
```

#### 3.6 Frontend - Simplificar Branch Indicator

**Modificar `frontend/src/components/BranchIndicator/BranchIndicator.tsx`:**

```typescript
// Simplificar para mostrar apenas se tem branch ou não
// Remover lógica de status de merge

export const BranchIndicator: React.FC<BranchIndicatorProps> = ({
  branchName,
  onClick
}) => {
  const shortName = branchName.replace('agent/', '').split('-')[0];

  return (
    <button
      className={styles.branchBadge}
      onClick={onClick}
      title={branchName}
    >
      <span className={styles.icon}>🔀</span>
      <span className={styles.name}>{shortName}</span>
    </button>
  );
};
```

#### 3.7 Limpeza de Worktrees

Como não haverá mais merge automático, considerar quando/como limpar worktrees:

**Opção 1:** Limpar quando card vai para DONE
```typescript
// Em useWorkflowAutomation.ts, após mover para DONE:
await cleanupWorktree(card.id); // Nova chamada de API
```

**Opção 2:** Manter worktrees e limpar periodicamente via manutenção

**Opção 3:** Adicionar botão manual para limpar worktree de um card específico

---

## 4. Testes

### Unitários
- [x] Workflow completa sem chamar merge
- [x] Card vai direto de REVIEW para DONE
- [x] Worktree ainda é criado ao iniciar workflow
- [x] Branch indicator mostra branch sem status de merge

### Integração
- [x] Pipeline completo BACKLOG → PLAN → IMPLEMENT → TEST → REVIEW → DONE
- [x] Múltiplos cards executando em paralelo (isolamento mantido)
- [x] Worktrees são criados mas não há tentativa de merge
- [x] Limpeza de worktrees funciona (se implementada)

---

## 5. Considerações

### Riscos
- **Worktrees acumulados:** Sem merge automático, worktrees podem acumular
  - Mitigação: Implementar limpeza periódica ou manual

- **Branches órfãs:** Branches não serão deletadas automaticamente
  - Mitigação: Script de manutenção para limpar branches antigas

### Dependências
- Nenhuma dependência externa
- Alteração puramente de simplificação de fluxo

### Impacto
- **Positivo:** Simplificação significativa do código
- **Positivo:** Menos pontos de falha no pipeline
- **Positivo:** Execução mais rápida (sem esperar merge)
- **Neutro:** Usuário precisará fazer merge manualmente se desejar
- **Negativo:** Perda de integração contínua automática