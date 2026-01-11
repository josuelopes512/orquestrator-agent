# Plano de Remoção da Aba de Métricas Não Utilizada

## 1. Resumo

Remover a aba de "Métricas" da barra lateral do workspace, mantendo apenas as métricas integradas ao Dashboard. A aba de métricas separada não está sendo utilizada e cria redundância com o dashboard que já exibe informações de métricas.

---

## 2. Objetivos e Escopo

### Objetivos
- [x] Remover a navegação para página de métricas da sidebar
- [x] Remover a rota de métricas do sistema de navegação
- [x] Manter funcionalidade de métricas no Dashboard
- [x] Limpar código não utilizado relacionado à página de métricas

### Fora do Escopo
- Remoção das APIs de métricas (ainda usadas pelo Dashboard)
- Alteração nas métricas exibidas no Dashboard
- Remoção dos componentes de métricas do Dashboard

---

## 3. Implementação

### Arquivos a Serem Modificados/Removidos

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `frontend/src/components/Navigation/Sidebar.tsx` | Modificar | Remover item "Métricas" da lista de navegação |
| `frontend/src/layouts/WorkspaceLayout.tsx` | Modificar | Remover tipo 'metrics' do ModuleType e labels |
| `frontend/src/App.tsx` | Modificar | Remover case 'metrics' do switch e imports |
| `frontend/src/pages/MetricsPage.tsx` | Remover | Deletar página não utilizada |
| `frontend/src/pages/MetricsPage.module.css` | Remover | Deletar estilos da página |

### Detalhes Técnicos

#### 1. Atualizar Sidebar.tsx
Remover o item de métricas do array `navigationItems`:

```typescript
const navigationItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'fa-solid fa-chart-line',
    description: 'Visão geral do projeto',
  },
  {
    id: 'kanban',
    label: 'Kanban Board',
    icon: 'fa-solid fa-table-columns',
    description: 'Gerenciar tarefas e workflow',
  },
  {
    id: 'chat',
    label: 'AI Assistant',
    icon: 'fa-solid fa-comments',
    description: 'Chat com assistente AI',
  },
  // Item de métricas removido
  {
    id: 'settings',
    label: 'Configurações',
    icon: 'fa-solid fa-gear',
    description: 'Preferências do projeto',
  },
];
```

#### 2. Atualizar WorkspaceLayout.tsx
Atualizar o tipo ModuleType e remover referência:

```typescript
export type ModuleType = 'dashboard' | 'kanban' | 'chat' | 'settings';

const moduleLabels: Record<ModuleType, string> = {
  dashboard: 'Dashboard',
  kanban: 'Kanban Board',
  chat: 'AI Assistant',
  settings: 'Configurações',
};
```

#### 3. Limpar App.tsx
- Remover import de MetricsPage
- Remover case 'metrics' do switch em renderView()
- Verificar se há outras referências a 'metrics' como ModuleType

#### 4. Manter APIs de métricas
- NÃO remover `frontend/src/api/metrics.ts` - ainda usado pelo Dashboard
- NÃO remover `frontend/src/types/metrics.ts` - ainda usado pelo Dashboard
- NÃO remover hooks como `useDashboardMetrics.ts` - usado pelo Dashboard

---

## 4. Testes

### Manuais
- [x] Verificar que a sidebar não mostra mais a opção "Métricas"
- [x] Confirmar que navegação entre outras páginas funciona normalmente
- [x] Verificar que Dashboard ainda exibe métricas corretamente
- [x] Testar que não há erros no console ao navegar

### Validação
- [x] TypeScript compila sem erros
- [x] Nenhuma referência órfã a 'metrics' como ModuleType
- [x] Dashboard mantém funcionalidade completa de métricas

---

## 5. Considerações

- **Riscos:** Baixo - apenas remoção de UI não utilizada
- **Benefícios:** Interface mais limpa e focada, menos código para manter
- **Nota:** As métricas continuam disponíveis através do Dashboard que já fornece visualização rica e integrada dos dados