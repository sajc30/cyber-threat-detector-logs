import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Button,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  LinearProgress,
  Tooltip,
  Badge,
  Grid,
} from '@mui/material';
import {
  Warning,
  Security,
  Visibility,
  Block,
  CheckCircle,
  Schedule,
  FilterList,
  Refresh,
  GetApp,
  DeleteForever,
  PlayArrow,
  Pause,
  Info,
  TrendingUp,
  Shield,
  BugReport,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

// Types
interface ActiveThreat {
  id: string;
  timestamp: string;
  source_ip: string;
  threat_type: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  confidence: number;
  status: 'Active' | 'Investigating' | 'Mitigated' | 'False Positive';
  description: string;
  affected_systems: string[];
  detection_method: string;
  indicators: string[];
  response_actions: string[];
  assigned_analyst?: string;
  estimated_impact: string;
  attack_vector: string;
}

interface ThreatStats {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  active: number;
  mitigated: number;
}

const ActiveThreats: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedThreat, setSelectedThreat] = useState<ActiveThreat | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>('All');
  const [filterStatus, setFilterStatus] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(false);

  // Mock data - replace with API calls
  const [threats, setThreats] = useState<ActiveThreat[]>([
    {
      id: 'THR-001',
      timestamp: '2024-01-20 14:30:25',
      source_ip: '192.168.1.100',
      threat_type: 'SQL Injection',
      severity: 'Critical',
      confidence: 95,
      status: 'Active',
      description: 'Multiple SQL injection attempts detected targeting user authentication system',
      affected_systems: ['Web Server 01', 'Database Primary'],
      detection_method: 'AI Pattern Recognition',
      indicators: ['malicious SQL patterns', 'authentication bypass attempts', 'unusual query structure'],
      response_actions: ['Block source IP', 'Enable WAF strict mode', 'Alert security team'],
      assigned_analyst: 'Sarah Chen',
      estimated_impact: 'High - Potential data breach',
      attack_vector: 'Web Application'
    },
    {
      id: 'THR-002',
      timestamp: '2024-01-20 14:25:12',
      source_ip: '10.0.0.45',
      threat_type: 'Brute Force Attack',
      severity: 'High',
      confidence: 88,
      status: 'Investigating',
      description: 'Sustained brute force attack against SSH service with credential enumeration',
      affected_systems: ['SSH Server', 'Authentication Service'],
      detection_method: 'Behavioral Analysis',
      indicators: ['repeated failed login attempts', 'credential enumeration', 'automated attack patterns'],
      response_actions: ['Rate limit IP', 'Enable 2FA enforcement', 'Monitor for lateral movement'],
      assigned_analyst: 'Mike Rodriguez',
      estimated_impact: 'Medium - Account compromise risk',
      attack_vector: 'Network Service'
    },
    {
      id: 'THR-003',
      timestamp: '2024-01-20 14:20:45',
      source_ip: '203.0.113.15',
      threat_type: 'Malware Download',
      severity: 'High',
      confidence: 92,
      status: 'Mitigated',
      description: 'Malicious file download attempt blocked by endpoint protection',
      affected_systems: ['Workstation WS-045'],
      detection_method: 'Signature Detection',
      indicators: ['known malware hash', 'suspicious download behavior', 'C2 communication attempt'],
      response_actions: ['Quarantine file', 'Scan system', 'Update signatures'],
      assigned_analyst: 'Alex Kim',
      estimated_impact: 'Low - Contained by endpoint protection',
      attack_vector: 'Email/Web'
    },
    {
      id: 'THR-004',
      timestamp: '2024-01-20 14:15:30',
      source_ip: '172.16.0.89',
      threat_type: 'Privilege Escalation',
      severity: 'Critical',
      confidence: 89,
      status: 'Active',
      description: 'Unauthorized privilege escalation attempt detected on domain controller',
      affected_systems: ['Domain Controller DC-01'],
      detection_method: 'Behavioral Analysis',
      indicators: ['unusual admin activity', 'privilege escalation techniques', 'lateral movement patterns'],
      response_actions: ['Isolate system', 'Revoke elevated permissions', 'Forensic analysis'],
      assigned_analyst: 'Sarah Chen',
      estimated_impact: 'Critical - Domain compromise risk',
      attack_vector: 'Internal Network'
    },
    {
      id: 'THR-005',
      timestamp: '2024-01-20 14:10:15',
      source_ip: '198.51.100.22',
      threat_type: 'Data Exfiltration',
      severity: 'Medium',
      confidence: 76,
      status: 'Investigating',
      description: 'Unusual data transfer patterns suggesting potential data exfiltration',
      affected_systems: ['File Server FS-02', 'Network Gateway'],
      detection_method: 'Traffic Analysis',
      indicators: ['large data transfers', 'unusual timing patterns', 'encrypted tunneling'],
      response_actions: ['Monitor traffic', 'Analyze data flows', 'Check data sensitivity'],
      assigned_analyst: 'Jordan Park',
      estimated_impact: 'Medium - Sensitive data at risk',
      attack_vector: 'Network Traffic'
    }
  ]);

  // Calculate threat statistics
  const [threatStats, setThreatStats] = useState<ThreatStats>({
    total: 0,
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    active: 0,
    mitigated: 0
  });

  // Threat timeline data for charts
  const [threatTimeline, setThreatTimeline] = useState([
    { time: '12:00', threats: 2, resolved: 1 },
    { time: '13:00', threats: 4, resolved: 2 },
    { time: '14:00', threats: 8, resolved: 3 },
    { time: '15:00', threats: 5, resolved: 6 },
    { time: '16:00', threats: 3, resolved: 2 },
  ]);

  // Update statistics when threats change
  useEffect(() => {
    const stats: ThreatStats = {
      total: threats.length,
      critical: threats.filter(t => t.severity === 'Critical').length,
      high: threats.filter(t => t.severity === 'High').length,
      medium: threats.filter(t => t.severity === 'Medium').length,
      low: threats.filter(t => t.severity === 'Low').length,
      active: threats.filter(t => t.status === 'Active').length,
      mitigated: threats.filter(t => t.status === 'Mitigated').length,
    };
    setThreatStats(stats);
  }, [threats]);

  // Auto-refresh functionality
  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        // Simulate new threat data
        refreshThreats();
      }, 30000); // 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const refreshThreats = () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setLoading(false);
    }, 1000);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'Critical': return 'error';
      case 'High': return 'warning';
      case 'Medium': return 'info';
      case 'Low': return 'success';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'error';
      case 'Investigating': return 'warning';
      case 'Mitigated': return 'success';
      case 'False Positive': return 'default';
      default: return 'default';
    }
  };

  const handleThreatClick = (threat: ActiveThreat) => {
    setSelectedThreat(threat);
    setDetailsDialogOpen(true);
  };

  const updateThreatStatus = (threatId: string, newStatus: string) => {
    setThreats(prev => prev.map(threat => 
      threat.id === threatId ? { ...threat, status: newStatus as any } : threat
    ));
  };

  const filteredThreats = threats.filter(threat => {
    const matchesSeverity = filterSeverity === 'All' || threat.severity === filterSeverity;
    const matchesStatus = filterStatus === 'All' || threat.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      threat.threat_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      threat.source_ip.includes(searchTerm) ||
      threat.description.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSeverity && matchesStatus && matchesSearch;
  });

  const severityDistribution = [
    { name: 'Critical', value: threatStats.critical, color: '#d32f2f' },
    { name: 'High', value: threatStats.high, color: '#f57c00' },
    { name: 'Medium', value: threatStats.medium, color: '#1976d2' },
    { name: 'Low', value: threatStats.low, color: '#388e3c' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center' }}>
            <Warning sx={{ mr: 2, color: 'error.main' }} />
            Active Threats
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Real-time threat monitoring and incident management
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={autoRefresh ? <Pause /> : <PlayArrow />}
            onClick={() => setAutoRefresh(!autoRefresh)}
            color={autoRefresh ? 'warning' : 'success'}
          >
            {autoRefresh ? 'Pause' : 'Resume'} Auto-Refresh
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={refreshThreats}
            disabled={loading}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Statistics Cards */}
      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(5, 1fr)' },
        gap: 3,
        mb: 3
      }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Shield sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Total</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
              {threatStats.total}
            </Typography>
            <Typography variant="body2" color="text.secondary">Active threats</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Warning sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Critical</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'error.main' }}>
              {threatStats.critical}
            </Typography>
            <Typography variant="body2" color="text.secondary">Immediate attention</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <TrendingUp sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>High</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'warning.main' }}>
              {threatStats.high}
            </Typography>
            <Typography variant="body2" color="text.secondary">High priority</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Security sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Mitigated</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main' }}>
              {threatStats.mitigated}
            </Typography>
            <Typography variant="body2" color="text.secondary">Successfully resolved</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <BugReport sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Under Investigation</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'info.main' }}>
              {threats.filter(t => t.status === 'Investigating').length}
            </Typography>
            <Typography variant="body2" color="text.secondary">Being analyzed</Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Tabs */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<Warning />} label="Active Threats" />
          <Tab icon={<TrendingUp />} label="Threat Timeline" />
          <Tab icon={<Shield />} label="Threat Analytics" />
        </Tabs>
      </Card>

      {/* Active Threats Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            {/* Filters */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
              <TextField
                placeholder="Search threats..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{ minWidth: 200 }}
              />
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={filterSeverity}
                  onChange={(e) => setFilterSeverity(e.target.value)}
                  label="Severity"
                >
                  <MenuItem value="All">All</MenuItem>
                  <MenuItem value="Critical">Critical</MenuItem>
                  <MenuItem value="High">High</MenuItem>
                  <MenuItem value="Medium">Medium</MenuItem>
                  <MenuItem value="Low">Low</MenuItem>
                </Select>
              </FormControl>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Status</InputLabel>
                <Select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  label="Status"
                >
                  <MenuItem value="All">All</MenuItem>
                  <MenuItem value="Active">Active</MenuItem>
                  <MenuItem value="Investigating">Investigating</MenuItem>
                  <MenuItem value="Mitigated">Mitigated</MenuItem>
                  <MenuItem value="False Positive">False Positive</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Threats Table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Threat ID</TableCell>
                    <TableCell>Timestamp</TableCell>
                    <TableCell>Source IP</TableCell>
                    <TableCell>Threat Type</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Analyst</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredThreats.map((threat) => (
                    <TableRow 
                      key={threat.id} 
                      hover 
                      sx={{ cursor: 'pointer' }}
                      onClick={() => handleThreatClick(threat)}
                    >
                      <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                        {threat.id}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace' }}>
                        {threat.timestamp}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace' }}>
                        {threat.source_ip}
                      </TableCell>
                      <TableCell>{threat.threat_type}</TableCell>
                      <TableCell>
                        <Chip
                          label={threat.severity}
                          color={getSeverityColor(threat.severity)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={threat.status}
                          color={getStatusColor(threat.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Badge badgeContent={`${threat.confidence}%`} color="primary">
                          <LinearProgress
                            variant="determinate"
                            value={threat.confidence}
                            sx={{ width: 60, height: 6, borderRadius: 1 }}
                          />
                        </Badge>
                      </TableCell>
                      <TableCell>{threat.assigned_analyst || 'Unassigned'}</TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleThreatClick(threat); }}>
                          <Visibility />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>
      )}

      {/* Threat Timeline Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              📈 Threat Activity Timeline
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={threatTimeline}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="time" />
                  <YAxis />
                  <ChartTooltip />
                  <Line type="monotone" dataKey="threats" stroke="#ff4444" strokeWidth={2} name="New Threats" />
                  <Line type="monotone" dataKey="resolved" stroke="#00ff88" strokeWidth={2} name="Resolved" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Threat Analytics Tab */}
      {activeTab === 2 && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🥧 Severity Distribution
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={severityDistribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={(entry) => `${entry.name}: ${entry.value}`}
                    >
                      {severityDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <ChartTooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🎯 Top Threat Types
              </Typography>
              {['SQL Injection', 'Brute Force Attack', 'Malware Download', 'Privilege Escalation', 'Data Exfiltration'].map((type, index) => (
                <Box key={type} sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">{type}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {Math.floor(Math.random() * 20) + 1}
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={(5 - index) * 20}
                    sx={{ height: 6, borderRadius: 1 }}
                  />
                </Box>
              ))}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Threat Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Threat Details: {selectedThreat?.id}</Typography>
            <Box>
              <Chip
                label={selectedThreat?.severity}
                color={getSeverityColor(selectedThreat?.severity || '')}
                size="small"
                sx={{ mr: 1 }}
              />
              <Chip
                label={selectedThreat?.status}
                color={getStatusColor(selectedThreat?.status || '')}
                size="small"
              />
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedThreat && (
            <Box sx={{ display: 'grid', gap: 3 }}>
              <Alert severity={selectedThreat.severity === 'Critical' ? 'error' : 'warning'}>
                <Typography variant="body1" sx={{ fontWeight: 600 }}>
                  {selectedThreat.description}
                </Typography>
              </Alert>

              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Source Information
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                    IP: {selectedThreat.source_ip}
                  </Typography>
                  <Typography variant="body2">
                    Attack Vector: {selectedThreat.attack_vector}
                  </Typography>
                  <Typography variant="body2">
                    Detection Method: {selectedThreat.detection_method}
                  </Typography>
                </Box>
                
                <Box>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Impact Assessment
                  </Typography>
                  <Typography variant="body2">
                    Confidence: {selectedThreat.confidence}%
                  </Typography>
                  <Typography variant="body2">
                    Estimated Impact: {selectedThreat.estimated_impact}
                  </Typography>
                  <Typography variant="body2">
                    Assigned Analyst: {selectedThreat.assigned_analyst || 'Unassigned'}
                  </Typography>
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Affected Systems
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedThreat.affected_systems.map((system) => (
                    <Chip key={system} label={system} variant="outlined" size="small" />
                  ))}
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Threat Indicators
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedThreat.indicators.map((indicator) => (
                    <Chip key={indicator} label={indicator} color="warning" size="small" />
                  ))}
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                  Response Actions
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedThreat.response_actions.map((action) => (
                    <Chip key={action} label={action} color="success" size="small" />
                  ))}
                </Box>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            color="warning"
            onClick={() => selectedThreat && updateThreatStatus(selectedThreat.id, 'Investigating')}
          >
            Start Investigation
          </Button>
          <Button 
            variant="contained" 
            color="success"
            onClick={() => selectedThreat && updateThreatStatus(selectedThreat.id, 'Mitigated')}
          >
            Mark as Mitigated
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ActiveThreats; 