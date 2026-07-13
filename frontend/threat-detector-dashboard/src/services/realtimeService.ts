/**
 * Real-Time Service for Server-Sent Events (SSE)
 * Connects to the backend live log stream.
 * In demo mode (GitHub Pages / production builds without a backend),
 * generates a simulated log stream client-side instead.
 */

import { getDemoStatus } from './api';

export interface LiveLog {
  log: {
    id: string;
    timestamp: string;
    content: string;
    source_ip: string;
    method: string;
    status_code: number;
  };
  analysis: {
    threat_detected: boolean;
    threat_types: string[];
    threat_level: string;
    threat_score: number;
    confidence: number;
    inference_time_ms: number;
    timestamp: string;
    log_entry_length: number;
    analysis_details: string;
  };
  event_type: 'live_log';
}

export interface ThreatAlert {
  id: string;
  timestamp: string;
  threat_type: string;
  severity: string;
  source_ip: string;
  description: string;
  threat_score: number;
  confidence: number;
  blocked: boolean;
  log_content: string;
  event_type: 'threat_alert';
}

export interface HeartbeatEvent {
  event_type: 'heartbeat';
  timestamp: string;
}

export type StreamEvent = LiveLog | ThreatAlert | HeartbeatEvent;

export interface RealTimeCallbacks {
  onLiveLog?: (log: LiveLog) => void;
  onThreatAlert?: (alert: ThreatAlert) => void;
  onConnectionChange?: (connected: boolean) => void;
  onError?: (error: string) => void;
}

// Simulated log entries for demo mode (mirrors backend sample data)
const DEMO_SAMPLE_LOGS: { content: string; threat: boolean; threatTypes: string[] }[] = [
  { content: 'GET /index.html HTTP/1.1 200 192.168.1.10', threat: false, threatTypes: [] },
  { content: 'POST /login HTTP/1.1 200 192.168.1.15', threat: false, threatTypes: [] },
  { content: 'Normal web request GET /api/data HTTP/1.1 200', threat: false, threatTypes: [] },
  { content: 'User successfully logged in: john.doe', threat: false, threatTypes: [] },
  { content: 'Database backup completed successfully', threat: false, threatTypes: [] },
  { content: 'GET /admin HTTP/1.1 404 192.168.1.100', threat: false, threatTypes: [] },
  { content: 'SELECT * FROM users WHERE id=1; DROP TABLE users;--', threat: true, threatTypes: ['sql_injection'] },
  { content: 'Failed login attempt for user admin from 192.168.1.50', threat: true, threatTypes: ['brute_force'] },
  { content: '<script>alert("XSS attack")</script>', threat: true, threatTypes: ['xss_attack'] },
  { content: '../../../etc/passwd directory traversal attempt', threat: true, threatTypes: ['directory_traversal'] },
  { content: 'Malicious file upload attempt: exploit.php', threat: true, threatTypes: ['malicious_upload'] },
];

class RealTimeService {
  private eventSource: EventSource | null = null;
  private callbacks: RealTimeCallbacks = {};
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;
  private demoInterval: ReturnType<typeof setInterval> | null = null;

  private get isDemoMode(): boolean {
    return getDemoStatus().isDemoMode;
  }

  /**
   * Get the appropriate API URL based on environment
   */
  private getApiUrl(): string {
    // In browser environment, always use localhost for external access
    if (typeof window !== 'undefined') {
      return process.env.REACT_APP_HOST_API_URL || 'http://localhost:5001/api';
    } else {
      // In SSR/build environment, use container URL if available
      return process.env.REACT_APP_API_URL || 'http://localhost:5001/api';
    }
  }

