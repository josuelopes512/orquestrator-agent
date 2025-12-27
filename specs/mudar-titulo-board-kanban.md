# Refactor: Mudar Título de "Kanban Board" para "Board Kanban"

**Tipo:** Refactor
**Prioridade:** Baixa
**Estimativa:** 5 minutos

---

## 1. Resumo

Alterar o título exibido na interface do usuário de "Kanban Board" para "Board Kanban". Esta mudança visa adaptar a nomenclatura para uma forma mais natural em português, mantendo consistência com a linguagem do projeto.

---

## 2. Objetivos e Escopo

### Objetivos
- [ ] Alterar o título visível na UI (header da aplicação)
- [ ] Alterar o título da aba do navegador (tag `<title>`)

### Fora do Escopo
- Não alterar documentação interna (specs, README, etc.)
- Não alterar nome de variáveis, classes ou identificadores de código
- Não alterar textos em arquivos de configuração (package.json description)

---

## 3. Implementação

### Arquivos a Serem Modificados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `frontend/src/App.tsx` | Modificar | Alterar texto do `<h1>` no header |
| `frontend/index.html` | Modificar | Alterar conteúdo da tag `<title>` |

### Detalhes Técnicos

#### 1. frontend/src/App.tsx (linha 124)

**Antes:**
```tsx
<h1 className={styles.title}>Kanban Board</h1>
```

**Depois:**
```tsx
<h1 className={styles.title}>Board Kanban</h1>
```

#### 2. frontend/index.html (linha 7)

**Antes:**
```html
<title>Kanban Board</title>
```

**Depois:**
```html
<title>Board Kanban</title>
```

---

## 4. Testes

### Manuais
- [ ] Verificar que o título no header da aplicação exibe "Board Kanban"
- [ ] Verificar que a aba do navegador exibe "Board Kanban"
- [ ] Verificar que a aplicação continua funcionando normalmente após as mudanças

### Unitários
- Não aplicável (mudança apenas em texto estático)

---

## 5. Considerações

- **Riscos:** Nenhum risco significativo. São apenas mudanças em strings de texto estático.
- **Dependências:** Nenhuma dependência externa ou aprovação necessária.
- **Impacto:** Mudança puramente visual, sem impacto funcional.
