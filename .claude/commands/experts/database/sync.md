---
description: Sincroniza o knowledge base do Database Expert quando houver mudancas no codigo
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Sync: Database Expert

## Proposito

Manter o knowledge base e os comandos do agent de database atualizados quando houver mudancas no codigo.

## Quando Executar

Execute este comando quando:
- Novos models foram criados em `backend/src/models/`
- Novos repositories foram criados em `backend/src/repositories/`
- Novas migrations foram adicionadas em `backend/migrations/`
- Campos foram adicionados/removidos dos models existentes
- Novos services de banco foram criados
- Schemas foram modificados

## Processo de Sync

### Passo 1: Detectar Mudancas Recentes

Verificar mudancas via git:

```bash
git diff --name-only HEAD~10 -- backend/src/models/ backend/src/repositories/ backend/src/schemas/ backend/migrations/ backend/src/database*.py backend/src/services/*metric* backend/src/services/migration*
```

### Passo 2: Varrer Arquivos Atuais

Usar Glob para listar arquivos atuais:

```
backend/src/models/*.py
backend/src/repositories/*.py
backend/src/schemas/*.py
backend/migrations/*.sql
backend/src/database*.py
```

### Passo 3: Comparar com KNOWLEDGE.md

Para cada arquivo encontrado:
1. Verificar se esta listado no KNOWLEDGE.md
2. Identificar novos arquivos que deveriam ser incluidos
3. Identificar arquivos obsoletos que deveriam ser removidos
4. Verificar se descricoes estao atualizadas

### Passo 4: Atualizar Models

Para models novos ou modificados:
1. Ler o arquivo e extrair campos da tabela
2. Atualizar a secao de "Tabelas Principais" no KNOWLEDGE.md
3. Atualizar a secao de "Enums Importantes" se houver novos enums

### Passo 5: Atualizar Migrations

Para novas migrations:
1. Listar todas em `backend/migrations/`
2. Adicionar novas ao KNOWLEDGE.md com descricao da mudanca
3. Manter ordem numerica

### Passo 6: Atualizar Services

Para novos services relacionados a banco:
1. Verificar `backend/src/services/`
2. Adicionar services novos que manipulam banco de dados
3. Remover services que nao existem mais

### Passo 7: Validar e Atualizar Sub-comandos

Verificar se os sub-comandos ainda fazem sentido:
- `/database/query` - paths de repositories ainda validos?
- `/database/migrate` - path de migrations correto?
- `/database/schema` - paths de models corretos?
- `/database/debug` - arquivos de conexao corretos?

## Arquivos a Verificar

### Core
| Glob Pattern | Descricao |
|--------------|-----------|
| `backend/src/database*.py` | Conexao e manager |
| `backend/src/config/settings.py` | Configuracoes |

### Models
| Glob Pattern | Descricao |
|--------------|-----------|
| `backend/src/models/*.py` | Models ORM |

### Repositories
| Glob Pattern | Descricao |
|--------------|-----------|
| `backend/src/repositories/*.py` | Data Access |

### Schemas
| Glob Pattern | Descricao |
|--------------|-----------|
| `backend/src/schemas/*.py` | Pydantic schemas |

### Migrations
| Glob Pattern | Descricao |
|--------------|-----------|
| `backend/migrations/*.sql` | SQL migrations |

### Services
| Glob Pattern | Descricao |
|--------------|-----------|
| `backend/src/services/migration*.py` | Migration service |
| `backend/src/services/metrics*.py` | Metrics services |
| `backend/src/services/auto_cleanup*.py` | Cleanup service |

## Output Esperado

Ao finalizar, reporte:

```
## Sync Database Expert - Resultado

### Arquivos Adicionados
- `path/novo_arquivo.py` - Descricao

### Arquivos Removidos
- `path/arquivo_antigo.py` - Motivo: nao existe mais

### Descricoes Atualizadas
- `path/arquivo.py` - Antes: X, Agora: Y

### Tabelas Atualizadas
- `tabela_x` - Novos campos: campo1, campo2

### Sub-comandos Afetados
- `/database/query` - Atualizado path de X

### KNOWLEDGE.md
- [ ] Atualizado
- [ ] Nenhuma mudanca necessaria
```

## Argumentos

$ARGUMENTS - Opcional: especificar o que verificar (ex: "models", "migrations", "all")
