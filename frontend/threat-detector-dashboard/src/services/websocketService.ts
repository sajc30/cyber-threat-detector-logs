/**
 * WebSocket Service for CyberGuard AI Real-Time Features
 * Handles all real-time communication with the Flask-SocketIO backend
 */

import io from 'socket.io-client';
import toast from 'react-hot-toast';

export interface ThreatAlert {
  id: string;
  timestamp: string;
  threat_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source_ip: string;
  target: string;
  description: string;
  threat_score: number;
  confidence: number;
  response_time_ms: number;
  blocked: boolean;
  investigated: boolean;
}

export interface SystemMetrics {
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  network_io: {
    bytes_in: number;
    bytes_out: number;
  };
  active_connections: number;
  threats_per_minute: number;
  model_inference_time: number;
  queue_size: number;
}

export interface UserSession {
  username: string;
  active_page: string;
  join_time: string;
}

export interface ConnectionStatus {
  status: 'connecting' | 'connected' | 'disconnected' | 'error';
  message?: string;
  session_id?: string;
  timestamp?: string;
}

export interface WebSocketCallbacks {
  onThreatAlert?: (alert: ThreatAlert) => void;
  onPriorityAlert?: (alert: ThreatAlert) => void;
  onSystemMetricsUpdate?: (metrics: SystemMetrics) => void;
  onActiveUsersUpdate?: (users: UserSession[], count: number) => void;
  onConnectionStatusChange?: (status: ConnectionStatus) => void;
  onAnalysisResult?: (result: any) => void;
  onThreatAcknowledged?: (data: any) => void;
  onUserMessage?: (data: any) => void;
  onError?: (error: string) => void;
  onMonitoringStateChange?: (isActive: boolean) => void;
}

class WebSocketService {
  private socket: any = null;
  private callbacks: WebSocketCallbacks = {};
  private connectionStatus: ConnectionStatus = { status: 'disconnected' };
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private username: string = 'Anonymous';

  constructor() {
    this.username = `User_${Math.random().toString(36).substr(2, 8)}`;
  }

  /**
   * Get the appropriate WebSocket URL based on environment
   */
  private getWebSocketUrl(): string {
    // In browser environment, always use localhost for external access
    if (typeof window !== 'undefined') {
      return process.env.REACT_APP_HOST_WS_URL || 'http://localhost:5001';
    } else {
      // In SSR/build environment, use container URL if available
      return process.env.REACT_APP_WS_URL || 'http://localhost:5001';
    }
  }

  /**
   * Initialize WebSocket connection to the Flask-SocketIO backend
   */
  connect(username?: string): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        if (username) this.username = username;

        const wsUrl = this.getWebSocketUrl();
        console.log('🔌 Connecting to WebSocket server at:', wsUrl);
        this.updateConnectionStatus({ status: 'connecting', message: 'Establishing connection...' });

        // Initialize socket connection
        this.socket = io(wsUrl, {
          transports: ['websocket', 'polling'],
          timeout: 10000,
          auth: {
            username: this.username
          },
          autoConnect: true,
          reconnection: true,
          reconnectionDelay: this.reconnectDelay,
          reconnectionAttempts: this.maxReconnectAttempts
        });

        // Connection event handlers
        this.socket.on('connect', () => {
          console.log('✅ WebSocket connected successfully');
          this.reconnectAttempts = 0;
          this.updateConnectionStatus({ 
            status: 'connected', 
            message: 'Connected to CyberGuard AI',
            session_id: this.socket?.id 
          });
          
          // Join monitoring namespace
          this.connectToMonitoring();
          resolve();
        });

        this.socket.on('disconnect', (reason: string) => {
          console.log('🔌 WebSocket disconnected:', reason);
          this.updateConnectionStatus({ 
            status: 'disconnected', 
            message: `Disconnected: ${reason}` 
          });
          
          if (reason === 'io server disconnect') {
            // Server disconnected the client, manual reconnection needed
            this.socket?.connect();
          }
        });

