"""Service for calculating execution costs based on token usage and model pricing."""

from decimal import Decimal
from typing import Dict, List

from ..config.pricing import calculate_cost
from ..models.execution import Execution


class CostCalculator:
    """Service for calculating costs of card executions."""

    @staticmethod
    def calculate_execution_cost(execution: Execution) -> Decimal:
        """Calcula o custo de uma execução específica.

        Args:
            execution: Objeto de execução com informações de tokens e modelo

        Returns:
            Custo em USD como Decimal
        """
        if not execution.model:
            return Decimal("0")

        input_tokens = execution.input_tokens or 0
        output_tokens = execution.output_tokens or 0

        return calculate_cost(execution.model, input_tokens, output_tokens)

    @staticmethod
    def calculate_total_cost(executions: List[Execution]) -> Decimal:
        """Calcula o custo total de múltiplas execuções.

        Args:
            executions: Lista de objetos de execução

        Returns:
            Custo total em USD como Decimal
        """
        total = Decimal("0")
        for execution in executions:
            total += CostCalculator.calculate_execution_cost(execution)
        return total

    @staticmethod
    def calculate_cost_breakdown(executions: List[Execution]) -> Dict[str, float]:
        """Calcula o breakdown de custos por tipo de execução.

        Args:
            executions: Lista de objetos de execução

        Returns:
            Dicionário com custos por tipo (plan, implement, test, review) e total
        """
        costs = {
            "totalCost": 0.0,
            "planCost": 0.0,
            "implementCost": 0.0,
            "testCost": 0.0,
            "reviewCost": 0.0,
            "currency": "USD"
        }

        for execution in executions:
            cost = float(CostCalculator.calculate_execution_cost(execution))

            # Mapear tipo de execução para campo de custo
            execution_type = execution.execution_type
            if execution_type == "plan":
                costs["planCost"] += cost
            elif execution_type == "implement":
                costs["implementCost"] += cost
            elif execution_type == "test":
                costs["testCost"] += cost
            elif execution_type == "review":
                costs["reviewCost"] += cost

            costs["totalCost"] += cost

        return costs
