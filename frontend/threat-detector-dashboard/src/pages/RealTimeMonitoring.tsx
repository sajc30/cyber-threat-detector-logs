import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  CircularProgress,
  Divider,
  Paper,
  Tab,
  Tabs,
  LinearProgress,
  IconButton,
  Tooltip,
  Badge,
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  Clear,
  Security,
  Warning,
  CheckCircle,
  Error,
  Timeline,
  Send,
  Refresh,
  Visibility,
  NotificationsActive,
  VolumeUp,
  VolumeOff,
  Wifi,
  WifiOff,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import toast from 'react-hot-toast';

import { apiService, ThreatDetectionResult, checkBackendAvailability, mockThreatDetectionResult } from '../services/api';
import realTimeService, { LiveLog, ThreatAlert } from '../services/realtimeService';

interface LogEntry {
  id: string;
  timestamp: Date;
  content: string;
  result?: ThreatDetectionResult;
  processing?: boolean;
  source_ip?: string;
  method?: string;
  status_code?: number;
}

interface ThreatTimelinePoint {
  time: string;
  threatLevel: number;
  threatCount: number;
}

// Sound notification functions
const playThreatSound = (severity: string) => {
  try {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Different sounds for different threat levels
    switch (severity.toLowerCase()) {
      case 'high':
      case 'critical':
        // High-pitched urgent beep
        oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
        oscillator.frequency.setValueAtTime(1000, audioContext.currentTime + 0.1);
        gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.3);
        break;
      case 'medium':
        // Medium beep
        oscillator.frequency.setValueAtTime(600, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.2, audioContext.currentTime);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.2);
        break;
      case 'low':
        // Low soft beep
        oscillator.frequency.setValueAtTime(400, audioContext.currentTime);
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.1);
        break;
    }
  } catch (error) {
    console.warn('Audio notification failed:', error);
  }
};

