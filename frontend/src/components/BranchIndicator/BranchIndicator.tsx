import React from 'react';
import styles from './BranchIndicator.module.css';

interface BranchIndicatorProps {
  branchName: string;
  onClick?: () => void;
}

export const BranchIndicator: React.FC<BranchIndicatorProps> = ({
  branchName,
  onClick
}) => {
  // Mostrar apenas short name (ex: "agent/abc123-1234567890" -> "abc123")
  const shortName = branchName.replace('agent/', '').split('-')[0];

  return (
    <button
      className={styles.branchBadge}
      onClick={onClick}
      title={branchName}
    >
      <span className={styles.icon}>🔀</span>
      <span className={styles.name}>{shortName}</span>
    </button>
  );
};
