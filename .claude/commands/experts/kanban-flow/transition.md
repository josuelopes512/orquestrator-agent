---
allowed-tools: Read, Glob, Grep, Edit, Write
description: Validar e debugar transicoes de cards entre colunas
---

# Kanban Flow - Transition

Expert em transicoes de cards entre colunas do Kanban.

## Dominio

- Validacao de transicoes SDLC
- ALLOWED_TRANSITIONS no frontend e backend
- Regras de movimentacao de cards
- Debug de "card nao pode mover"

## Arquivos Principais

### Frontend
- `frontend/src/types/index.ts` - ALLOWED_TRANSITIONS, isValidTransition()
- `frontend/src/components/Card/Card.tsx` - disabled draggable logic

### Backend
- `backend/src/repositories/card_repository.py` - ALLOWED_TRANSITIONS, move()
- `backend/src/schemas/card.py` - CardMove validation
- `backend/src/routes/cards.py` - PATCH /move endpoint

## Transicoes Validas

```
backlog   -> plan, cancelado
plan      -> implement, cancelado
implement -> test, cancelado
test      -> review, cancelado
review    -> done, cancelado
done      -> completed, archived, cancelado
completed -> archived
archived  -> done
cancelado -> (nenhuma - terminal)
```

## Instrucoes

Quando chamado para:

### 1. Validar uma transicao
```
Entrada: "de backlog para implement"
Acao: Verificar ALLOWED_TRANSITIONS
Saida: Valido/Invalido + motivo
```

### 2. Debugar problema de transicao
```
1. Ler ALLOWED_TRANSITIONS nos dois arquivos
2. Verificar se estao sincronizados
3. Ler logica de disabled no Card.tsx
4. Identificar onde a validacao falha
```

### 3. Adicionar nova transicao
```
1. Editar frontend/src/types/index.ts
2. Editar backend/src/repositories/card_repository.py
3. Verificar impacto no workflow automation
```

### 4. Remover transicao
```
1. Verificar se ha cards que usam essa transicao
2. Editar ambos os arquivos
3. Atualizar testes se existirem
```

## Validacoes Importantes

1. **Frontend e Backend devem estar sincronizados**
2. **Transicao para cancelado sempre permitida** (exceto de cancelado)
3. **Workflow linear**: nao pode pular etapas
4. **Card em execucao**: nao pode ser movido manualmente

## Argumentos

$ARGUMENTS
