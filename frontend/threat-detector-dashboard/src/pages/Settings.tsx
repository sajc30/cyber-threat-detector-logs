import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Switch,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Slider,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Security,
  Notifications,
  Monitor,
  Save,
  Download,
  Upload,
  RestartAlt,
  Speed,
  Storage,
  VpnKey,
  Backup,
  Add,
} from '@mui/icons-material';

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<'idle' | 'saving' | 'success' | 'error'>('idle');
  const [newOriginDialog, setNewOriginDialog] = useState(false);
  const [newOrigin, setNewOrigin] = useState('');

  // System configuration state
  const [config, setConfig] = useState({
    security: {
      enableRateLimit: true,
      rateLimitRequests: 100,
      rateLimitWindow: 3600,
      enableCORS: true,
      allowedOrigins: ['http://localhost:3000', 'https://yourdomain.com'],
      enableSSL: false,
      sessionTimeout: 1800,
      passwordPolicy: {
        minLength: 8,
        requireNumbers: true,
        requireSymbols: true,
        requireUppercase: true,
      },
    },
    monitoring: {
      enableMetrics: true,
      metricsInterval: 30,
      enableLogging: true,
      logLevel: 'INFO',
      logRetention: 30,
      enableAlerts: true,
      alertThresholds: {
        cpuUsage: 80,
        memoryUsage: 85,
        diskUsage: 90,
        errorRate: 5,
      },
    },
  });

  // System status state
  const [systemStatus, setSystemStatus] = useState({
    uptime: '2d 14h 32m',
    cpuUsage: 45,
    memoryUsage: 62,
    diskUsage: 28,
    activeConnections: 23,
    lastBackup: '2024-01-20 02:00:00',
  });

  useEffect(() => {
    // Simulate periodic status updates
    const statusInterval = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        cpuUsage: Math.max(20, Math.min(90, prev.cpuUsage + (Math.random() - 0.5) * 10)),
        memoryUsage: Math.max(30, Math.min(95, prev.memoryUsage + (Math.random() - 0.5) * 8)),
        activeConnections: Math.max(0, prev.activeConnections + Math.floor((Math.random() - 0.5) * 6)),
      }));
    }, 5000);
    
    return () => clearInterval(statusInterval);
  }, []);

  const saveConfiguration = async () => {
    try {
      setLoading(true);
      setSaveStatus('saving');
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSaveStatus('success');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } catch (error) {
      console.error('Failed to save configuration:', error);
      setSaveStatus('error');
      setTimeout(() => setSaveStatus('idle'), 3000);
    } finally {
      setLoading(false);
    }
  };

  const addOrigin = () => {
    if (newOrigin && !config.security.allowedOrigins.includes(newOrigin)) {
      setConfig(prev => ({
        ...prev,
        security: {
          ...prev.security,
          allowedOrigins: [...prev.security.allowedOrigins, newOrigin],
        },
      }));
      setNewOrigin('');
      setNewOriginDialog(false);
    }
  };

  const removeOrigin = (origin: string) => {
    setConfig(prev => ({
      ...prev,
      security: {
        ...prev.security,
        allowedOrigins: prev.security.allowedOrigins.filter(o => o !== origin),
      },
    }));
  };

  const exportConfiguration = () => {
    const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cyberguard-config-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const getStatusColor = (value: number, thresholds: { warning: number; danger: number }) => {
    if (value >= thresholds.danger) return 'error';
    if (value >= thresholds.warning) return 'warning';
    return 'success';
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            ⚙️ System Configuration & Production Settings
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Enterprise-grade system configuration with security hardening and performance optimization
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={exportConfiguration}
          >
            Export Config
          </Button>
          
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={saveConfiguration}
            disabled={loading || saveStatus === 'saving'}
          >
            {saveStatus === 'saving' ? 'Saving...' : 'Save Configuration'}
          </Button>
        </Box>
      </Box>

      {/* Save Status Alert */}
      {saveStatus !== 'idle' && (
        <Alert 
          severity={
            saveStatus === 'saving' ? 'info' :
            saveStatus === 'success' ? 'success' : 'error'
          } 
          sx={{ mb: 3 }}
        >
          {saveStatus === 'saving' && 'Saving configuration...'}
          {saveStatus === 'success' && 'Configuration saved successfully!'}
          {saveStatus === 'error' && 'Failed to save configuration. Please try again.'}
        </Alert>
      )}

      {/* System Status Overview */}
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' }, gap: 3, mb: 3 }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Speed sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="subtitle2">CPU Usage</Typography>
            </Box>
            <Typography variant="h4" color={getStatusColor(systemStatus.cpuUsage, { warning: 70, danger: 85 })}>
              {systemStatus.cpuUsage}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={systemStatus.cpuUsage} 
              color={getStatusColor(systemStatus.cpuUsage, { warning: 70, danger: 85 })}
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Storage sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="subtitle2">Memory Usage</Typography>
            </Box>
            <Typography variant="h4" color={getStatusColor(systemStatus.memoryUsage, { warning: 75, danger: 90 })}>
              {systemStatus.memoryUsage}%
            </Typography>
            <LinearProgress 
              variant="determinate" 
              value={systemStatus.memoryUsage} 
              color={getStatusColor(systemStatus.memoryUsage, { warning: 75, danger: 90 })}
              sx={{ mt: 1 }}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Monitor sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="subtitle2">Active Connections</Typography>
            </Box>
            <Typography variant="h4" sx={{ color: 'success.main' }}>
              {systemStatus.activeConnections}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time users
            </Typography>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Backup sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="subtitle2">System Uptime</Typography>
            </Box>
            <Typography variant="h4" sx={{ color: 'warning.main' }}>
              {systemStatus.uptime}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Last backup: {systemStatus.lastBackup.split(' ')[0]}
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Configuration Tabs */}
      <Card>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<Security />} label="Security" />
          <Tab icon={<Monitor />} label="Monitoring" />
          <Tab icon={<Notifications />} label="Notifications" />
          <Tab icon={<Speed />} label="Performance" />
          <Tab icon={<VpnKey />} label="Authentication" />
          <Tab icon={<Backup />} label="Backup" />
        </Tabs>
      </Card>

      {/* Security Settings */}
      {activeTab === 0 && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              🛡️ Security Configuration
            </Typography>
            
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
              {/* Rate Limiting */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                    Rate Limiting
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography>Enable Rate Limiting</Typography>
                      <Switch
                        checked={config.security.enableRateLimit}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          security: { ...prev.security, enableRateLimit: e.target.checked }
                        }))}
                      />
                    </Box>
                  </Box>

                  {config.security.enableRateLimit && (
                    <>
                      <TextField
                        fullWidth
                        label="Requests per window"
                        type="number"
                        value={config.security.rateLimitRequests}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          security: { ...prev.security, rateLimitRequests: parseInt(e.target.value) }
                        }))}
                        sx={{ mb: 2 }}
                      />
                      
                      <TextField
                        fullWidth
                        label="Window duration (seconds)"
                        type="number"
                        value={config.security.rateLimitWindow}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          security: { ...prev.security, rateLimitWindow: parseInt(e.target.value) }
                        }))}
                      />
                    </>
                  )}
                </CardContent>
              </Card>

              {/* CORS Settings */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                    CORS Configuration
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography>Enable CORS</Typography>
                      <Switch
                        checked={config.security.enableCORS}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          security: { ...prev.security, enableCORS: e.target.checked }
                        }))}
                      />
                    </Box>
                  </Box>

                  {config.security.enableCORS && (
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="body2">Allowed Origins</Typography>
                        <Button
                          size="small"
                          startIcon={<Add />}
                          onClick={() => setNewOriginDialog(true)}
                        >
                          Add Origin
                        </Button>
                      </Box>
                      
                      <Box sx={{ maxHeight: 150, overflow: 'auto' }}>
                        {config.security.allowedOrigins.map((origin, index) => (
                          <Chip
                            key={index}
                            label={origin}
                            onDelete={() => removeOrigin(origin)}
                            sx={{ m: 0.5 }}
                            size="small"
                          />
                        ))}
                      </Box>
                    </Box>
                  )}
                </CardContent>
              </Card>

              {/* Password Policy */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                    Password Policy
                  </Typography>
                  
                  <TextField
                    fullWidth
                    label="Minimum Length"
                    type="number"
                    value={config.security.passwordPolicy.minLength}
                    onChange={(e) => setConfig(prev => ({
                      ...prev,
                      security: {
                        ...prev.security,
                        passwordPolicy: {
                          ...prev.security.passwordPolicy,
                          minLength: parseInt(e.target.value)
                        }
                      }
                    }))}
                    sx={{ mb: 2 }}
                  />

                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {[
                      { key: 'requireNumbers', label: 'Require Numbers' },
                      { key: 'requireSymbols', label: 'Require Symbols' },
                      { key: 'requireUppercase', label: 'Require Uppercase' },
                    ].map((item) => (
                      <Box key={item.key} sx={{ display: 'flex', alignItems: 'center' }}>
                        <Typography sx={{ flexGrow: 1 }}>{item.label}</Typography>
                        <Switch
                          checked={config.security.passwordPolicy[item.key as keyof typeof config.security.passwordPolicy] as boolean}
                          onChange={(e) => setConfig(prev => ({
                            ...prev,
                            security: {
                              ...prev.security,
                              passwordPolicy: {
                                ...prev.security.passwordPolicy,
                                [item.key]: e.target.checked
                              }
                            }
                          }))}
                        />
                      </Box>
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Monitoring Settings */}
      {activeTab === 1 && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 3, fontWeight: 600 }}>
              📊 Monitoring & Alerting Configuration
            </Typography>
            
            <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3, mb: 3 }}>
              {/* Metrics Configuration */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                    Metrics Collection
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography>Enable Metrics</Typography>
                      <Switch
                        checked={config.monitoring.enableMetrics}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          monitoring: { ...prev.monitoring, enableMetrics: e.target.checked }
                        }))}
                      />
                    </Box>
                  </Box>

                  {config.monitoring.enableMetrics && (
                    <TextField
                      fullWidth
                      label="Collection Interval (seconds)"
                      type="number"
                      value={config.monitoring.metricsInterval}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        monitoring: { ...prev.monitoring, metricsInterval: parseInt(e.target.value) }
                      }))}
                    />
                  )}
                </CardContent>
              </Card>

              {/* Logging Configuration */}
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                    Logging Configuration
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Typography>Enable Logging</Typography>
                      <Switch
                        checked={config.monitoring.enableLogging}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          monitoring: { ...prev.monitoring, enableLogging: e.target.checked }
                        }))}
                      />
                    </Box>
                  </Box>

                  {config.monitoring.enableLogging && (
                    <>
                      <FormControl fullWidth sx={{ mb: 2 }}>
                        <InputLabel>Log Level</InputLabel>
                        <Select
                          value={config.monitoring.logLevel}
                          onChange={(e) => setConfig(prev => ({
                            ...prev,
                            monitoring: { ...prev.monitoring, logLevel: e.target.value }
                          }))}
                        >
                          <MenuItem value="DEBUG">DEBUG</MenuItem>
                          <MenuItem value="INFO">INFO</MenuItem>
                          <MenuItem value="WARNING">WARNING</MenuItem>
                          <MenuItem value="ERROR">ERROR</MenuItem>
                          <MenuItem value="CRITICAL">CRITICAL</MenuItem>
                        </Select>
                      </FormControl>

                      <TextField
                        fullWidth
                        label="Log Retention (days)"
                        type="number"
                        value={config.monitoring.logRetention}
                        onChange={(e) => setConfig(prev => ({
                          ...prev,
                          monitoring: { ...prev.monitoring, logRetention: parseInt(e.target.value) }
                        }))}
                      />
                    </>
                  )}
                </CardContent>
              </Card>
            </Box>

            {/* Alert Thresholds */}
            <Card variant="outlined">
              <CardContent>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  Alert Thresholds
                </Typography>
                
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
                    <Typography>Enable Alerts</Typography>
                    <Switch
                      checked={config.monitoring.enableAlerts}
                      onChange={(e) => setConfig(prev => ({
                        ...prev,
                        monitoring: { ...prev.monitoring, enableAlerts: e.target.checked }
                      }))}
                    />
                  </Box>
                </Box>

                {config.monitoring.enableAlerts && (
                  <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(4, 1fr)' }, gap: 2 }}>
                    {[
                      { key: 'cpuUsage', label: 'CPU Usage (%)', max: 100 },
                      { key: 'memoryUsage', label: 'Memory Usage (%)', max: 100 },
                      { key: 'diskUsage', label: 'Disk Usage (%)', max: 100 },
                      { key: 'errorRate', label: 'Error Rate (%)', max: 50 },
                    ].map((threshold) => (
                      <Box key={threshold.key}>
                        <Typography variant="body2" sx={{ mb: 1 }}>
                          {threshold.label}
                        </Typography>
                        <Slider
                          value={config.monitoring.alertThresholds[threshold.key as keyof typeof config.monitoring.alertThresholds]}
                          onChange={(_, value) => setConfig(prev => ({
                            ...prev,
                            monitoring: {
                              ...prev.monitoring,
                              alertThresholds: {
                                ...prev.monitoring.alertThresholds,
                                [threshold.key]: value as number
                              }
                            }
                          }))}
                          min={0}
                          max={threshold.max}
                          valueLabelDisplay="on"
                          marks={[
                            { value: 0, label: '0%' },
                            { value: threshold.max, label: `${threshold.max}%` },
                          ]}
                        />
                      </Box>
                    ))}
                  </Box>
                )}
              </CardContent>
            </Card>
          </CardContent>
        </Card>
      )}

      {/* Other tabs placeholder */}
      {activeTab > 1 && (
        <Card sx={{ mt: 2 }}>
          <CardContent>
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="h6">
                🚧 Tab {activeTab + 1} Configuration
              </Typography>
              <Typography>
                {activeTab === 2 && 'Notifications: Email, Slack, SMS, and webhook configurations for threat alerts'}
                {activeTab === 3 && 'Performance: Connection limits, caching, compression, and optimization settings'}  
                {activeTab === 4 && 'Authentication: MFA, SSO, LDAP, OAuth, and session management'}
                {activeTab === 5 && 'Backup: Automated backups, encryption, retention policies, and restore procedures'}
              </Typography>
            </Alert>
            
            <Typography variant="body1" color="text.secondary">
              Advanced configuration interface for this section is ready for implementation with the same comprehensive approach as Security and Monitoring tabs.
            </Typography>
          </CardContent>
        </Card>
      )}

      {/* Add Origin Dialog */}
      <Dialog
        open={newOriginDialog}
        onClose={() => setNewOriginDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Add Allowed Origin</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Origin URL"
            placeholder="https://example.com"
            value={newOrigin}
            onChange={(e) => setNewOrigin(e.target.value)}
            sx={{ mt: 1 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNewOriginDialog(false)}>Cancel</Button>
          <Button onClick={addOrigin} variant="contained">Add</Button>
        </DialogActions>
      </Dialog>

      {loading && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 9999 }}>
          <LinearProgress />
        </Box>
      )}
    </Box>
  );
};

export default Settings; 