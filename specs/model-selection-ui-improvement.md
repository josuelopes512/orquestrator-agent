# Melhoria da Interface de Seleção de Modelos

## 1. Resumo

Redesenhar a interface de seleção de modelos no modal de criação de cards para melhorar a experiência visual e a usabilidade. A interface atual apresenta uma distribuição de modelos em cards pequenos que não se integram bem com o design do sistema. A nova implementação terá uma interface mais moderna, intuitiva e alinhada com o design system existente.

---

## 2. Objetivos e Escopo

### Objetivos
- [x] Criar uma interface de seleção de modelos mais elegante e intuitiva
- [x] Melhorar a integração visual com o design system existente (tema dark, glassmorphism)
- [x] Adicionar melhor hierarquia visual e feedback de interação
- [x] Implementar animações suaves para transições de estado
- [x] Otimizar o layout para melhor uso do espaço disponível

### Fora do Escopo
- Mudanças na funcionalidade de seleção de modelos
- Alterações no backend ou APIs
- Modificações em outros modais além do AddCardModal

---

## 3. Implementação

### Arquivos a Serem Modificados/Criados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `frontend/src/components/AddCardModal/AddCardModal.tsx` | Modificar | Atualizar estrutura HTML da seleção de modelos |
| `frontend/src/components/AddCardModal/AddCardModal.module.css` | Modificar | Redesenhar estilos da seleção de modelos |
| `frontend/src/components/ModelCard/ModelCard.tsx` | Criar | Novo componente reutilizável para cards de modelo |
| `frontend/src/components/ModelCard/ModelCard.module.css` | Criar | Estilos dedicados para o componente ModelCard |
| `frontend/src/components/ModelCard/index.ts` | Criar | Export barrel para o componente |

### Detalhes Técnicos

#### 1. Novo Design da Seleção de Modelos

**Layout Principal:**
- Substituir o grid 2x2 atual por um layout em linha horizontal com scroll (desktop) ou vertical (mobile)
- Cards maiores com mais informações visuais
- Indicadores de performance mais destacados
- Efeito glassmorphism consistente com o resto do sistema

**Estrutura do Componente ModelCard:**
```tsx
interface ModelCardProps {
  model: {
    id: string;
    name: string;
    displayName: string;
    provider: 'anthropic' | 'google';
    performance: 'fastest' | 'balanced' | 'powerful';
    description: string;
    icon: string;
    accent: string;
    maxTokens: number;
  };
  selected: boolean;
  onSelect: () => void;
  compact?: boolean;
}

const ModelCard: React.FC<ModelCardProps> = ({ model, selected, onSelect, compact = false }) => {
  return (
    <div
      className={`${styles.modelCard} ${selected ? styles.selected : ''} ${compact ? styles.compact : ''}`}
      onClick={onSelect}
      role="button"
      tabIndex={0}
      aria-selected={selected}
    >
      <div className={styles.cardGlow} style={{ background: model.accent }} />

      <div className={styles.cardHeader}>
        <span className={styles.modelIcon}>{model.icon}</span>
        <div className={styles.modelInfo}>
          <h4 className={styles.modelName}>{model.displayName}</h4>
          <span className={styles.providerBadge}>{model.provider}</span>
        </div>
      </div>

      <p className={styles.description}>{model.description}</p>

      <div className={styles.cardFooter}>
        <div className={styles.performanceIndicator}>
          <PerformanceIcon type={model.performance} />
          <span>{getPerformanceLabel(model.performance)}</span>
        </div>
        <span className={styles.tokenCapacity}>
          {formatTokens(model.maxTokens)}
        </span>
      </div>

      {selected && (
        <div className={styles.selectedIndicator}>
          <CheckIcon />
        </div>
      )}
    </div>
  );
};
```

#### 2. Estilos CSS Aprimorados

