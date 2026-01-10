---
description: Debug de problemas de banco de dados
---

# Database Debug

Sub-comando para investigar e resolver problemas de banco de dados.

## Comandos de Diagnostico

### Verificar Estrutura

```bash
# Listar tabelas
sqlite3 backend/auth.db ".tables"

# Ver schema de tabela
sqlite3 backend/auth.db ".schema cards"

# Ver indices
sqlite3 backend/auth.db ".indices cards"
```

### Verificar Dados

```bash
# Contar registros
sqlite3 backend/auth.db "SELECT COUNT(*) FROM cards"

# Ver ultimos registros
sqlite3 backend/auth.db "SELECT id, title, column_id FROM cards ORDER BY created_at DESC LIMIT 10"

# Verificar migrations aplicadas
sqlite3 backend/auth.db "SELECT * FROM applied_migrations"
```

### Verificar Integridade

```bash
# Check de integridade
sqlite3 backend/auth.db "PRAGMA integrity_check"

# Foreign keys
sqlite3 backend/auth.db "PRAGMA foreign_key_check"
```

## Problemas Comuns

### 1. Database Locked

**Sintoma**: `sqlite3.OperationalError: database is locked`

**Causas**:
- Multiplos processos acessando o banco
- Transacao nao commitada

**Solucao**:
```python
# Usar timeout maior
engine = create_async_engine(url, connect_args={"timeout": 30})

# Verificar conexoes abertas
sqlite3 backend/auth.db ".databases"
```

### 2. Migration Falhou

**Sintoma**: Erro ao aplicar migration

**Diagnostico**:
```bash
# Ver migrations aplicadas
sqlite3 backend/auth.db "SELECT * FROM applied_migrations ORDER BY applied_at"

# Verificar se tabela/coluna ja existe
sqlite3 backend/auth.db ".schema tabela"
```

**Solucao**:
- Se parcialmente aplicada, corrigir manualmente
- Usar `IF NOT EXISTS` em CREATE
- Verificar se coluna ja existe antes de ALTER

### 3. Foreign Key Violation

**Sintoma**: `FOREIGN KEY constraint failed`

**Diagnostico**:
```bash
# Verificar registros orfaos
sqlite3 backend/auth.db "
SELECT e.id FROM executions e
LEFT JOIN cards c ON e.card_id = c.id
WHERE c.id IS NULL
"
```

**Solucao**:
```sql
-- Deletar registros orfaos
DELETE FROM executions WHERE card_id NOT IN (SELECT id FROM cards);
```

### 4. Dados Corrompidos

**Sintoma**: Erros de leitura, dados inconsistentes

**Diagnostico**:
```bash
# Verificar integridade
sqlite3 backend/auth.db "PRAGMA integrity_check"

# Verificar journal
ls -la backend/auth.db*
```

**Solucao**:
```bash
# Backup e recriacao
sqlite3 backend/auth.db ".backup backup.db"
sqlite3 backup.db "VACUUM"
```

### 5. Performance Lenta

**Diagnostico**:
```bash
# Analisar query
sqlite3 backend/auth.db "EXPLAIN QUERY PLAN SELECT * FROM cards WHERE column_id = 'done'"

# Ver estatisticas
sqlite3 backend/auth.db "ANALYZE"
```

**Solucao**:
```sql
-- Criar indice
CREATE INDEX idx_cards_column ON cards(column_id);

-- Vacuum para otimizar
VACUUM;
```

## Logs e Monitoramento

### Habilitar Logs SQLAlchemy

```python
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
```

### Ver Queries Executadas

```python
# Em settings.py ou database.py
engine = create_async_engine(url, echo=True)
```

## Scripts Uteis

### Backup

```bash
# Backup com timestamp
cp backend/auth.db "backups/auth_$(date +%Y%m%d_%H%M%S).db"
```

### Reset (CUIDADO!)

```bash
# Remove e recria banco
rm backend/auth.db
# Reiniciar aplicacao para recriar tabelas
```

### Dump de Dados

```bash
# Exportar como SQL
sqlite3 backend/auth.db ".dump" > backup.sql

# Exportar tabela especifica
sqlite3 backend/auth.db ".dump cards" > cards_backup.sql
```

## Instrucoes

Ao receber solicitacao de debug:

1. Identifique o sintoma exato
2. Execute comandos de diagnostico
3. Verifique logs da aplicacao
4. Identifique causa raiz
5. Proponha solucao com minimo impacto

$ARGUMENTS
