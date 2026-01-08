# Adicionar Custo por Card na UI

## 1. Resumo

Implementar visualização de custo estimado por card na interface, similar ao sistema de tokens já existente. O cálculo será baseado nos modelos selecionados para cada etapa do workflow (plan, implement, test, review) e seus respectivos custos de input/output tokens.

---

## 2. Objetivos e Escopo

### Objetivos
- [x] Adicionar configuração de preços por modelo no sistema
- [x] Calcular custo baseado nos tokens usados e modelo utilizado
- [x] Exibir custo total do card na UI (similar aos tokens)
- [x] Adicionar breakdown de custos por etapa no modal de detalhes
- [x] Implementar estimativa de custo antes da execução

### Fora do Escopo
- Sistema de billing/cobrança real
- Integração com APIs de pagamento
- Histórico de custos por período
- Dashboard de análise de custos

---

## 3. Implementação

### Arquivos a Serem Modificados/Criados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `backend/src/config/pricing.py` | Criar | Configuração de preços por modelo |
| `backend/src/services/cost_calculator.py` | Criar | Serviço para cálculo de custos |
| `backend/src/models/execution.py` | Modificar | Adicionar campo de custo na execução |
| `backend/src/repositories/execution_repository.py` | Modificar | Adicionar cálculo e persistência de custos |
| `backend/src/schemas/card.py` | Modificar | Adicionar CostStats ao schema |
| `backend/src/routes/cards.py` | Modificar | Retornar custos na resposta da API |
| `frontend/src/types/index.ts` | Modificar | Adicionar tipo CostStats |
| `frontend/src/components/Card/Card.tsx` | Modificar | Exibir custo no card |
| `frontend/src/components/Card/Card.module.css` | Modificar | Estilização do indicador de custo |
| `frontend/src/components/LogsModal/LogsModal.tsx` | Modificar | Exibir breakdown de custos |
| `frontend/src/constants/pricing.ts` | Criar | Constantes de preços no frontend |
| `frontend/src/utils/costCalculator.ts` | Criar | Utilitários para formatação de custos |

### Detalhes Técnicos

#### 1. Configuração de Preços (Backend)

```python
# backend/src/config/pricing.py
from decimal import Decimal
from typing import Dict, Tuple

# Preços em USD por 1M tokens (input, output)
MODEL_PRICING: Dict[str, Tuple[Decimal, Decimal]] = {
    # Claude Models
    "opus-4.5": (Decimal("15.00"), Decimal("75.00")),
    "sonnet-4.5": (Decimal("3.00"), Decimal("15.00")),
    "haiku-4.5": (Decimal("0.25"), Decimal("1.25")),

    # Gemini Models
    "gemini-3-pro": (Decimal("1.25"), Decimal("5.00")),
    "gemini-3-flash": (Decimal("0.075"), Decimal("0.30")),
}

def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Decimal:
    """Calcula custo baseado no modelo e tokens"""
    if model not in MODEL_PRICING:
        return Decimal("0")

    input_price, output_price = MODEL_PRICING[model]

    # Converter tokens para milhões e calcular
    input_cost = (Decimal(input_tokens) / 1_000_000) * input_price
    output_cost = (Decimal(output_tokens) / 1_000_000) * output_price

    return input_cost + output_cost
```

#### 2. Modificação do Modelo Execution

```python
# backend/src/models/execution.py (adicionar campo)
execution_cost: Mapped[Decimal | None] = mapped_column(
    Numeric(10, 6),  # Até 10 dígitos, 6 decimais
    nullable=True
)
```

#### 3. Schema para Cost Stats

```python
# backend/src/schemas/card.py
class CostStats(BaseModel):
    """Schema for cost statistics."""
    totalCost: float = 0.0
    planCost: float = 0.0
    implementCost: float = 0.0
    testCost: float = 0.0
    reviewCost: float = 0.0
    currency: str = "USD"
```

#### 4. Componente de Custo no Frontend

```typescript
// frontend/src/types/index.ts
export interface CostStats {
  totalCost: number;
  planCost: number;
  implementCost: number;
  testCost: number;
  reviewCost: number;
  currency: string;
}
```

```tsx
// frontend/src/components/Card/Card.tsx (adicionar após tokenStats)
{card.costStats && card.costStats.totalCost > 0 && (
  <div className={styles.costStats}>
    <span className={styles.costIcon}>$</span>
    <span>{formatCost(card.costStats.totalCost)}</span>
  </div>
)}
```

#### 5. Estimativa de Custo Pré-Execução

```typescript
// frontend/src/utils/costCalculator.ts
export function estimateCost(
  modelPlan: ModelType,
  modelImplement: ModelType,
  modelTest: ModelType,
  modelReview: ModelType
): number {
  // Estimativas médias baseadas em histórico
  const avgTokens = {
    plan: { input: 5000, output: 2000 },
    implement: { input: 10000, output: 5000 },
    test: { input: 8000, output: 3000 },
    review: { input: 7000, output: 2500 }
  };

  return (
    calculateModelCost(modelPlan, avgTokens.plan) +
    calculateModelCost(modelImplement, avgTokens.implement) +
    calculateModelCost(modelTest, avgTokens.test) +
    calculateModelCost(modelReview, avgTokens.review)
  );
}
```

---

## 4. Testes

### Unitários
- [ ] Teste de cálculo de custo por modelo
- [ ] Teste de agregação de custos por card
- [ ] Teste de formatação de valores monetários
- [ ] Teste de estimativa de custos

### Integração
- [ ] Teste de API retornando custos corretos
- [ ] Teste de atualização de custos após execução
- [ ] Teste de exibição na UI

---

## 5. Considerações

### Riscos
- **Precisão de custos**: Os preços dos modelos podem mudar - considerar sistema de atualização
- **Performance**: Cálculos adicionais podem impactar performance - implementar cache se necessário

### Dependências
- Nenhuma biblioteca externa necessária
- Usar Decimal no Python para precisão monetária

### Melhorias Futuras
- Dashboard de análise de custos
- Alertas de custo elevado
- Comparação de custo entre modelos
- Histórico de custos por período
- Orçamento por projeto/card