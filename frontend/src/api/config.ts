/**
 * Configuração centralizada de APIs
 */
const getBaseUrl = () => {
  // Se tem variável de ambiente, usar ela
  if (import.meta.env.VITE_API_URL) {
    return import.meta.env.VITE_API_URL;
  }
  // Em produção (não localhost), usar a mesma origem
  if (typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
    return `${window.location.protocol}//${window.location.host}`;
  }
  // Default para desenvolvimento
  return 'http://localhost:3001';
};

const getWsUrl = () => {
  if (import.meta.env.VITE_WS_URL) {
    return import.meta.env.VITE_WS_URL;
  }
  const baseUrl = getBaseUrl();
  return baseUrl.replace(/^http/, 'ws');
};

export const API_CONFIG = {
  // URL base do backend
  BASE_URL: getBaseUrl(),

  // URL base do WebSocket
  WS_URL: getWsUrl(),

  // Timeouts padrão
  TIMEOUT: 30000,

  // Retry configuration
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000,
} as const;

// Endpoints específicos
export const API_ENDPOINTS = {
  // Cards
  cards: `${API_CONFIG.BASE_URL}/api/cards`,

  // Projects
  projects: {
    load: `${API_CONFIG.BASE_URL}/api/projects/load`,
    current: `${API_CONFIG.BASE_URL}/api/projects/current`,
    recent: `${API_CONFIG.BASE_URL}/api/projects/recent`,
  },

  // Images
  images: `${API_CONFIG.BASE_URL}/api/images`,

  // Agent
  agent: {
    stream: `${API_CONFIG.BASE_URL}/api/cards`,
  },

  // Logs
  logs: `${API_CONFIG.BASE_URL}/api/logs`,

  // Execution endpoints
  execution: {
    plan: `${API_CONFIG.BASE_URL}/api/execute-plan`,
    implement: `${API_CONFIG.BASE_URL}/api/execute-implement`,
    test: `${API_CONFIG.BASE_URL}/api/execute-test`,
    review: `${API_CONFIG.BASE_URL}/api/execute-review`,
    expertTriage: `${API_CONFIG.BASE_URL}/api/execute-expert-triage`,
  },

  // Git worktree isolation endpoints
  branches: `${API_CONFIG.BASE_URL}/api/branches`,
  cleanupWorktrees: `${API_CONFIG.BASE_URL}/api/cleanup-orphan-worktrees`,

  // Expert agents endpoints
  experts: {
    triage: `${API_CONFIG.BASE_URL}/api/expert-triage`,
    sync: `${API_CONFIG.BASE_URL}/api/expert-sync`,
  },

  // Live spectator endpoints
  live: {
    status: `${API_CONFIG.BASE_URL}/api/live/status`,
    projects: `${API_CONFIG.BASE_URL}/api/live/projects`,
    voting: `${API_CONFIG.BASE_URL}/api/live/voting`,
    vote: `${API_CONFIG.BASE_URL}/api/live/vote`,
  },
} as const;

// WebSocket endpoints centralizados
export const WS_ENDPOINTS = {
  // Cards WebSocket
  cards: `${API_CONFIG.WS_URL}/api/cards/ws`,

  // Execution WebSocket (com cardId dinâmico)
  execution: (cardId: string) => `${API_CONFIG.WS_URL}/api/execution/ws/${cardId}`,

  // Chat WebSocket (com sessionId dinâmico)
  chat: (sessionId: string) => `${API_CONFIG.WS_URL}/api/chat/ws/${sessionId}`,

  // Live spectator WebSocket
  live: `${API_CONFIG.WS_URL}/api/live/ws`,
} as const;