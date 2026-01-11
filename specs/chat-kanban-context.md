# Chat com Contexto do Kanban

## Objetivo

Integrar o chat com o Kanban, injetando automaticamente o estado atual do board no system prompt para que o assistente AI possa responder perguntas sobre tarefas, status, e atividades recentes.

## Decisoes Tecnicas

- Consultar DB a cada mensagem (dados sempre frescos)
- Usar CardRepository e ActivityRepository existentes
- Metodo `get_system_prompt()` vira async
- Formato estruturado com emojis para facilitar leitura

## Arquivos Modificados

- [x] `backend/src/services/chat_service.py` - Logica de contexto do kanban implementada

## Implementacao

### 1. Modificar ChatService

**Arquivo**: `backend/src/services/chat_service.py`

#### 1.1 Adicionar imports necessarios

```python
from ..database import async_session_maker
from ..repositories.card_repository import CardRepository
from ..repositories.activity_repository import ActivityRepository
from datetime import datetime, timezone
```

#### 1.2 Criar metodo para formatar tempo relativo

```python
def _format_relative_time(self, dt: datetime) -> str:
    """Formata datetime como tempo relativo (ex: 'ha 2 dias')"""
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt

    if diff.days > 0:
        return f"ha {diff.days} dia{'s' if diff.days > 1 else ''}"

    hours = diff.seconds // 3600
    if hours > 0:
        return f"ha {hours}h"

    minutes = diff.seconds // 60
    if minutes > 0:
        return f"ha {minutes}min"

    return "agora"
```

#### 1.3 Criar metodo para truncar texto

```python
def _truncate(self, text: str, max_length: int = 80) -> str:
    """Trunca texto adicionando ... se necessario"""
    if not text:
        return ""
    text = text.replace('\n', ' ').strip()
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
```

#### 1.4 Criar metodo para buscar contexto do kanban

```python
async def _get_kanban_context(self) -> str:
    """Busca estado atual do kanban e formata como contexto"""
    try:
        async with async_session_maker() as session:
            card_repo = CardRepository(session)
            activity_repo = ActivityRepository(session)

            # Buscar todos os cards
            cards = await card_repo.get_all()

            # Buscar atividades recentes
            activities = await activity_repo.get_recent_activities(limit=5)

            # Agrupar cards por coluna
            columns = {
                "backlog": [], "plan": [], "implement": [],
                "test": [], "review": [], "done": [],
                "completed": [], "archived": [], "cancelado": []
            }

            for card in cards:
                if card.column_id in columns:
                    columns[card.column_id].append(card)

            # Montar contexto
            lines = ["=== KANBAN STATUS ==="]

            # Colunas ativas (excluindo completed, archived, cancelado)
            column_config = [
                ("backlog", "Backlog"),
                ("plan", "Plan"),
                ("implement", "Implement"),
                ("test", "Test"),
                ("review", "Review"),
                ("done", "Done"),
            ]

            for col_id, col_name in column_config:
                col_cards = columns[col_id]
                if col_cards:
                    emoji = {"backlog": "📋", "plan": "📝", "implement": "🔨",
                             "test": "🧪", "review": "👀", "done": "✅"}.get(col_id, "📌")
                    lines.append(f"\n{emoji} {col_name} ({len(col_cards)}):")
                    for card in col_cards[:5]:  # Limitar a 5 cards por coluna
                        time_str = self._format_relative_time(card.created_at)
                        lines.append(f"  • \"{card.title}\" ({time_str})")
                        if card.description:
                            desc = self._truncate(card.description, 60)
                            lines.append(f"    → {desc}")

            # Resumo
            active_cols = ["backlog", "plan", "implement", "test", "review", "done"]
            summary = " | ".join([f"{len(columns[c])} {c}" for c in active_cols])
            lines.append(f"\n📊 Resumo: {summary}")

            # Atividades recentes
            if activities:
                lines.append("\n🕐 Ultimas atividades:")
                for act in activities[:5]:
                    time_str = self._format_relative_time(
                        datetime.fromisoformat(act["timestamp"])
                    )
                    card_title = self._truncate(act["cardTitle"], 30)

                    if act["type"] == "moved":
                        lines.append(f"  • \"{card_title}\" movido para {act['toColumn']} ({time_str})")
                    elif act["type"] == "completed":
                        lines.append(f"  • \"{card_title}\" concluido ({time_str})")
                    elif act["type"] == "created":
                        lines.append(f"  • \"{card_title}\" criado ({time_str})")
                    else:
                        lines.append(f"  • \"{card_title}\" {act['type']} ({time_str})")

            lines.append("===================")

            return "\n".join(lines)

    except Exception as e:
        print(f"[ChatService] Error getting kanban context: {e}")
        return ""
```

#### 1.5 Modificar get_system_prompt para ser async

```python
async def get_system_prompt(self) -> str:
    """Get system prompt with kanban context"""
    kanban_context = await self._get_kanban_context()

    base_prompt = DEFAULT_SYSTEM_PROMPT

    if kanban_context:
        return f"{base_prompt}\n\n{kanban_context}"

    return base_prompt
```

#### 1.6 Modificar send_message para usar await no system_prompt

Na linha onde chama `self.get_system_prompt()`, mudar para `await self.get_system_prompt()`.

## Exemplo de Contexto Gerado

```
=== KANBAN STATUS ===

📋 Backlog (3):
  • "Implementar login" (ha 2 dias)
    → Sistema de autenticacao com JWT e refresh tokens
  • "Adicionar footer" (ha 1 dia)
    → Footer responsivo com links de redes sociais
  • "Corrigir bug #45" (ha 3h)
    → Erro de validacao no formulario de cadastro

🔨 Implement (1):
  • "Refatorar API" (ha 3h)
    → Reorganizar endpoints seguindo REST conventions

✅ Done (2):
  • "Setup do projeto" (ha 1 dia)
  • "Criar banco de dados" (ha 2 dias)

📊 Resumo: 3 backlog | 0 plan | 1 implement | 0 test | 0 review | 2 done

🕐 Ultimas atividades:
  • "Refatorar API" movido para implement (ha 3h)
  • "Setup do projeto" concluido (ha 1 dia)
  • "Criar banco" concluido (ha 2 dias)
===================
```

## Testes

### Teste Manual

1. Iniciar o backend
2. Abrir o chat
3. Perguntar: "Quais tarefas tenho no backlog?"
4. Verificar se a resposta menciona os cards corretos
5. Perguntar: "O que foi feito recentemente?"
6. Verificar se menciona as atividades corretas

### Verificacao de Logs

- Verificar no console do backend se o contexto esta sendo gerado
- Verificar se nao ha erros de conexao com o banco

## Consideracoes

- O contexto e gerado a cada mensagem para garantir dados frescos
- Cards arquivados e cancelados nao aparecem no resumo principal
- Limitado a 5 cards por coluna para nao poluir o contexto
- Atividades limitadas a 5 mais recentes
