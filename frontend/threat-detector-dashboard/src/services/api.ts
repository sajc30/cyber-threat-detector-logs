import axios from 'axios';

// Environment configuration
const isProduction = process.env.NODE_ENV === 'production';
const isDemoMode = window.location.hostname.includes('github.io') || isProduction;

// API Configuration
const getApiUrl = () => {
  // Check if running in browser vs SSR
  if (typeof window === 'undefined') {
    return 'http://backend:5001';
  }
  
  // Browser environment - try environment variables first, then fallback
  return process.env.REACT_APP_API_URL || 
         process.env.REACT_APP_CONTAINER_API_URL || 
         'http://localhost:5001';
};

const API_BASE_URL = isDemoMode ? '' : getApiUrl();

const api = axios.create({
  baseURL: API_BASE_URL.replace('/api', ''),
  timeout: isDemoMode ? 1000 : 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Mock data for demo mode
const mockData = {
  threats: [
    {
      id: 'THR-001',
      title: 'Suspicious PowerShell Activity',
      description: 'Encoded PowerShell command detected with potential malicious payload',
      severity: 'High',
      status: 'Active',
      source: '192.168.1.45',
      timestamp: '2024-01-20 14:32:15',
      details: 'Base64 encoded PowerShell execution detected'
    },
    {
      id: 'THR-002', 
      title: 'Unusual Network Traffic',
      description: 'Large data transfer to unknown external IP detected',
      severity: 'Medium',
      status: 'Investigating',
      source: '10.0.0.23',
      timestamp: '2024-01-20 14:15:08',
      details: 'Data exfiltration attempt detected'
    },
    {
      id: 'THR-003',
      title: 'Failed Login Attempts',
      description: 'Multiple failed SSH login attempts from external IP',
      severity: 'Low',
      status: 'Mitigated', 
      source: '203.45.67.89',
      timestamp: '2024-01-20 13:45:22',
      details: 'Brute force attack blocked by firewall'
    }
  ],
  metrics: {
    totalThreats: 247,
    activeThreats: 12,
    resolvedToday: 8,
    systemHealth: 98.5,
    avgResponseTime: 1.2,
    threatLevel: 'Medium'
  },
  logs: [
    {
      id: 1,
      timestamp: '2024-01-20 14:35:00',
      level: 'WARNING',
      source: 'Firewall',
      message: 'Blocked connection attempt from 203.45.67.89:4444',
      category: 'Security'
    },
    {
      id: 2,
      timestamp: '2024-01-20 14:34:15',
      level: 'INFO',
      source: 'IDS',
      message: 'Signature update completed successfully',
      category: 'System'
    },
    {
      id: 3,
      timestamp: '2024-01-20 14:33:42',
      level: 'ERROR',
      source: 'Auth',
      message: 'Failed login attempt for user admin from 192.168.1.100',
      category: 'Security'
    }
  ]
};

// Request interceptor
api.interceptors.request.use(
  (config) => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Intercepting API request:', config.url);
    } else {
      console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor  
api.interceptors.response.use(
  (response) => {
    if (!isDemoMode) {
      console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    }
    return response;
  },
  (error) => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: API request failed, returning mock data');
      return Promise.resolve({ data: getMockDataForEndpoint(error.config?.url || '') });
    }
    console.error(`❌ API Error: ${error.response?.status || 'Network Error'} ${error.config?.url}`);
    return Promise.reject(error);
  }
);

// Helper function to get mock data based on endpoint
function getMockDataForEndpoint(url: string) {
  if (url.includes('/threats')) return mockData.threats;
  if (url.includes('/metrics')) return mockData.metrics;
  if (url.includes('/logs')) return mockData.logs;
  if (url.includes('/health')) return { status: 'healthy', message: 'Demo mode active' };
  if (url.includes('/monitoring/start')) return { success: true, message: 'Demo monitoring started' };
  if (url.includes('/monitoring/stop')) return { success: true, message: 'Demo monitoring stopped' };
  
  return { success: true, message: 'Demo mode response' };
}

// Types for API responses
export interface ThreatResponse {
  id: string;
  title: string;
  description: string;
  severity: string;
  status: string;
  source: string;
  timestamp: string;
  details?: string;
}

export interface MetricsResponse {
  totalThreats: number;
  activeThreats: number;
  resolvedToday: number;
  systemHealth: number;
  avgResponseTime: number;
  threatLevel: string;
}

// API functions
export const threatAPI = {
  getAll: async () => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Returning mock threats');
      return { data: mockData.threats };
    }
    return api.get('/api/threats');
  },
  
  getById: async (id: string) => {
    if (isDemoMode) {
      const threat = mockData.threats.find(t => t.id === id);
      return { data: threat || mockData.threats[0] };
    }
    return api.get(`/api/threats/${id}`);
  },
  
  updateStatus: async (id: string, status: string) => {
    if (isDemoMode) {
      console.log(`🎭 Demo Mode: Updated threat ${id} status to ${status}`);
      return { data: { success: true, message: 'Status updated in demo mode' } };
    }
    return api.patch(`/api/threats/${id}`, { status });
  }
};

export const metricsAPI = {
  getDashboard: async () => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Returning mock metrics');
      return { data: mockData.metrics };
    }
    return api.get('/api/metrics/dashboard');
  },
  
  getSystemHealth: async () => {
    if (isDemoMode) {
      return { data: { health: 98.5, status: 'excellent' } };
    }
    return api.get('/api/metrics/health');
  }
};

export const logsAPI = {
  getRecent: async () => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Returning mock logs');
      return { data: mockData.logs };
    }
    return api.get('/api/logs/recent');
  },
  
  search: async (query: string) => {
    if (isDemoMode) {
      const filtered = mockData.logs.filter(log => 
        log.message.toLowerCase().includes(query.toLowerCase())
      );
      return { data: filtered };
    }
    return api.get(`/api/logs/search?q=${encodeURIComponent(query)}`);
  }
};

export const monitoringAPI = {
  start: async () => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Started monitoring simulation');
      return { data: { success: true, message: 'Demo monitoring started' } };
    }
    return api.post('/api/monitoring/start');
  },
  
  stop: async () => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Stopped monitoring simulation');
      return { data: { success: true, message: 'Demo monitoring stopped' } };
    }
    return api.post('/api/monitoring/stop');
  },
  
  getStatus: async () => {
    if (isDemoMode) {
      return { data: { status: 'active', message: 'Demo monitoring active' } };
    }
    return api.get('/api/monitoring/status');
  }
};

export const healthAPI = {
  check: async () => {
    if (isDemoMode) {
      console.log('🎭 Demo Mode: Health check simulation');
      return { 
        data: { 
          status: 'healthy', 
          message: 'Demo mode - all systems operational',
          uptime: '99.9%',
          version: '1.0.0-demo'
        } 
      };
    }
    return api.get('/api/health');
  }
};

// Demo mode indicator
export const getDemoStatus = () => ({
  isDemoMode,
  isProduction,
  apiBaseUrl: API_BASE_URL,
  hostname: window.location.hostname
});

export default api; 