"""
Script para migrar todos os databases do sistema (auth.db e project databases).
"""

import asyncio
import sqlite3
from pathlib import Path


def add_column_if_not_exists(db_path: Path, table: str, column: str, column_type: str):
    """Adiciona coluna a uma tabela se ela não existir."""
    if not db_path.exists():
        print(f"Database {db_path} não existe, pulando...")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Verificar se a tabela existe
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"Tabela {table} não existe em {db_path}, pulando...")
            conn.close()
            return

        # Verificar se a coluna já existe
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]

        if column not in columns:
            print(f"Adicionando coluna {column} à tabela {table} em {db_path}...")
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")
            conn.commit()
            print(f"✓ Coluna {column} adicionada com sucesso!")
        else:
            print(f"✓ Coluna {column} já existe em {db_path}")

        conn.close()
    except Exception as e:
        print(f"✗ Erro ao processar {db_path}: {e}")


async def main():
    """Migra todos os databases."""
    print("=" * 60)
    print("Migrando todos os databases para adicionar execution_cost")
    print("=" * 60)

    # Lista de databases para migrar
    databases = [
        Path("backend/auth.db"),
        Path(".claude/database.db"),
        Path("auth.db"),
        Path("backend/.project_data/project_history.db"),
    ]

    # Adicionar databases de projetos em .project_data
    project_data_dir = Path("backend/.project_data")
    if project_data_dir.exists():
        for project_dir in project_data_dir.iterdir():
            if project_dir.is_dir():
                db_path = project_dir / "database.db"
                if db_path.exists():
                    databases.append(db_path)

    # Processar cada database
    for db_path in databases:
        print(f"\n📁 Processando: {db_path}")
        add_column_if_not_exists(
            db_path=db_path,
            table="executions",
            column="execution_cost",
            column_type="NUMERIC(10, 6)"
        )

    print("\n" + "=" * 60)
    print("✓ Migração concluída!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