**Card de Modelo:**
```css
.modelCard {
  position: relative;
  min-width: 280px;
  padding: var(--space-5);
  background: linear-gradient(
    135deg,
    rgba(22, 22, 26, 0.8) 0%,
    rgba(28, 28, 33, 0.6) 100%
  );
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-xl);
  cursor: pointer;
  transition: all var(--duration-normal) var(--ease-out);
  overflow: hidden;
}

.modelCard::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(
    135deg,
    transparent 0%,
    rgba(var(--model-accent-rgb), 0.05) 100%
  );
  opacity: 0;
  transition: opacity var(--duration-normal) var(--ease-out);
}

.modelCard:hover {
  transform: translateY(-4px) scale(1.02);
  border-color: var(--accent-primary);
  box-shadow:
    0 10px 40px rgba(0, 0, 0, 0.3),
    0 0 40px rgba(var(--model-accent-rgb), 0.1);
}

.modelCard:hover::before {
  opacity: 1;
}

.modelCard.selected {
  background: linear-gradient(
    135deg,
    rgba(124, 58, 237, 0.1) 0%,
    rgba(var(--model-accent-rgb), 0.08) 100%
  );
  border-color: var(--accent-primary);
  box-shadow:
    0 0 30px rgba(124, 58, 237, 0.2),
    0 10px 40px rgba(0, 0, 0, 0.4);
}

.cardGlow {
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  opacity: 0;
  filter: blur(80px);
  transition: opacity var(--duration-normal) var(--ease-out);
  pointer-events: none;
  animation: pulse 3s ease-in-out infinite;
}

.modelCard.selected .cardGlow {
  opacity: 0.15;
}
```

**Container de Seleção de Etapas:**
```css
.workflowStages {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

.stageSection {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.stageHeader {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.stageIcon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-tertiary);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  color: var(--accent-primary);
}

.stageTitle {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stageDescription {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-left: 44px; /* Align with title */
}

.modelCarousel {
  position: relative;
  margin-left: 44px; /* Align with title */
}

.modelCarouselInner {
  display: flex;
  gap: var(--space-4);
  overflow-x: auto;
  padding: var(--space-1) 0 var(--space-3);
  scroll-snap-type: x mandatory;
  scrollbar-width: thin;
  scrollbar-color: var(--border-default) transparent;
}

.modelCarouselInner::-webkit-scrollbar {
  height: 6px;
}

.modelCarouselInner::-webkit-scrollbar-track {
  background: transparent;
}

.modelCarouselInner::-webkit-scrollbar-thumb {
  background: var(--border-default);
  border-radius: var(--radius-full);
}

.modelCarouselInner::-webkit-scrollbar-thumb:hover {
  background: var(--border-strong);
}

.modelCard {
  scroll-snap-align: start;
  flex-shrink: 0;
}

/* Responsive para mobile */
@media (max-width: 768px) {
  .modelCarousel {
    margin-left: 0;
  }

  .modelCarouselInner {
    flex-direction: column;
    overflow-x: hidden;
    overflow-y: visible;
  }

  .modelCard {
    min-width: 100%;
  }
}
```

#### 3. Indicadores de Performance Visual

```tsx
const PerformanceIcon: React.FC<{ type: string }> = ({ type }) => {
  switch(type) {
    case 'fastest':
      return (
        <svg className={styles.perfIcon} viewBox="0 0 20 20">
          <path d="M10 2L8 8H2L10 18L12 12H18L10 2Z" fill="currentColor"/>
        </svg>
      );
    case 'balanced':
      return (
        <svg className={styles.perfIcon} viewBox="0 0 20 20">
          <circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" strokeWidth="2"/>
          <circle cx="10" cy="10" r="3" fill="currentColor"/>
        </svg>
      );
    case 'powerful':
      return (
        <svg className={styles.perfIcon} viewBox="0 0 20 20">
          <path d="M10 2L12.5 7.5L18 10L12.5 12.5L10 18L7.5 12.5L2 10L7.5 7.5L10 2Z" fill="currentColor"/>
        </svg>
      );
    default:
      return null;
  }
};
```

#### 4. Animações e Micro-interações