        this.socket.on('connect_error', (error: Error) => {
          console.error('❌ WebSocket connection error:', error);
          this.reconnectAttempts++;
          
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.updateConnectionStatus({ 
              status: 'error', 
              message: 'Failed to connect after multiple attempts' 
            });
            reject(new Error('Connection failed'));
          } else {
            this.updateConnectionStatus({ 
              status: 'connecting', 
              message: `Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})` 
            });
          }
        });

        // General event handlers
        this.socket.on('connected', (data: any) => {
          console.log('📡 General connection confirmed:', data);
        });

        this.socket.on('error', (error: any) => {
          console.error('❌ WebSocket error:', error);
          this.callbacks.onError?.(error.message || 'Unknown WebSocket error');
          toast.error(`WebSocket Error: ${error.message || 'Unknown error'}`);
        });

      } catch (error) {
        console.error('❌ Failed to initialize WebSocket:', error);
        this.updateConnectionStatus({ status: 'error', message: 'Initialization failed' });
        reject(error);
      }
    });
  }

  /**
   * Connect to the monitoring namespace for real-time threat monitoring
   */
  private connectToMonitoring(): void {
    if (!this.socket) return;

    console.log('📊 Connecting to monitoring namespace...');
    
    const wsUrl = this.getWebSocketUrl();
    // Connect to monitoring namespace
    const monitoringSocket = io(`${wsUrl}/monitoring`, {
      auth: { username: this.username }
    });

    // Monitoring namespace event handlers
    monitoringSocket.on('connect', () => {
      console.log('✅ Connected to monitoring namespace');
      
      // Join monitoring room
      monitoringSocket.emit('join_monitoring', { username: this.username });
      
      // Request initial live data
      monitoringSocket.emit('request_live_data', { type: 'all' });
    });

    monitoringSocket.on('connection_status', (data: any) => {
      console.log('📡 Monitoring connection status:', data);
      if (data.status === 'connected') {
        toast.success('🛡️ Connected to real-time monitoring!');
      }
    });

    // Threat alert handlers
    monitoringSocket.on('threat_alert', (data: any) => {
      console.log('🚨 Threat alert received:', data);
      this.callbacks.onThreatAlert?.(data.alert);
      this.showThreatNotification(data.alert);
    });

    monitoringSocket.on('priority_alert', (alert: ThreatAlert) => {
      console.log('🚨🚨 PRIORITY ALERT:', alert);
      this.callbacks.onPriorityAlert?.(alert);
      this.showPriorityThreatNotification(alert);
    });

    // System metrics handler
    monitoringSocket.on('system_metrics_update', (metrics: SystemMetrics) => {
      this.callbacks.onSystemMetricsUpdate?.(metrics);
    });

    // User management handlers
    monitoringSocket.on('active_users_update', (data: any) => {
      this.callbacks.onActiveUsersUpdate?.(data.users, data.count);
    });

    // Monitoring state handlers
    monitoringSocket.on('monitoring_started', (data: any) => {
      console.log('✅ Monitoring started via WebSocket:', data);
      this.callbacks.onMonitoringStateChange?.(true);
      toast.success('🚀 Live monitoring started!');
    });

    monitoringSocket.on('monitoring_stopped', (data: any) => {
      console.log('🛑 Monitoring stopped via WebSocket:', data);
      this.callbacks.onMonitoringStateChange?.(false);
      toast.success('🛑 Live monitoring stopped');
    });

    monitoringSocket.on('monitoring_status', (data: any) => {
      console.log('📊 Monitoring status update:', data);
      const isActive = data.status === 'started';
      this.callbacks.onMonitoringStateChange?.(isActive);
    });

    monitoringSocket.on('welcome', (data: any) => {
      console.log('👋 Welcome data received:', data);
      // Process initial data
      if (data.recent_threats) {
        data.recent_threats.forEach((threat: ThreatAlert) => {
          this.callbacks.onThreatAlert?.(threat);
        });
      }
    });

    // Live data response handler
    monitoringSocket.on('live_data_response', (data: any) => {
      console.log('📊 Live data received:', data);
      if (data.data.threats) {
        data.data.threats.forEach((threat: ThreatAlert) => {
          this.callbacks.onThreatAlert?.(threat);
        });
      }
    });

    // Analysis result handler
    monitoringSocket.on('analysis_result', (result: any) => {
      console.log('🔍 Analysis result:', result);
      this.callbacks.onAnalysisResult?.(result);
      
      if (result.threat_detected) {
        toast.success(`🔍 Threat detected: ${result.threat_level.toUpperCase()}`);
      } else {
        toast.success('✅ Log entry appears safe');
      }
    });

    monitoringSocket.on('analysis_error', (error: any) => {
      console.error('❌ Analysis error:', error);
      this.callbacks.onError?.(error.message);
      toast.error(`Analysis Error: ${error.message}`);
    });

    // Threat acknowledgment handler
    monitoringSocket.on('threat_acknowledged', (data: any) => {
      console.log('✅ Threat acknowledged:', data);
      this.callbacks.onThreatAcknowledged?.(data);
      toast(`Threat ${data.threat_id} ${data.action} by ${data.user}`, {
        icon: 'ℹ️',
        style: { background: '#3b82f6', color: 'white' }
      });
    });

    // User message handler
    monitoringSocket.on('user_message', (data: any) => {
      console.log('💬 User message:', data);
      this.callbacks.onUserMessage?.(data);
      toast(`💬 ${data.username}: ${data.message}`, { duration: 3000 });
    });

    // Room management
    monitoringSocket.on('room_joined', (data: any) => {
      console.log('🏠 Joined room:', data);
    });

    // Ping/Pong for connection testing
    monitoringSocket.on('pong', (data: any) => {
      console.log('🏓 Pong received:', data);
    });

    // Store monitoring socket reference
    (this as any).monitoringSocket = monitoringSocket;
  }

  /**
   * Show threat notification with appropriate styling
   */
  private showThreatNotification(alert: ThreatAlert): void {
    const severityEmoji = {
      low: '⚠️',
      medium: '🟡',
      high: '🟠',
      critical: '🔴'
    };

    const message = `${severityEmoji[alert.severity]} ${alert.threat_type} detected from ${alert.source_ip}`;
    
    if (alert.severity === 'critical' || alert.severity === 'high') {
      toast.error(message, { duration: 8000 });
    } else {
      toast(message, { duration: 5000 });
    }
  }

  /**
   * Show priority threat notification
   */
  private showPriorityThreatNotification(alert: ThreatAlert): void {
    toast.error(`🚨 PRIORITY ALERT: ${alert.threat_type} - ${alert.description}`, {
      duration: 10000,
      style: {
        background: '#dc2626',
        color: 'white',
        fontWeight: 'bold'
      }
    });
  }

  /**
   * Update connection status and notify callbacks
   */
  private updateConnectionStatus(status: ConnectionStatus): void {
    this.connectionStatus = status;
    this.callbacks.onConnectionStatusChange?.(status);
  }

  /**
   * Register event callbacks
   */
  setCallbacks(callbacks: WebSocketCallbacks): void {
    this.callbacks = { ...this.callbacks, ...callbacks };
  }

  /**
   * Send manual threat analysis request
   */
  analyzeLog(logEntry: string): void {
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket?.connected) {
      console.log('🔍 Sending manual analysis request:', logEntry);
      monitoringSocket.emit('manual_threat_analysis', { log_entry: logEntry });
    } else {
      toast.error('Not connected to monitoring service');
    }
  }

  /**
   * Acknowledge a threat
   */
  acknowledgeThreat(threatId: string, action: 'acknowledged' | 'investigated' | 'blocked'): void {
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket?.connected) {
      console.log('✅ Acknowledging threat:', threatId, action);
      monitoringSocket.emit('acknowledge_threat', { 
        threat_id: threatId, 
        action 
      });
    }
  }

  /**
   * Send a chat message to other users
   */
  sendMessage(message: string): void {
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket?.connected) {
      console.log('💬 Sending message:', message);
      monitoringSocket.emit('send_message', { message });
    }
  }

  /**
   * Request live data update
   */
  requestLiveData(type: 'all' | 'threats' | 'metrics' | 'statistics' | 'users' = 'all'): void {
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket?.connected) {
      monitoringSocket.emit('request_live_data', { type });
    }
  }

  /**
   * Request system status
   */
  requestSystemStatus(): void {
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket?.connected) {
      monitoringSocket.emit('request_system_status');
    }
  }

  /**
   * Send ping to test connection
   */
  ping(): void {
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket?.connected) {
      monitoringSocket.emit('ping');
    }
  }

  /**
   * Get current connection status
   */
  getConnectionStatus(): ConnectionStatus {
    return this.connectionStatus;
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.connectionStatus.status === 'connected';
  }

  /**
   * Disconnect from WebSocket
   */
  disconnect(): void {
    console.log('🔌 Disconnecting WebSocket...');
    
    const monitoringSocket = (this as any).monitoringSocket;
    if (monitoringSocket) {
      monitoringSocket.disconnect();
    }
    
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
    
    this.updateConnectionStatus({ status: 'disconnected', message: 'Manually disconnected' });
  }
}

// Export singleton instance
export const websocketService = new WebSocketService();
export default websocketService; 