import axios from 'axios';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error(`❌ API Error: ${error.response?.status || 'Network Error'} ${error.config?.url}`);
    return Promise.reject(error);
  }
);

// Types for API responses
export interface ThreatDetectionResult {
  threat_detected: boolean;
  threat_level: string;
  threat_score: number;
  confidence: number;
  inference_time_ms: number;
  features_extracted?: number;
  log_entry?: string;
  timestamp: string;
  threat_types?: string[];
  analysis_details?: string;
  log_entry_length?: number;
}

export interface BatchDetectionResult {
  total_logs: number;
  threats_detected: number;
  normal_logs: number;
  threat_distribution: Record<string, number>;
  average_inference_time_ms: number;
  results: ThreatDetectionResult[];
}

export interface SystemHealth {
  status: string;
  model_loaded: boolean;
  model_path: string;
  feature_extractor_ready: boolean;
  uptime_seconds: number;
  total_predictions: number;
  average_inference_time_ms: number;
  timestamp: string;
}

export interface SystemStats {
  total_detections: number;
  threats_blocked: number;
  detection_accuracy: number;
  uptime_hours: number;
  model_version: string;
  last_model_update: string;
  performance_metrics: {
    average_response_time_ms: number;
    requests_per_minute: number;
    error_rate: number;
  };
}

export interface SystemMetrics {
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_activity: {
    bytes_sent: number;
    bytes_received: number;
  };
  active_connections: number;
  queue_size: number;
  timestamp: string;
}

// API Service Class
class ApiService {
  // Threat Detection APIs
  async detectThreat(logEntry: string): Promise<ThreatDetectionResult> {
    const response = await api.post('/api/analyze', {
      log_entry: logEntry,
    });
    
    // Transform backend response to match frontend interface
    const backendData = response.data;
    return {
      threat_detected: backendData.threat_detected,
      threat_level: backendData.threat_level,
      threat_score: backendData.threat_score,
      confidence: backendData.confidence,
      inference_time_ms: backendData.inference_time_ms || 2.5,
      features_extracted: 25, // Based on our backend detection patterns
      log_entry: logEntry,
      timestamp: backendData.timestamp || new Date().toISOString(),
      threat_types: backendData.threat_types || [],
      analysis_details: backendData.analysis_details,
      log_entry_length: backendData.log_entry_length,
    };
  }

  async detectThreatseBatch(logEntries: string[]): Promise<BatchDetectionResult> {
    const response = await api.post('/api/detect/batch', {
      log_entries: logEntries,
    });
    return response.data;
  }

  // System Monitoring APIs
  async getSystemHealth(): Promise<SystemHealth> {
    const response = await api.get('/api/health');
    return response.data;
  }

  async getSystemStats(): Promise<SystemStats> {
    const response = await api.get('/api/stats');
    return response.data;
  }

  async getSystemMetrics(): Promise<SystemMetrics> {
    const response = await api.get('/api/metrics');
    return response.data;
  }

  // Admin APIs
  async reloadModel(): Promise<{ success: boolean; message: string }> {
    const response = await api.post('/api/admin/reload_model');
    return response.data;
  }

  // Test APIs
  async runTestDetection(): Promise<any> {
    const response = await api.get('/api/test');
    return response.data;
  }

  // Generic API call for custom endpoints
  async customCall(method: 'GET' | 'POST' | 'PUT' | 'DELETE', endpoint: string, data?: any): Promise<any> {
    const response = await api.request({
      method,
      url: endpoint,
      data,
    });
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();

// Export types and utilities
export default apiService;

// Helper function to check if backend is available
export const checkBackendAvailability = async (): Promise<boolean> => {
  try {
    await apiService.getSystemHealth();
    return true;
  } catch (error) {
    console.warn('Backend not available:', error);
    return false;
  }
};

// Mock data for development when backend is not available
export const mockThreatDetectionResult: ThreatDetectionResult = {
  threat_detected: true,
  threat_level: 'high',
  threat_score: 0.87,
  confidence: 0.92,
  inference_time_ms: 3.2,
  features_extracted: 52,
  log_entry: 'Suspicious SQL injection attempt detected',
  timestamp: new Date().toISOString(),
};

export const mockSystemHealth: SystemHealth = {
  status: 'operational',
  model_loaded: true,
  model_path: '/models/lstm_autoencoder.h5',
  feature_extractor_ready: true,
  uptime_seconds: 86400,
  total_predictions: 1247,
  average_inference_time_ms: 2.8,
  timestamp: new Date().toISOString(),
};

export const mockSystemStats: SystemStats = {
  total_detections: 1247,
  threats_blocked: 23,
  detection_accuracy: 0.997,
  uptime_hours: 24,
  model_version: '1.0.0',
  last_model_update: '2024-01-15T10:30:00Z',
  performance_metrics: {
    average_response_time_ms: 2.8,
    requests_per_minute: 145,
    error_rate: 0.003,
  },
}; 