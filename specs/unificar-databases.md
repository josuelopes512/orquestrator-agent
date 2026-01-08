## 1. Resumo

Consolidar e organizar o uso de múltiplos databases SQLite no projeto, centralizando no arquivo `/backend/auth.db` como database principal e removendo databases redundantes e vazios. O problema surgiu da criação de múltiplos arquivos `.db` ao longo do desenvolvimento, causando confusão sobre qual database está efetivamente sendo usado.

---

## 2. Objetivos e Escopo

### Objetivos
- [x] Confirmar `/backend/auth.db` como database principal do projeto
- [x] Remover arquivos de database redundantes e não utilizados
- [x] Atualizar configurações para apontar consistentemente para o database correto
- [x] Documentar a arquitetura de database para evitar confusões futuras
- [x] Ajustar o `DatabaseManager` para trabalhar corretamente com a estrutura unificada

### Fora do Escopo
- Migração para outro sistema de database (PostgreSQL, MySQL, etc.)
- Alteração do schema das tabelas existentes
- Implementação de backup automático

---

## 3. Implementação

### Arquivos a Serem Modificados/Criados

| Arquivo | Ação | Descrição |
|---------|------|-----------|
| `backend/orchestrator.db` | Deletar | Database vazio e não utilizado |
| `backend/database.db` | Deletar | Database vazio e não utilizado |
| `backend/kanban.db` | Analisar/Mesclar | Verificar dados e mesclar com auth.db se necessário |
| `/auth.db` | Deletar | Database duplicado na raiz |
| `.claude/database.db` | Analisar | Verificar se contém dados únicos antes de decidir |
| `backend/src/config.py` | Modificar | Garantir que aponte para auth.db corretamente |
| `backend/src/database_manager.py` | Modificar | Ajustar lógica para usar auth.db como base |
| `backend/.env` | Criar | Criar arquivo .env com DATABASE_URL correto |
| `docs/database-architecture.md` | Criar | Documentar estrutura de databases |

### Detalhes Técnicos

#### 1. Análise dos Databases Existentes

Situação atual dos databases encontrados:
- `/backend/auth.db` (2.15MB) - Database principal com tabelas: active_project, cards, execution_logs, executions, users
- `/backend/kanban.db` (53KB) - Database com as mesmas tabelas que auth.db
- `/backend/orchestrator.db` (0 bytes) - Vazio
- `/backend/database.db` (0 bytes) - Vazio
- `/.claude/database.db` - Database de projeto com as mesmas tabelas
- `/auth.db` - Database duplicado na raiz

#### 2. Configuração Unificada

```python
# backend/src/config.py
class Settings(BaseSettings):
    # Database principal - sempre auth.db no backend
    database_url: str = "sqlite+aiosqlite:///./backend/auth.db"

    # Multi-Database Configuration - para databases de projetos específicos
    project_data_dir: str = ".project_data"
    store_db_in_project: bool = True
```

#### 3. Ajuste do DatabaseManager

O `DatabaseManager` precisa ser ajustado para:
- Usar `auth.db` como database principal/raiz
- Continuar criando databases isolados em `.claude/` para projetos específicos
- Remover referências a databases obsoletos

```python
# backend/src/database_manager.py
class DatabaseManager:
    def __init__(self, base_data_dir: str = ".project_data"):
        # Configurar auth.db como database principal
        self.main_database_path = Path("backend/auth.db")
        # Resto da implementação...
```

#### 4. Script de Migração de Dados

Criar script para verificar e migrar dados do kanban.db se necessário:

```python
# backend/scripts/migrate_databases.py
import sqlite3
import shutil
from pathlib import Path

def merge_kanban_to_auth():
    """Mescla dados únicos do kanban.db para auth.db"""
    kanban_db = Path("backend/kanban.db")
    auth_db = Path("backend/auth.db")

    if kanban_db.exists():
        # Conectar aos dois databases
        kanban_conn = sqlite3.connect(kanban_db)
        auth_conn = sqlite3.connect(auth_db)

        # Verificar dados únicos em kanban.db
        # (implementar lógica de verificação e migração)

        kanban_conn.close()
        auth_conn.close()

        # Fazer backup antes de deletar
        shutil.copy2(kanban_db, "backend/kanban.db.backup")
        kanban_db.unlink()
```

---

## 4. Testes

### Unitários
- [x] Testar que `database_url` aponta para auth.db
- [x] Testar criação de novos projetos com database isolado
- [x] Testar operações CRUD em auth.db
- [x] Verificar que databases obsoletos não são mais criados

### Integração
- [x] Testar fluxo completo de login/autenticação usando auth.db
- [x] Testar criação e gestão de cards
- [x] Testar execução de agentes
- [x] Verificar que múltiplos projetos funcionam com databases isolados

### Manual
- [x] Verificar que aplicação inicia corretamente
- [x] Confirmar que não há erros de database não encontrado
- [x] Testar funcionalidades principais do sistema

---

## 5. Considerações

### Riscos
- **Perda de dados:** Risco de perder dados ao deletar databases - Mitigar com backup antes de qualquer deleção
- **Quebra de funcionalidades:** Sistema pode parar de funcionar se configuração estiver errada - Mitigar com testes completos
- **Referências hardcoded:** Pode haver referências diretas a outros databases no código - Mitigar com busca completa no código

### Dependências
- Nenhuma aprovação externa necessária
- Backup dos databases antes de começar a implementação

### Passos de Implementação
1. Fazer backup de todos os databases existentes
2. Analisar conteúdo do kanban.db e verificar necessidade de migração
3. Atualizar configurações para apontar para auth.db
4. Remover databases vazios e não utilizados
5. Testar sistema completo
6. Documentar arquitetura final