import React from 'react';
import styles from './EmptyState.module.css';

interface EmptyStateProps {
  type: 'backlog' | 'done' | 'plan' | 'implement' | 'test' | 'review';
}

interface StateConfig {
  icon: string;
  title: string;
  message: string;
  action?: string;
}

const stateConfigs: Record<string, StateConfig> = {
  backlog: {
    icon: '🌱',
    title: 'Pronto para começar',
    message: 'Adicione sua primeira tarefa e veja a mágica acontecer',
    action: 'Criar primeira tarefa'
  },
  plan: {
    icon: '🎯',
    title: 'Nenhum plano em andamento',
    message: 'Mova cards para cá para iniciar o planejamento',
    action: null
  },
  implement: {
    icon: '⚡',
    title: 'Aguardando implementação',
    message: 'Os cards aprovados aparecerão aqui para desenvolvimento',
    action: null
  },
  test: {
    icon: '🧪',
    title: 'Pronto para testes',
    message: 'Implementações concluídas aparecerão aqui para validação',
    action: null
  },
  review: {
    icon: '👀',
    title: 'Nada para revisar',
    message: 'Tarefas testadas aparecerão aqui para revisão final',
    action: null
  },
  done: {
    icon: '✨',
    title: 'Nada concluído ainda',
    message: 'Continue trabalhando! Suas conquistas aparecerão aqui',
    action: null
  }
};

export const EmptyState: React.FC<EmptyStateProps> = ({ type }) => {
  const config = stateConfigs[type] || stateConfigs.backlog;

  return (
    <div className={styles.emptyState}>
      <div className={styles.emptyIcon}>
        <span className={styles.iconEmoji}>{config.icon}</span>
      </div>
      <h3 className={styles.emptyTitle}>{config.title}</h3>
      <p className={styles.emptyMessage}>{config.message}</p>
      {config.action && (
        <button className={styles.emptyAction}>
          {config.action}
        </button>
      )}
    </div>
  );
};

export default EmptyState;
