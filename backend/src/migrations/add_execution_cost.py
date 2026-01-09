"""
Migração para adicionar campo de custo (execution_cost) à tabela executions.

Execute este script para atualizar o esquema do banco:
    python -m backend.src.migrations.add_execution_cost
"""

import asyncio
from sqlalchemy import text
from backend.src.database import engine, create_tables

async def add_execution_cost_field():
    """Adiciona campo execution_cost à tabela executions"""

    async with engine.begin() as conn:
        try:
            # Verificar se a coluna já existe
            result = await conn.execute(text("PRAGMA table_info(executions)"))
            columns = [row[1] for row in result.fetchall()]

            if 'execution_cost' not in columns:
                print("Adicionando campo 'execution_cost' à tabela executions...")
                await conn.execute(text("""
                    ALTER TABLE executions
                    ADD COLUMN execution_cost NUMERIC(10, 6);
                """))
                print("Campo execution_cost adicionado com sucesso!")
            else:
                print("Campo execution_cost já existe, pulando migração.")

        except Exception as e:
            print(f"Erro ao adicionar campo: {e}")
            # Se houver erro, continuar
            pass

async def main():
    """Executa a migração"""
    print("Iniciando migração para adicionar campo de custo...")

    # Primeiro garantir que as tabelas existem
    print("Criando/atualizando tabelas...")
    await create_tables()

    # Adicionar novo campo
    await add_execution_cost_field()

    print("Migração concluída!")

if __name__ == "__main__":
    asyncio.run(main())
