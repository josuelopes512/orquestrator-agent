#!/bin/bash
# Hook: Sync automático do Kanban Flow Knowledge Base
# Executado via PostToolUse quando arquivos são editados/criados

set -e

# Fallback para CLAUDE_PROJECT_DIR se não estiver definido
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"

KNOWLEDGE_FILE="$PROJECT_DIR/.claude/commands/experts/kanban-flow/KNOWLEDGE.md"
LOG_FILE="$PROJECT_DIR/.claude/hooks/kanban-flow-sync.log"

# Garantir que o diretório de log existe
mkdir -p "$(dirname "$LOG_FILE")"

# Paths monitorados pelo kanban-flow expert
MONITORED_PATTERNS=(
    "frontend/src/components/Board/"
    "frontend/src/components/Column/"
    "frontend/src/components/Card/"
    "frontend/src/pages/KanbanPage"
    "frontend/src/hooks/useWorkflow"
    "frontend/src/hooks/useAgent"
    "frontend/src/api/cards"
    "frontend/src/types/"
    "backend/src/models/card"
    "backend/src/models/activity"
    "backend/src/models/execution"
    "backend/src/schemas/card"
    "backend/src/repositories/card_repository"
    "backend/src/repositories/activity_repository"
    "backend/src/routes/cards"
    "backend/src/routes/activities"
    "backend/src/services/auto_cleanup"
    "backend/src/services/diff_analyzer"
)

# Ler input do hook (JSON via stdin)
INPUT=$(cat)

# Extrair file_path do JSON
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.filePath // empty' 2>/dev/null)

# Se não conseguiu extrair o path, sair silenciosamente
if [ -z "$FILE_PATH" ]; then
    exit 0
fi

# Converter para path relativo se necessário
if [[ "$FILE_PATH" == "$PROJECT_DIR"* ]]; then
    FILE_PATH="${FILE_PATH#$PROJECT_DIR/}"
fi

# Verificar se o arquivo está nos paths monitorados
is_monitored() {
    local file="$1"
    for pattern in "${MONITORED_PATTERNS[@]}"; do
        if [[ "$file" == *"$pattern"* ]]; then
            return 0
        fi
    done
    return 1
}

# Se não é um arquivo monitorado, sair
if ! is_monitored "$FILE_PATH"; then
    exit 0
fi

# Log da detecção
log_change() {
    local msg="$1"
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $msg" >> "$LOG_FILE"
}

log_change "Arquivo monitorado modificado: $FILE_PATH"

# Verificar se KNOWLEDGE.md existe
if [ ! -f "$KNOWLEDGE_FILE" ]; then
    log_change "ERRO: KNOWLEDGE.md não encontrado em $KNOWLEDGE_FILE"
    exit 0
fi

# Verificar se o arquivo já está no KNOWLEDGE.md
if grep -q "$FILE_PATH" "$KNOWLEDGE_FILE" 2>/dev/null; then
    # Arquivo já documentado, apenas atualizar timestamp
    log_change "Arquivo já documentado, atualizando timestamp"
else
    # Arquivo novo - adicionar ao KNOWLEDGE.md
    log_change "Novo arquivo detectado, adicionando ao KNOWLEDGE.md"

    # Determinar a seção baseado no path
    SECTION=""
    if [[ "$FILE_PATH" == frontend/src/components/* ]]; then
        SECTION="Frontend - Componentes UI"
    elif [[ "$FILE_PATH" == frontend/src/hooks/* ]]; then
        SECTION="Frontend - Hooks de Automacao"
    elif [[ "$FILE_PATH" == frontend/src/api/* ]] || [[ "$FILE_PATH" == frontend/src/types/* ]]; then
        SECTION="Frontend - API e Types"
    elif [[ "$FILE_PATH" == backend/src/models/* ]]; then
        SECTION="Backend - Models"
    elif [[ "$FILE_PATH" == backend/src/schemas/* ]]; then
        SECTION="Backend - Schemas e Validacao"
    elif [[ "$FILE_PATH" == backend/src/repositories/* ]]; then
        SECTION="Backend - Repository"
    elif [[ "$FILE_PATH" == backend/src/routes/* ]]; then
        SECTION="Backend - Routes"
    elif [[ "$FILE_PATH" == backend/src/services/* ]]; then
        SECTION="Backend - Services"
    fi

    if [ -n "$SECTION" ]; then
        # Extrair nome do arquivo para descrição
        FILENAME=$(basename "$FILE_PATH")

        # Adicionar entrada após a seção correspondente
        # Usando sed para inserir após a linha da tabela da seção
        TEMP_FILE=$(mktemp)

        awk -v section="$SECTION" -v path="$FILE_PATH" -v desc="Novo arquivo (revisar descrição)" '
        {
            print
            if ($0 ~ section) {
                # Pular próximas 3 linhas (header da tabela)
                for (i=0; i<3; i++) {
                    getline
                    print
                }
                # Adicionar nova entrada
                printf "| `%s` | %s |\n", path, desc
            }
        }
        ' "$KNOWLEDGE_FILE" > "$TEMP_FILE"

        mv "$TEMP_FILE" "$KNOWLEDGE_FILE"
        log_change "Adicionado $FILE_PATH na seção '$SECTION'"
    fi
fi

# Atualizar timestamp de última atualização
CURRENT_DATE=$(date '+%Y-%m-%d')

# Encontrar linha do timestamp atual e substituir
if grep -q "^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}$" "$KNOWLEDGE_FILE"; then
    # Substituir data existente
    sed -i '' "s/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}$/$CURRENT_DATE/" "$KNOWLEDGE_FILE"
fi

log_change "Sync concluído para $FILE_PATH"

exit 0
