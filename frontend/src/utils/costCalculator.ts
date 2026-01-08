/**
 * Utility functions for cost calculation and formatting.
 */

/**
 * Format cost value as USD currency.
 * @param cost - Cost value in USD
 * @returns Formatted cost string (e.g., "$0.05", "$1.23")
 */
export function formatCost(cost: number): string {
  if (cost === 0) return '$0.00';

  // Se o custo for muito pequeno, mostrar em centavos
  if (cost < 0.01) {
    return `$${cost.toFixed(4)}`;
  }

  // Para custos maiores, mostrar 2 casas decimais
  return `$${cost.toFixed(2)}`;
}

/**
 * Format cost value with more precision for tooltips or detailed views.
 * @param cost - Cost value in USD
 * @returns Formatted cost string with 4 decimal places
 */
export function formatCostDetailed(cost: number): string {
  return `$${cost.toFixed(4)}`;
}

/**
 * Get cost color based on value (for visual feedback).
 * @param cost - Cost value in USD
 * @returns Color class or hex color
 */
export function getCostColor(cost: number): string {
  if (cost === 0) return '#999';
  if (cost < 0.10) return '#22c55e'; // Verde - baixo custo
  if (cost < 0.50) return '#3b82f6'; // Azul - custo moderado
  if (cost < 1.00) return '#f59e0b'; // Laranja - custo médio
  return '#ef4444'; // Vermelho - custo alto
}

/**
 * Get a relative cost indicator (low, medium, high).
 * @param cost - Cost value in USD
 * @returns Cost level indicator
 */
export function getCostLevel(cost: number): 'zero' | 'low' | 'medium' | 'high' | 'very-high' {
  if (cost === 0) return 'zero';
  if (cost < 0.10) return 'low';
  if (cost < 0.50) return 'medium';
  if (cost < 1.00) return 'high';
  return 'very-high';
}