```css
@keyframes slideInModel {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.modelCard {
  animation: slideInModel var(--duration-normal) var(--ease-out) backwards;
}

.modelCard:nth-child(1) { animation-delay: 0ms; }
.modelCard:nth-child(2) { animation-delay: 50ms; }
.modelCard:nth-child(3) { animation-delay: 100ms; }
.modelCard:nth-child(4) { animation-delay: 150ms; }
.modelCard:nth-child(5) { animation-delay: 200ms; }

.selectedIndicator {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  width: 24px;
  height: 24px;
  background: var(--accent-success);
  border-radius: var(--radius-full);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: springIn var(--duration-normal) var(--ease-out);
}

@keyframes springIn {
  0% {
    transform: scale(0);
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
  }
}
```

#### 5. Integração no AddCardModal

```tsx
// AddCardModal.tsx - Seção de seleção de modelos atualizada
const workflowStages = [
  {
    id: 'plan',
    title: 'Planejamento',
    description: 'Estratégia e arquitetura da implementação',
    icon: '📋',
    modelKey: 'modelPlan'
  },
  {
    id: 'implement',
    title: 'Implementação',
    description: 'Codificação e desenvolvimento da solução',
    icon: '🚀',
    modelKey: 'modelImplement'
  },
  {
    id: 'test',
    title: 'Testes',
    description: 'Validação e verificação da qualidade',
    icon: '✅',
    modelKey: 'modelTest'
  },
  {
    id: 'review',
    title: 'Revisão',
    description: 'Polimento e refinamento final',
    icon: '🔍',
    modelKey: 'modelReview'
  }
];

// Renderização
<div className={styles.workflowStages}>
  {workflowStages.map(stage => (
    <div key={stage.id} className={styles.stageSection}>
      <div className={styles.stageHeader}>
        <div className={styles.stageIcon}>{stage.icon}</div>
        <div>
          <h3 className={styles.stageTitle}>{stage.title}</h3>
          <p className={styles.stageDescription}>{stage.description}</p>
        </div>
      </div>

      <div className={styles.modelCarousel}>
        <div className={styles.modelCarouselInner}>
          {availableModels.map(model => (
            <ModelCard
              key={model.id}
              model={model}
              selected={formData[stage.modelKey] === model.id}
              onSelect={() => handleModelSelect(stage.modelKey, model.id)}
            />
          ))}
        </div>
      </div>
    </div>
  ))}
</div>
```

---

## 4. Testes

### Unitários
- [x] Teste do componente ModelCard com diferentes props
- [x] Teste de seleção de modelo e propagação de eventos
- [x] Teste de renderização condicional baseada em breakpoints
- [x] Teste de acessibilidade (ARIA labels, keyboard navigation)

### Integração
- [x] Teste de persistência da seleção no formulário
- [x] Teste de responsividade em diferentes tamanhos de tela
- [x] Teste de performance com animações
- [x] Teste de compatibilidade com temas light/dark

### Visuais
- [x] Verificar alinhamento e espaçamento em todos os breakpoints
- [x] Validar contraste de cores e legibilidade
- [x] Confirmar animações suaves sem flicker
- [x] Testar com diferentes quantidades de modelos disponíveis

---

## 5. Considerações

### Benefícios da Nova Implementação
- **Melhor Hierarquia Visual**: Separação clara entre etapas com ícones e descrições
- **Experiência Aprimorada**: Cards maiores com mais informações relevantes
- **Consistência Visual**: Integração completa com o design system existente
- **Responsividade**: Layout adaptativo para desktop e mobile
- **Acessibilidade**: Melhor suporte para navegação por teclado e leitores de tela

### Possíveis Extensões Futuras
- Adicionar tooltips com informações detalhadas sobre cada modelo
- Implementar comparação lado a lado de modelos
- Incluir métricas de uso/custos estimados
- Adicionar presets de seleção (ex: "Rápido", "Balanceado", "Máxima Qualidade")

### Riscos
- **Performance**: Animações podem impactar em dispositivos mais lentos - Mitigação: usar `prefers-reduced-motion`
- **Espaço**: Cards maiores ocupam mais espaço vertical - Mitigação: layout horizontal com scroll no desktop