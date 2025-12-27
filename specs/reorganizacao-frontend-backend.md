# Plano: Reorganização Frontend/Backend

## Objetivo
Separar o projeto em duas pastas distintas (`frontend/` e `backend/`) para melhor organização e manutenibilidade.

## Estrutura Atual
```
orquestrator-agent/
├── package.json          # Frontend + scripts gerais
├── index.html            # Frontend
├── vite.config.ts        # Frontend
├── tsconfig.json         # Frontend
├── tsconfig.node.json    # Frontend
├── src/                  # Frontend React
├── server/               # Backend (já separado)
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
├── specs/
├── docs/
└── .claude/
```

## Estrutura Proposta
```
orquestrator-agent/
├── package.json          # Scripts do monorepo (dev, build, setup)
├── frontend/
│   ├── package.json      # Dependências React/Vite
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   └── src/
├── backend/
│   ├── package.json      # Dependências Express/Claude SDK
│   ├── tsconfig.json
│   └── src/
├── specs/
├── docs/
└── .claude/
```

## Checklist de Implementação

### 1. Criar estrutura de pastas
- [x] Criar pasta `frontend/`
- [x] Renomear pasta `server/` para `backend/`

### 2. Mover arquivos do frontend
- [x] Mover `src/` para `frontend/src/`
- [x] Mover `index.html` para `frontend/`
- [x] Mover `vite.config.ts` para `frontend/`
- [x] Mover `tsconfig.json` para `frontend/`
- [x] Mover `tsconfig.node.json` para `frontend/`

### 3. Criar package.json do frontend
- [x] Criar `frontend/package.json` com dependências React/Vite
- [x] Remover dependências do package.json raiz

### 4. Atualizar package.json raiz
- [x] Atualizar script `dev` para apontar para novas pastas
- [x] Atualizar script `dev:frontend` para usar `--prefix frontend`
- [x] Atualizar script `dev:backend` para usar `--prefix backend`
- [x] Atualizar script `build` para frontend
- [x] Atualizar script `setup` para instalar em ambas as pastas

### 5. Atualizar configurações do Vite
- [x] Verificar se paths no vite.config.ts precisam de ajuste (não precisou)

### 6. Atualizar .gitignore
- [x] Adicionar `frontend/node_modules` (já coberto por node_modules/)
- [x] Adicionar `frontend/dist` (já coberto por dist/)
- [x] Atualizar paths se necessário (não precisou)

### 7. Atualizar imports do frontend (se necessário)
- [x] Verificar se há imports que referenciam paths antigos (não há)

## Arquivos Afetados
- `package.json` (raiz) - modificar
- `frontend/package.json` - criar
- `frontend/index.html` - mover
- `frontend/vite.config.ts` - mover
- `frontend/tsconfig.json` - mover
- `frontend/tsconfig.node.json` - mover
- `frontend/src/*` - mover
- `backend/` - renomear de server/
- `.gitignore` - atualizar

## Testes
- [x] Executar `npm run setup` e verificar instalação
- [x] Executar `npm run dev` e verificar se frontend inicia
- [x] Executar `npm run dev:backend` e verificar se backend inicia
- [x] Testar funcionalidade do Kanban board (build funcionando)

## Rollback
Se algo der errado, a estrutura pode ser revertida usando git:
```bash
git checkout -- .
```
