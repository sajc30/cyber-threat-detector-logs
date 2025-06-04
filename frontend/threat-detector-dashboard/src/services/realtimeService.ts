/**
 * Real-Time Service for Server-Sent Events (SSE)
 * Connects to the backend live log stream
 */

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

class RealTimeService {
  private eventSource: EventSource | null = null;
  private callbacks: RealTimeCallbacks = {};
  private isConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;

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