# Arquitetura de Databases

## Visão Geral

O projeto utiliza uma arquitetura de databases multi-camada com SQLite, separando o database principal do sistema de databases isolados por projeto.

## Estrutura de Databases

### 1. Database Principal (Raiz)

**Localização:** `backend/auth.db`

**Propósito:** Database principal do sistema que contém dados globais e centralizados.

**Tabelas:**
- `users` - Usuários do sistema
- `cards` - Cards/tarefas do Kanban
- `executions` - Histórico de execuções de agentes
- `execution_logs` - Logs detalhados de execuções
- `active_project` - Projeto ativo no momento

**Configuração:**
```python
# backend/src/config.py
database_url: str = "sqlite+aiosqlite:///./backend/auth.db"
```

**Conexão:**
O database principal é acessado através das rotas da API e gerenciado pelo SQLAlchemy.

### 2. Databases de Projeto (Isolados)

**Localização:** `.claude/database.db` (dentro de cada projeto)

**Propósito:** Cada projeto tem seu próprio database isolado para dados específicos do projeto.

**Criação Automática:**
Quando um projeto é inicializado, o `DatabaseManager` automaticamente:
1. Cria a pasta `.claude/` no diretório do projeto
2. Cria `database.db` dentro dessa pasta
3. Inicializa as tabelas necessárias

**Exemplo:**
```
/Users/eduardo/projeto-a/.claude/database.db
/Users/eduardo/projeto-b/.claude/database.db
```

### 3. Database de Histórico (Global)

**Localização:** `backend/.project_data/project_history.db`

**Propósito:** Armazena histórico global de projetos acessados.

**Tabelas:**
- Informações sobre projetos visitados
- Timestamps de acesso
- Metadados de projetos

## Migração de Databases Legados

### Databases Removidos

Os seguintes databases foram identificados como vazios ou redundantes e **removidos**:

| Database | Status | Ação |
|----------|--------|------|
| `backend/orchestrator.db` | Vazio (0 bytes) | ✅ Removido |
| `backend/database.db` | Vazio (0 bytes) | ✅ Removido |
| `backend/kanban.db` | Vazio (0 registros) | ✅ Removido |
| `auth.db` (raiz) | Duplicado | ✅ Removido |

### Backup

Todos os databases foram copiados para `backups/databases_backup/` antes de qualquer remoção.

### Migração Automática

O sistema possui migração automática de databases legados:

```python
# backend/src/database_manager.py
# Se existe database em .project_data e não existe em .claude,
# o sistema automaticamente copia para .claude
if os.path.exists(legacy_db_path) and not os.path.exists(db_path):
    shutil.copy2(legacy_db_path, db_path)
    logger.info(f"Migrated database from {legacy_db_path} to {db_path}")
```

## Fluxo de Dados

```
┌─────────────────────────────────────────────────────────┐
│                    APLICAÇÃO                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ├── Dados Globais (auth, users, cards)
                           │
                           ▼
                ┌──────────────────────┐
                │  backend/auth.db     │
                │  (Database Principal)│
                └──────────────────────┘
                           │
                           ├── Dados de Projeto Específico
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  .claude/database.db (Projeto A)    │
         │  .claude/database.db (Projeto B)    │
         │  .claude/database.db (Projeto C)    │
         └─────────────────────────────────────┘
                           │
                           ├── Histórico de Projetos
                           │
                           ▼
         ┌─────────────────────────────────────┐
         │  backend/.project_data/             │
         │  project_history.db                 │
         └─────────────────────────────────────┘
```

## Gerenciamento de Databases

### DatabaseManager

O `DatabaseManager` (`backend/src/database_manager.py`) é responsável por:

1. **Inicializar databases de projeto**
   - Criar diretório `.claude/`
   - Criar e configurar `database.db`
   - Migrar databases legados se necessário

2. **Gerenciar múltiplas conexões**
   - Manter engines separados por projeto
   - Gerenciar sessions por projeto
   - Controlar projeto ativo

3. **Isolamento de dados**
   - Cada projeto tem seu próprio database
   - Dados não vazam entre projetos
   - Limpeza automática de conexões

### Exemplo de Uso

```python
from backend.src.database_manager import db_manager

# Inicializar database para um projeto
project_id = await db_manager.initialize_project_database("/path/to/project")

# Obter session do projeto ativo
session_factory = db_manager.get_current_session()

# Usar session
async with session_factory() as session:
    # Operações no database do projeto
    pass

# Resetar para projeto raiz
db_manager.reset()
```

## Variáveis de Ambiente

Configure o database através do arquivo `backend/.env`:

```env
# Database principal
DATABASE_URL=sqlite+aiosqlite:///./backend/auth.db

# Configurações de multi-database
PROJECT_DATA_DIR=.project_data
STORE_DB_IN_PROJECT=true
AUTO_MIGRATE_LEGACY_DB=true
```

## Troubleshooting

### Database não encontrado

**Problema:** Erro ao conectar ao database

**Solução:**
1. Verificar se `backend/auth.db` existe
2. Verificar permissões de leitura/escrita
3. Verificar configuração em `backend/src/config.py`

### Múltiplos databases criados

**Problema:** Databases duplicados em diferentes locais

**Solução:**
1. Executar script de migração: `python backend/scripts/migrate_databases.py`
2. Verificar configuração `STORE_DB_IN_PROJECT=true`
3. Remover databases vazios manualmente

### Migração de dados antigos

**Problema:** Precisa migrar dados de database antigo

**Solução:**
```bash
cd backend
python scripts/migrate_databases.py
```

## Manutenção

### Backup Manual

```bash
# Fazer backup do database principal
cp backend/auth.db "backups/auth.db.$(date +%Y%m%d_%H%M%S)"

# Fazer backup de todos os databases de projetos
find . -name "database.db" -path "*/.claude/*" -exec cp {} backups/ \;
```

### Limpeza de Databases Antigos

```bash
# Remover databases em .project_data (após migração)
rm -rf backend/.project_data/*/database.db
```

### Verificar Integridade

```bash
# Verificar database principal
sqlite3 backend/auth.db "PRAGMA integrity_check;"

# Verificar database de projeto
sqlite3 .claude/database.db "PRAGMA integrity_check;"
```

## Referências

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLAlchemy Async Documentation](https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html)
- [Pydantic Settings](https://docs.pydantic.dev/latest/usage/settings/)

## Histórico de Mudanças

### 2025-01-07 - Unificação de Databases
- ✅ Confirmado `backend/auth.db` como database principal
- ✅ Removidos databases vazios: `orchestrator.db`, `database.db`, `kanban.db`
- ✅ Removido database duplicado `auth.db` na raiz
- ✅ Atualizado `config.py` para apontar para `backend/auth.db`
- ✅ Documentada arquitetura de databases
- ✅ Criado script de migração `backend/scripts/migrate_databases.py`
- ✅ Adicionados comentários explicativos em `database_manager.py`