  /**
   * Test connectivity to backend
   */
  async testConnectivity(): Promise<boolean> {
    try {
      console.log('🔍 Testing backend connectivity...');
      const apiUrl = this.getApiUrl();
      const response = await fetch(`${apiUrl.replace('/api', '')}/api/health`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const result = await response.json();
      console.log('✅ Backend connectivity test passed:', result);
      return response.ok;
    } catch (error) {
      console.error('❌ Backend connectivity test failed:', error);
      return false;
    }
  }

  /**
   * Connect to the real-time log stream
   */
  connect(callbacks: RealTimeCallbacks): void {
    this.callbacks = callbacks;

    if (this.isDemoMode) {
      console.log('🎭 Demo Mode: Real-time service connected (simulated stream)');
      this.isConnected = true;
      this.callbacks.onConnectionChange?.(true);
      return;
    }

    // Test connectivity first
    this.testConnectivity().then(isConnected => {
      if (isConnected) {
        console.log('🟢 Backend is reachable, connecting to stream...');
        this.connectToStream();
      } else {
        console.error('🔴 Backend is not reachable, cannot connect to stream');
        this.callbacks.onError?.('Backend server is not reachable');
      }
    });
  }

  /**
   * Disconnect from the stream
   */
  disconnect(): void {
    this.stopDemoStream();
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.isConnected = false;
    this.callbacks.onConnectionChange?.(false);
  }

  /**
   * Check if currently connected
   */
  getConnectionStatus(): boolean {
    return this.isConnected;
  }

  /**
   * Start monitoring on the backend
   */
  async startMonitoring(): Promise<boolean> {
    if (this.isDemoMode) {
      console.log('🎭 Demo Mode: Starting simulated monitoring stream');
      this.startDemoStream();
      return true;
    }

    try {
      const apiUrl = this.getApiUrl();
      const response = await fetch(`${apiUrl.replace('/api', '')}/api/monitoring/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      console.log('📊 Monitoring started:', result);
      
      // The monitoring state will be updated via WebSocket events
      // so we don't need to manually update state here
      return response.ok;
    } catch (error) {
      console.error('❌ Failed to start monitoring:', error);
      this.callbacks.onError?.('Failed to start monitoring');
      return false;
    }
  }

  /**
   * Stop monitoring on the backend
   */
  async stopMonitoring(): Promise<boolean> {
    if (this.isDemoMode) {
      console.log('🎭 Demo Mode: Stopping simulated monitoring stream');
      this.stopDemoStream();
      return true;
    }

    try {
      const apiUrl = this.getApiUrl();
      const response = await fetch(`${apiUrl.replace('/api', '')}/api/monitoring/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      const result = await response.json();
      console.log('🛑 Monitoring stopped:', result);
      
      // The monitoring state will be updated via WebSocket events
      // so we don't need to manually update state here
      return response.ok;
    } catch (error) {
      console.error('❌ Failed to stop monitoring:', error);
      this.callbacks.onError?.('Failed to stop monitoring');
      return false;
    }
  }

  /**
   * Start the client-side simulated log stream (demo mode only)
   */
  private startDemoStream(): void {
    if (this.demoInterval) {
      return;
    }

    this.isConnected = true;
    this.callbacks.onConnectionChange?.(true);

    this.demoInterval = setInterval(() => {
      const sample = DEMO_SAMPLE_LOGS[Math.floor(Math.random() * DEMO_SAMPLE_LOGS.length)];
      const now = new Date();
      const sourceIp = `192.168.1.${Math.floor(Math.random() * 190) + 10}`;

      // Score ranges mirror the backend's simulated classifier
      const threatScore = sample.threat
        ? 0.5 + Math.random() * 0.4
        : Math.random() * 0.45;
      const threatLevel = threatScore >= 0.8 ? 'critical'
        : threatScore >= 0.6 ? 'high'
        : threatScore >= 0.4 ? 'medium'
        : threatScore >= 0.2 ? 'low'
        : 'none';

      const liveLog: LiveLog = {
        event_type: 'live_log',
        log: {
          id: `demo_log_${now.getTime()}_${Math.floor(Math.random() * 9000) + 1000}`,
          timestamp: now.toISOString(),
          content: sample.content,
          source_ip: sourceIp,
          method: ['GET', 'POST', 'PUT', 'DELETE'][Math.floor(Math.random() * 4)],
          status_code: [200, 404, 401, 403, 500][Math.floor(Math.random() * 5)],
        },
        analysis: {
          threat_detected: sample.threat && threatScore > 0.5,
          threat_types: sample.threatTypes,
          threat_level: threatLevel,
          threat_score: Math.round(threatScore * 10000) / 10000,
          confidence: Math.round((0.75 + Math.random() * 0.2) * 10000) / 10000,
          inference_time_ms: Math.round((0.5 + Math.random() * 4) * 100) / 100,
          timestamp: now.toISOString(),
          log_entry_length: sample.content.length,
          analysis_details: 'Simulated analysis (demo mode)',
        },
      };

      this.callbacks.onLiveLog?.(liveLog);

      // Occasionally surface a threat alert toast for high-severity hits
      if (liveLog.analysis.threat_detected && threatScore >= 0.6 && Math.random() < 0.25) {
        const alert: ThreatAlert = {
          id: `demo_alert_${now.getTime()}`,
          timestamp: now.toISOString(),
          threat_type: sample.threatTypes[0] || 'suspicious_activity',
          severity: threatLevel,
          source_ip: sourceIp,
          description: sample.content,
          threat_score: liveLog.analysis.threat_score,
          confidence: liveLog.analysis.confidence,
          blocked: Math.random() < 0.5,
          log_content: sample.content,
          event_type: 'threat_alert',
        };
        this.callbacks.onThreatAlert?.(alert);
      }
    }, 2000);
  }

  /**
   * Stop the simulated log stream
   */
  private stopDemoStream(): void {
    if (this.demoInterval) {
      clearInterval(this.demoInterval);
      this.demoInterval = null;
    }
  }

  /**
   * Connect to the SSE stream
   */
  private connectToStream(): void {
    try {
      console.log('📡 Connecting to real-time stream...');
      
      // Close existing connection if any
      if (this.eventSource) {
        this.eventSource.close();
      }
      
      const apiUrl = this.getApiUrl();
      const streamUrl = `${apiUrl.replace('/api', '')}/api/stream/logs`;
      console.log('📡 Stream URL:', streamUrl);
      
      this.eventSource = new EventSource(streamUrl);

      this.eventSource.onopen = () => {
        console.log('✅ Connected to real-time stream');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.callbacks.onConnectionChange?.(true);
      };

      this.eventSource.onmessage = (event) => {
        try {
          console.log('📥 Raw stream data:', event.data);
          const data: StreamEvent = JSON.parse(event.data);
          this.handleStreamEvent(data);
        } catch (error) {
          console.error('❌ Failed to parse stream data:', error, 'Raw data:', event.data);
        }
      };

      this.eventSource.onerror = (error) => {
        console.error('❌ Stream connection error:', error);
        console.log('EventSource readyState:', this.eventSource?.readyState);
        console.log('EventSource URL:', this.eventSource?.url);
        
        this.isConnected = false;
        this.callbacks.onConnectionChange?.(false);

        // Check readyState to understand the error better
        if (this.eventSource?.readyState === EventSource.CLOSED) {
          console.log('🔍 EventSource connection was closed');
        } else if (this.eventSource?.readyState === EventSource.CONNECTING) {
          console.log('🔍 EventSource is still trying to connect...');
        }

        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnectAttempts++;
          console.log(`🔄 Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
          
          setTimeout(() => {
            this.connectToStream();
          }, this.reconnectDelay);
        } else {
          console.error('🚫 Max reconnection attempts reached');
          this.callbacks.onError?.('Failed to connect to real-time stream after multiple attempts');
        }
      };

    } catch (error) {
      console.error('❌ Failed to create stream connection:', error);
      this.callbacks.onError?.('Failed to initialize real-time connection');
    }
  }

  /**
   * Handle incoming stream events
   */
  private handleStreamEvent(event: StreamEvent): void {
    switch (event.event_type) {
      case 'live_log':
        console.log('📊 Live log received:', event.log.content);
        this.callbacks.onLiveLog?.(event);
        break;

      case 'threat_alert':
        console.log('🚨 Threat alert received:', event.threat_type);
        this.callbacks.onThreatAlert?.(event);
        break;

      case 'heartbeat':
        // Silent heartbeat to keep connection alive
        break;

      default:
        console.log('🔍 Unknown event type:', event);
    }
  }
}

// Export singleton instance
export const realTimeService = new RealTimeService();
export default realTimeService; 