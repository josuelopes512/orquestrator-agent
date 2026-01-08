#!/usr/bin/env python3
"""
Script para migrar e consolidar databases SQLite.

Este script verifica databases redundantes, identifica dados únicos
e mescla com o database principal (auth.db).
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple


class DatabaseMigrator:
    """Gerencia a migração e consolidação de databases SQLite."""

    def __init__(self, main_db_path: str = "backend/auth.db"):
        """
        Inicializa o migrador de databases.

        Args:
            main_db_path: Caminho para o database principal (auth.db)
        """
        self.main_db_path = Path(main_db_path)
        self.backup_dir = Path("backups/databases_backup")
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def analyze_database(self, db_path: Path) -> dict:
        """
        Analisa um database e retorna informações sobre suas tabelas e dados.

        Args:
            db_path: Caminho para o database a ser analisado

        Returns:
            Dicionário com informações do database
        """
        if not db_path.exists():
            return {"exists": False}

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Obter lista de tabelas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]

        # Contar registros em cada tabela
        table_counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            table_counts[table] = cursor.fetchone()[0]

        total_records = sum(table_counts.values())

        conn.close()

        return {
            "exists": True,
            "path": str(db_path),
            "size": db_path.stat().st_size,
            "tables": tables,
            "table_counts": table_counts,
            "total_records": total_records,
            "is_empty": total_records == 0
        }

    def backup_database(self, db_path: Path) -> Path:
        """
        Cria um backup de um database.

        Args:
            db_path: Caminho para o database a fazer backup

        Returns:
            Caminho para o arquivo de backup
        """
        if not db_path.exists():
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{db_path.stem}_{timestamp}.db.backup"
        backup_path = self.backup_dir / backup_name

        shutil.copy2(db_path, backup_path)
        print(f"✓ Backup criado: {backup_path}")

        return backup_path

    def merge_databases(self, source_db: Path, target_db: Path, tables: List[str]) -> int:
        """
        Mescla dados de um database origem para um database destino.

        Args:
            source_db: Database origem
            target_db: Database destino
            tables: Lista de tabelas a mesclar

        Returns:
            Número total de registros mesclados
        """
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)

        total_merged = 0

        for table in tables:
            # Obter dados da tabela origem
            source_cursor = source_conn.cursor()
            source_cursor.execute(f"SELECT * FROM {table}")
            rows = source_cursor.fetchall()

            if not rows:
                continue

            # Obter estrutura da tabela
            source_cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in source_cursor.fetchall()]

            # Inserir no database destino
            target_cursor = target_conn.cursor()
            placeholders = ','.join(['?' for _ in columns])

            try:
                target_cursor.executemany(
                    f"INSERT OR IGNORE INTO {table} VALUES ({placeholders})",
                    rows
                )
                target_conn.commit()
                merged_count = target_cursor.rowcount
                total_merged += merged_count
                print(f"  ✓ Mesclados {merged_count} registros de {table}")
            except sqlite3.Error as e:
                print(f"  ✗ Erro ao mesclar {table}: {e}")

        source_conn.close()
        target_conn.close()

        return total_merged

    def migrate_kanban_to_auth(self) -> bool:
        """
        Mescla dados únicos do kanban.db para auth.db.

        Returns:
            True se a migração foi bem-sucedida
        """
        kanban_db = Path("backend/kanban.db")

        print("\n=== Migrando kanban.db para auth.db ===")

        # Analisar kanban.db
        kanban_info = self.analyze_database(kanban_db)

        if not kanban_info["exists"]:
            print("✗ kanban.db não encontrado")
            return False

        if kanban_info["is_empty"]:
            print("✓ kanban.db está vazio, nenhuma migração necessária")
            return True

        print(f"kanban.db possui {kanban_info['total_records']} registros")

        # Fazer backup antes de mesclar
        self.backup_database(kanban_db)

        # Mesclar dados
        merged = self.merge_databases(
            kanban_db,
            self.main_db_path,
            kanban_info["tables"]
        )

        print(f"✓ {merged} registros mesclados com sucesso")
        return True

    def analyze_all_databases(self) -> dict:
        """
        Analisa todos os databases do projeto.

        Returns:
            Dicionário com análise de cada database
        """
        databases = {
            "main": Path("backend/auth.db"),
            "kanban": Path("backend/kanban.db"),
            "orchestrator": Path("backend/orchestrator.db"),
            "database": Path("backend/database.db"),
            "root_auth": Path("auth.db"),
            "claude_db": Path(".claude/database.db")
        }

        results = {}

        print("\n=== Análise de Databases ===\n")

        for name, path in databases.items():
            info = self.analyze_database(path)
            results[name] = info

            if info["exists"]:
                status = "VAZIO" if info["is_empty"] else f"{info['total_records']} registros"
                size_kb = info["size"] / 1024
                print(f"{name:15} | {size_kb:8.2f} KB | {status}")
            else:
                print(f"{name:15} | NÃO EXISTE")

        return results

    def cleanup_empty_databases(self, dry_run: bool = False) -> List[Path]:
        """
        Remove databases vazios e não utilizados.

        Args:
            dry_run: Se True, apenas mostra o que seria removido

        Returns:
            Lista de databases removidos
        """
        databases_to_check = [
            Path("backend/orchestrator.db"),
            Path("backend/database.db"),
            Path("backend/kanban.db"),  # Após migração
            Path("auth.db")  # Duplicado na raiz
        ]

        removed = []

        print(f"\n=== {'Simulação de ' if dry_run else ''}Limpeza de Databases ===\n")

        for db_path in databases_to_check:
            if not db_path.exists():
                continue

            info = self.analyze_database(db_path)

            if info["is_empty"]:
                if dry_run:
                    print(f"[DRY RUN] Removeria: {db_path}")
                else:
                    # Fazer backup antes de remover
                    self.backup_database(db_path)
                    db_path.unlink()
                    print(f"✓ Removido: {db_path}")
                removed.append(db_path)

        return removed


def main():
    """Função principal do script de migração."""
    print("=" * 60)
    print("Database Migration Tool")
    print("=" * 60)

    migrator = DatabaseMigrator()

    # Etapa 1: Analisar todos os databases
    results = migrator.analyze_all_databases()

    # Etapa 2: Migrar kanban.db se necessário
    migrator.migrate_kanban_to_auth()

    # Etapa 3: Limpeza (dry run primeiro)
    print("\n--- Simulação de Limpeza ---")
    migrator.cleanup_empty_databases(dry_run=True)

    # Confirmar limpeza
    response = input("\nDeseja prosseguir com a limpeza? (s/N): ")
    if response.lower() == 's':
        migrator.cleanup_empty_databases(dry_run=False)
        print("\n✓ Limpeza concluída!")
    else:
        print("\n✗ Limpeza cancelada")

    # Análise final
    print("\n--- Estado Final ---")
    migrator.analyze_all_databases()

    print("\n" + "=" * 60)
    print("Migração concluída!")
    print("=" * 60)


if __name__ == "__main__":
    main()