const RealTimeMonitoring: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [currentLog, setCurrentLog] = useState('');
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [isStreamConnected, setIsStreamConnected] = useState(false);
  const [backendAvailable, setBackendAvailable] = useState(false);
  const [threatTimeline, setThreatTimeline] = useState<ThreatTimelinePoint[]>([]);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [totalThreatsToday, setTotalThreatsToday] = useState(0);
  const [stats, setStats] = useState({
    totalAnalyzed: 0,
    threatsDetected: 0,
    averageResponseTime: 0,
  });

  // Sample log entries for testing
  const sampleLogs = [
    'GET /admin HTTP/1.1 404 192.168.1.100',
    'SELECT * FROM users WHERE id=1; DROP TABLE users;--',
    'Failed login attempt for user admin from 192.168.1.50',
    'Normal web request GET /index.html HTTP/1.1 200',
    'POST /api/data HTTP/1.1 200 application/json',
    'Multiple failed SSH attempts from 10.0.0.45',
    'Malicious file upload attempt: exploit.php',
    'User successfully logged in: john.doe',
    '<script>alert("XSS attack")</script>',
    'SELECT password FROM admin_users WHERE username="admin"',
    '../../../etc/passwd directory traversal attempt',
    'Normal user activity: file download completed',
  ];

  // Check backend availability
  useEffect(() => {
    const checkBackend = async () => {
      const available = await checkBackendAvailability();
      setBackendAvailable(available);
    };
    checkBackend();
  }, []);

  // Handle incoming live logs
  const handleLiveLog = useCallback((liveLog: LiveLog) => {
    const logEntry: LogEntry = {
      id: liveLog.log.id,
      timestamp: new Date(liveLog.log.timestamp),
      content: liveLog.log.content,
      source_ip: liveLog.log.source_ip,
      method: liveLog.log.method,
      status_code: liveLog.log.status_code,
      result: {
        threat_detected: liveLog.analysis.threat_detected,
        threat_level: liveLog.analysis.threat_level,
        threat_score: liveLog.analysis.threat_score,
        confidence: liveLog.analysis.confidence,
        inference_time_ms: liveLog.analysis.inference_time_ms,
        timestamp: liveLog.analysis.timestamp,
        threat_types: liveLog.analysis.threat_types,
        analysis_details: liveLog.analysis.analysis_details,
        log_entry_length: liveLog.analysis.log_entry_length,
      }
    };

    // Add to log entries
    setLogEntries(prev => [logEntry, ...prev.slice(0, 49)]);

    // Update stats
    setStats(prev => ({
      totalAnalyzed: prev.totalAnalyzed + 1,
      threatsDetected: prev.threatsDetected + (liveLog.analysis.threat_detected ? 1 : 0),
      averageResponseTime: (prev.averageResponseTime * prev.totalAnalyzed + liveLog.analysis.inference_time_ms) / (prev.totalAnalyzed + 1),
    }));

    // Update timeline
    const timeString = new Date().toLocaleTimeString();
    setThreatTimeline(prev => {
      const newPoint: ThreatTimelinePoint = {
        time: timeString,
        threatLevel: liveLog.analysis.threat_detected ? liveLog.analysis.threat_score * 100 : 0,
        threatCount: liveLog.analysis.threat_detected ? 1 : 0,
      };
      return [...prev.slice(-19), newPoint];
    });

  }, []);

  // Handle threat alerts
  const handleThreatAlert = useCallback((alert: ThreatAlert) => {
    const severity = alert.severity.toLowerCase();
    
    // Play sound if enabled
    if (soundEnabled) {
      playThreatSound(severity);
    }
    
    // Update total threats counter
    setTotalThreatsToday(prev => prev + 1);
    
    // Show toast notification
    switch (severity) {
      case 'high':
      case 'critical':
        toast.error(`🚨 ${severity.toUpperCase()} THREAT: ${alert.threat_type}`, {
          duration: 8000,
          position: 'top-right',
          style: {
            background: '#d32f2f',
            color: 'white',
          },
        });
        break;
      case 'medium':
        toast(`⚠️ ${severity.toUpperCase()} THREAT: ${alert.threat_type}`, {
          duration: 6000,
          position: 'top-right',
          style: {
            background: '#ed6c02',
            color: 'white',
          },
          icon: '⚠️',
        });
        break;
      case 'low':
        toast(`🟡 ${severity.toUpperCase()} THREAT: ${alert.threat_type}`, {
          duration: 4000,
          position: 'top-right',
          icon: '⚠️',
        });
        break;
    }

    // Browser notification for high/critical threats
    if ((severity === 'high' || severity === 'critical') && 'Notification' in window) {
      if (Notification.permission === 'granted') {
        new Notification('CyberGuard AI - Threat Detected!', {
          body: `${severity.toUpperCase()} threat: ${alert.threat_type}`,
          icon: '/favicon.ico',
        });
      }
    }
  }, [soundEnabled]);

  // Set up real-time service
  useEffect(() => {
    console.log('🔌 Setting up real-time service...');
    
    const callbacks = {
      onLiveLog: handleLiveLog,
      onThreatAlert: handleThreatAlert,
      onConnectionChange: setIsStreamConnected,
      onError: (error: string) => {
        console.error('Real-time service error:', error);
        toast.error(`Stream Error: ${error}`);
      }
    };
    
    realTimeService.connect(callbacks);

    return () => {
      realTimeService.disconnect();
    };
  }, [handleLiveLog, handleThreatAlert]);

  // Start monitoring
  const startMonitoring = async () => {
    const success = await realTimeService.startMonitoring();
    if (success) {
      setIsMonitoring(true);
      toast.success('🚀 Live monitoring started!');
    } else {
      toast.error('❌ Failed to start monitoring');
    }
  };

  // Stop monitoring
  const stopMonitoring = async () => {
    const success = await realTimeService.stopMonitoring();
    if (success) {
      setIsMonitoring(false);
      toast.success('🛑 Live monitoring stopped');
    } else {
      toast.error('❌ Failed to stop monitoring');
    }
  };

  const toggleMonitoring = () => {
    if (isMonitoring) {
      stopMonitoring();
    } else {
      startMonitoring();
    }
  };

  const handleManualAnalysis = async () => {
    if (currentLog.trim()) {
      try {
        const result = await apiService.detectThreat(currentLog.trim());
        
        const logEntry: LogEntry = {
          id: Date.now().toString(),
          timestamp: new Date(),
          content: currentLog.trim(),
          result: result
        };

        setLogEntries(prev => [logEntry, ...prev.slice(0, 49)]);
        
        // Update stats
        setStats(prev => ({
          totalAnalyzed: prev.totalAnalyzed + 1,
          threatsDetected: prev.threatsDetected + (result.threat_detected ? 1 : 0),
          averageResponseTime: (prev.averageResponseTime * prev.totalAnalyzed + result.inference_time_ms) / (prev.totalAnalyzed + 1),
        }));

        setCurrentLog('');
        
        if (result.threat_detected) {
          toast.success(`✅ Manual analysis: ${result.threat_level.toUpperCase()} threat detected`);
        } else {
          toast.success('✅ Manual analysis: No threats detected');
        }
      } catch (error) {
        toast.error('❌ Manual analysis failed');
      }
    }
  };

  const clearLogs = () => {
    setLogEntries([]);
    setThreatTimeline([]);
    setStats({ totalAnalyzed: 0, threatsDetected: 0, averageResponseTime: 0 });
    setTotalThreatsToday(0);
    toast.success('🗑️ Logs cleared', { duration: 2000 });
  };

  const getThreatLevelColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getThreatIcon = (detected: boolean, processing?: boolean) => {
    if (processing) return <CircularProgress size={20} />;
    return detected ? <Warning color="error" /> : <CheckCircle color="success" />;
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
          Real-Time Threat Monitoring
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Typography variant="body1" color="text.secondary">
            Live log analysis and threat detection • Backend: {backendAvailable ? '🟢 Online' : '🔴 Offline'}
          </Typography>
          <Chip
            icon={isStreamConnected ? <Wifi /> : <WifiOff />}
            label={`Stream: ${isStreamConnected ? 'Connected' : 'Disconnected'}`}
            color={isStreamConnected ? 'success' : 'error'}
            variant="outlined"
            size="small"
          />
        </Box>
      </Box>

      {/* Status Alert */}
      {!backendAvailable && (
        <Alert severity="warning" sx={{ mb: 3 }}>
          Backend API is not available. Using mock data for demonstration. Start the Flask server to enable live detection.
        </Alert>
      )}

      {/* Control Panel */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Button
                variant={isMonitoring ? "outlined" : "contained"}
                startIcon={isMonitoring ? <Pause /> : <PlayArrow />}
                onClick={toggleMonitoring}
                color={isMonitoring ? "error" : "primary"}
              >
                {isMonitoring ? 'Stop Monitoring' : 'Start Monitoring'}
              </Button>
              
              <IconButton
                onClick={() => setSoundEnabled(!soundEnabled)}
                color={soundEnabled ? "primary" : "default"}
                title={soundEnabled ? "Disable sound alerts" : "Enable sound alerts"}
                size="small"
              >
                {soundEnabled ? <VolumeUp /> : <VolumeOff />}
              </IconButton>

              <Badge 
                badgeContent={totalThreatsToday} 
                color="error" 
                max={99}
                overlap="rectangular"
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
              >
                <Chip
                  icon={<NotificationsActive />}
                  label="Alerts"
                  color={totalThreatsToday > 0 ? "warning" : "default"}
                  variant="outlined"
                  size="small"
                  sx={{ minWidth: '80px' }}
                />
              </Badge>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
              <Button
                variant="outlined"
                startIcon={<Clear />}
                onClick={clearLogs}
                disabled={logEntries.length === 0}
                size="small"
              >
                Clear Logs
              </Button>

              <Chip
                icon={<Timeline />}
                label={`${stats.totalAnalyzed} Analyzed`}
                color="primary"
                variant="outlined"
                size="small"
              />

              <Chip
                icon={<Warning />}
                label={`${stats.threatsDetected} Threats`}
                color="error"
                variant="outlined"
                size="small"
              />

              <Chip
                label={`${stats.averageResponseTime.toFixed(1)}ms`}
                color="info"
                variant="outlined"
                size="small"
              />
            </Box>
          </Box>

          {/* Manual Log Entry */}
          <Box sx={{ display: 'flex', gap: 2 }}>
            <TextField
              fullWidth
              placeholder="Enter log entry for manual analysis..."
              value={currentLog}
              onChange={(e) => setCurrentLog(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleManualAnalysis()}
              size="small"
            />
            <Button
              variant="contained"
              startIcon={<Send />}
              onClick={handleManualAnalysis}
              disabled={!currentLog.trim()}
            >
              Analyze
            </Button>
          </Box>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
          gap: 3,
          mb: 3,
        }}
      >
        {/* Timeline Chart */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              Threat Detection Timeline
            </Typography>
            {threatTimeline.length > 0 ? (
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={threatTimeline}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="time" stroke="#b0bec5" />
                    <YAxis stroke="#b0bec5" domain={[0, 100]} />
                    <ChartTooltip
                      contentStyle={{
                        backgroundColor: '#1a1f2e',
                        border: '1px solid #00e676',
                        borderRadius: '8px',
                      }}
                    />
                    <ReferenceLine y={50} stroke="#ff9800" strokeDasharray="5 5" />
                    <Line
                      type="monotone"
                      dataKey="threatLevel"
                      stroke="#f44336"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      activeDot={{ r: 6 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            ) : (
              <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  {isMonitoring ? 'Waiting for live logs...' : 'Start monitoring to see threat detection timeline'}
                </Typography>
              </Box>
            )}
          </CardContent>
        </Card>

        {/* Live Stats */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              Live Statistics
            </Typography>
            
            <Box sx={{ mb: 3 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Threat Detection Rate</Typography>
                <Typography variant="body2">
                  {stats.totalAnalyzed > 0 ? ((stats.threatsDetected / stats.totalAnalyzed) * 100).toFixed(1) : 0}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={stats.totalAnalyzed > 0 ? (stats.threatsDetected / stats.totalAnalyzed) * 100 : 0}
                sx={{ height: 8, borderRadius: 1 }}
                color="error"
              />
            </Box>

            <Divider sx={{ mb: 3 }} />

            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>
              System Status
            </Typography>
            
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Security sx={{ mr: 1, color: backendAvailable ? 'success.main' : 'error.main' }} />
              <Typography variant="body2">
                AI Model: {backendAvailable ? 'Active' : 'Offline'}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Visibility sx={{ mr: 1, color: isMonitoring ? 'success.main' : 'text.secondary' }} />
              <Typography variant="body2">
                Monitoring: {isMonitoring ? 'Active' : 'Stopped'}
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              {isStreamConnected ? <Wifi sx={{ mr: 1, color: 'success.main' }} /> : <WifiOff sx={{ mr: 1, color: 'error.main' }} />}
              <Typography variant="body2">
                Stream: {isStreamConnected ? 'Connected' : 'Disconnected'}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Log Entries */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Recent Log Analysis {isMonitoring && '(Live)'}
            </Typography>
            <IconButton size="small" onClick={() => window.location.reload()}>
              <Refresh />
            </IconButton>
          </Box>

          {logEntries.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <Typography color="text.secondary">
                {isMonitoring ? 'Live monitoring active - waiting for logs...' : 'No log entries yet. Start monitoring or enter a log manually.'}
              </Typography>
            </Box>
          ) : (
            <List sx={{ maxHeight: 400, overflow: 'auto' }}>
              {logEntries.map((entry) => (
                <React.Fragment key={entry.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getThreatIcon(entry.result?.threat_detected || false, entry.processing)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                          <Typography variant="body2" sx={{ fontFamily: 'monospace', flexGrow: 1 }}>
                            {entry.content}
                          </Typography>
                          {entry.source_ip && (
                            <Chip
                              label={entry.source_ip}
                              color="default"
                              size="small"
                              variant="outlined"
                            />
                          )}
                          {entry.result && (
                            <>
                              <Chip
                                label={entry.result.threat_detected ? 'THREAT' : 'SAFE'}
                                color={entry.result.threat_detected ? 'error' : 'success'}
                                size="small"
                              />
                              {entry.result.threat_detected && (
                                <Chip
                                  label={entry.result.threat_level.toUpperCase()}
                                  color={getThreatLevelColor(entry.result.threat_level) as any}
                                  size="small"
                                />
                              )}
                            </>
                          )}
                        </Box>
                      }
                      secondary={
                        <Typography variant="caption" color="text.secondary">
                          {entry.timestamp.toLocaleTimeString()}
                          {entry.result && ` • Score: ${(entry.result.threat_score * 100).toFixed(1)}% • ${entry.result.inference_time_ms.toFixed(1)}ms`}
                          {entry.method && ` • ${entry.method}`}
                        </Typography>
                      }
                    />
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          )}
        </CardContent>
      </Card>
    </Box>
  );
};

export default RealTimeMonitoring;