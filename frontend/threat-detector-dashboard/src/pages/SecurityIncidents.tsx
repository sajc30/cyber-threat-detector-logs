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
  Stepper,
  Step,
  StepLabel,
  StepContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Avatar,
} from '@mui/material';
import {
  BugReport,
  Security,
  Assignment,
  CheckCircle,
  Schedule,
  Warning,
  Error,
  Info,
  Visibility,
  Edit,
  Add,
  Person,
  Timeline as TimelineIcon,
  Assessment,
  PlayArrow,
  Pause,
  Refresh,
  AssignmentTurnedIn,
  NotificationImportant,
  Shield,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';

// Types
interface SecurityIncident {
  id: string;
  title: string;
  description: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  status: 'Open' | 'In Progress' | 'Under Investigation' | 'Resolved' | 'Closed';
  priority: 'P1' | 'P2' | 'P3' | 'P4';
  category: 'Malware' | 'Data Breach' | 'Phishing' | 'Insider Threat' | 'Network Attack' | 'System Compromise';
  created_date: string;
  updated_date: string;
  assigned_to: string;
  reporter: string;
  affected_assets: string[];
  timeline: IncidentTimelineEvent[];
  impact_assessment: string;
  resolution_summary?: string;
  lessons_learned?: string;
  estimated_cost?: number;
  compliance_impact?: string;
}

interface IncidentTimelineEvent {
  id: string;
  timestamp: string;
  event_type: 'created' | 'assigned' | 'updated' | 'escalated' | 'resolved' | 'closed';
  description: string;
  user: string;
  details?: string;
}

interface IncidentStats {
  total: number;
  open: number;
  inProgress: number;
  resolved: number;
  closed: number;
  averageResolutionTime: number;
  criticalIncidents: number;
}

const SecurityIncidents: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedIncident, setSelectedIncident] = useState<SecurityIncident | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [filterSeverity, setFilterSeverity] = useState<string>('All');
  const [filterStatus, setFilterStatus] = useState<string>('All');
  const [filterCategory, setFilterCategory] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  // Mock data - replace with API calls
  const [incidents, setIncidents] = useState<SecurityIncident[]>([
    {
      id: 'INC-001',
      title: 'Ransomware Attack on File Server',
      description: 'Multiple files encrypted with suspicious .locked extension detected on primary file server',
      severity: 'Critical',
      status: 'In Progress',
      priority: 'P1',
      category: 'Malware',
      created_date: '2024-01-20 09:15:00',
      updated_date: '2024-01-20 14:30:00',
      assigned_to: 'Sarah Chen',
      reporter: 'System Monitor',
      affected_assets: ['File Server FS-01', 'Backup System', 'User Workstations'],
      impact_assessment: 'High - Critical business data encrypted, operations severely impacted',
      estimated_cost: 50000,
      compliance_impact: 'GDPR notification required within 72 hours',
      timeline: [
        {
          id: 'evt-001',
          timestamp: '2024-01-20 09:15:00',
          event_type: 'created',
          description: 'Incident created by automated monitoring system',
          user: 'System Monitor',
          details: 'Ransomware signatures detected'
        },
        {
          id: 'evt-002',
          timestamp: '2024-01-20 09:20:00',
          event_type: 'assigned',
          description: 'Incident assigned to security team lead',
          user: 'Security Manager',
          details: 'Escalated to P1 priority due to critical nature'
        },
        {
          id: 'evt-003',
          timestamp: '2024-01-20 10:30:00',
          event_type: 'updated',
          description: 'File server isolated from network',
          user: 'Sarah Chen',
          details: 'Network containment measures implemented'
        }
      ]
    },
    {
      id: 'INC-002',
      title: 'Data Exfiltration Attempt',
      description: 'Unusual large data transfer patterns detected to external IP addresses',
      severity: 'High',
      status: 'Under Investigation',
      priority: 'P2',
      category: 'Data Breach',
      created_date: '2024-01-20 11:45:00',
      updated_date: '2024-01-20 13:15:00',
      assigned_to: 'Mike Rodriguez',
      reporter: 'Network Admin',
      affected_assets: ['Database Server', 'Network Gateway', 'Web Application'],
      impact_assessment: 'Medium - Potential customer data exposure',
      estimated_cost: 25000,
      compliance_impact: 'SOX compliance review required',
      timeline: [
        {
          id: 'evt-004',
          timestamp: '2024-01-20 11:45:00',
          event_type: 'created',
          description: 'Incident reported by network monitoring',
          user: 'Network Admin',
          details: 'Anomalous data flow patterns detected'
        },
        {
          id: 'evt-005',
          timestamp: '2024-01-20 12:00:00',
          event_type: 'assigned',
          description: 'Assigned to incident response team',
          user: 'Security Manager',
          details: 'Initial triage completed'
        }
      ]
    },
    {
      id: 'INC-003',
      title: 'Phishing Campaign Targeting Employees',
      description: 'Multiple employees reported suspicious emails requesting credential verification',
      severity: 'Medium',
      status: 'Resolved',
      priority: 'P3',
      category: 'Phishing',
      created_date: '2024-01-19 14:20:00',
      updated_date: '2024-01-20 10:00:00',
      assigned_to: 'Alex Kim',
      reporter: 'HR Department',
      affected_assets: ['Email System', 'User Accounts', 'Corporate Website'],
      impact_assessment: 'Low - No credentials compromised, blocked before impact',
      resolution_summary: 'Phishing emails blocked, user awareness training conducted',
      lessons_learned: 'Implement additional email filtering rules for similar patterns',
      estimated_cost: 5000,
      timeline: [
        {
          id: 'evt-006',
          timestamp: '2024-01-19 14:20:00',
          event_type: 'created',
          description: 'Multiple phishing reports received',
          user: 'HR Department',
          details: 'Employees forwarded suspicious emails'
        },
        {
          id: 'evt-007',
          timestamp: '2024-01-19 15:00:00',
          event_type: 'assigned',
          description: 'Assigned to security analyst',
          user: 'Security Manager',
          details: 'Standard phishing response protocol initiated'
        },
        {
          id: 'evt-008',
          timestamp: '2024-01-20 10:00:00',
          event_type: 'resolved',
          description: 'Incident resolved, emails blocked',
          user: 'Alex Kim',
          details: 'All malicious emails quarantined and blocked'
        }
      ]
    },
    {
      id: 'INC-004',
      title: 'Insider Threat Investigation',
      description: 'Unusual after-hours access patterns detected for privileged user account',
      severity: 'High',
      status: 'Open',
      priority: 'P2',
      category: 'Insider Threat',
      created_date: '2024-01-20 08:30:00',
      updated_date: '2024-01-20 08:30:00',
      assigned_to: 'Jordan Park',
      reporter: 'SIEM System',
      affected_assets: ['Active Directory', 'File Servers', 'Database Systems'],
      impact_assessment: 'High - Potential unauthorized access to sensitive data',
      estimated_cost: 35000,
      compliance_impact: 'Internal audit required',
      timeline: [
        {
          id: 'evt-009',
          timestamp: '2024-01-20 08:30:00',
          event_type: 'created',
          description: 'Suspicious access patterns detected',
          user: 'SIEM System',
          details: 'Multiple failed login attempts followed by successful access'
        }
      ]
    }
  ]);

  // Calculate incident statistics
  const [incidentStats, setIncidentStats] = useState<IncidentStats>({
    total: 0,
    open: 0,
    inProgress: 0,
    resolved: 0,
    closed: 0,
    averageResolutionTime: 0,
    criticalIncidents: 0
  });

  // Chart data
  const [incidentTrends, setIncidentTrends] = useState([
    { date: '2024-01-15', created: 3, resolved: 2 },
    { date: '2024-01-16', created: 5, resolved: 3 },
    { date: '2024-01-17', created: 2, resolved: 4 },
    { date: '2024-01-18', created: 4, resolved: 3 },
    { date: '2024-01-19', created: 6, resolved: 5 },
    { date: '2024-01-20', created: 4, resolved: 2 },
  ]);

  // Update statistics when incidents change
  useEffect(() => {
    const stats: IncidentStats = {
      total: incidents.length,
      open: incidents.filter(i => i.status === 'Open').length,
      inProgress: incidents.filter(i => i.status === 'In Progress' || i.status === 'Under Investigation').length,
      resolved: incidents.filter(i => i.status === 'Resolved').length,
      closed: incidents.filter(i => i.status === 'Closed').length,
      averageResolutionTime: 24.5, // Mock calculation
      criticalIncidents: incidents.filter(i => i.severity === 'Critical').length
    };
    setIncidentStats(stats);
  }, [incidents]);

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
      case 'Open': return 'error';
      case 'In Progress': return 'warning';
      case 'Under Investigation': return 'info';
      case 'Resolved': return 'success';
      case 'Closed': return 'default';
      default: return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'P1': return 'error';
      case 'P2': return 'warning';
      case 'P3': return 'info';
      case 'P4': return 'default';
      default: return 'default';
    }
  };

  const getTimelineIcon = (eventType: string) => {
    switch (eventType) {
      case 'created': return <Add />;
      case 'assigned': return <Person />;
      case 'updated': return <Edit />;
      case 'escalated': return <Warning />;
      case 'resolved': return <CheckCircle />;
      case 'closed': return <AssignmentTurnedIn />;
      default: return <Info />;
    }
  };

  const handleIncidentClick = (incident: SecurityIncident) => {
    setSelectedIncident(incident);
    setDetailsDialogOpen(true);
  };

  const updateIncidentStatus = (incidentId: string, newStatus: string) => {
    setIncidents(prev => prev.map(incident => 
      incident.id === incidentId ? { 
        ...incident, 
        status: newStatus as any,
        updated_date: new Date().toISOString().slice(0, 19).replace('T', ' ')
      } : incident
    ));
  };

  const filteredIncidents = incidents.filter(incident => {
    const matchesSeverity = filterSeverity === 'All' || incident.severity === filterSeverity;
    const matchesStatus = filterStatus === 'All' || incident.status === filterStatus;
    const matchesCategory = filterCategory === 'All' || incident.category === filterCategory;
    const matchesSearch = searchTerm === '' || 
      incident.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      incident.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      incident.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    return matchesSeverity && matchesStatus && matchesCategory && matchesSearch;
  });

  const categoryDistribution = [
    { name: 'Malware', value: incidents.filter(i => i.category === 'Malware').length, color: '#d32f2f' },
    { name: 'Data Breach', value: incidents.filter(i => i.category === 'Data Breach').length, color: '#f57c00' },
    { name: 'Phishing', value: incidents.filter(i => i.category === 'Phishing').length, color: '#1976d2' },
    { name: 'Insider Threat', value: incidents.filter(i => i.category === 'Insider Threat').length, color: '#388e3c' },
    { name: 'Network Attack', value: incidents.filter(i => i.category === 'Network Attack').length, color: '#7b1fa2' },
    { name: 'System Compromise', value: incidents.filter(i => i.category === 'System Compromise').length, color: '#00796b' },
  ];

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center' }}>
            <BugReport sx={{ mr: 2, color: 'warning.main' }} />
            Security Incidents
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Comprehensive incident management and response tracking
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<Add />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Create Incident
          </Button>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => setLoading(true)}
          >
            Refresh
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      {/* Statistics Cards */}
      <Box sx={{ 
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
        gap: 3,
        mb: 3
      }}>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Shield sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Total Incidents</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
              {incidentStats.total}
            </Typography>
            <Typography variant="body2" color="text.secondary">All time</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Warning sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Critical</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'error.main' }}>
              {incidentStats.criticalIncidents}
            </Typography>
            <Typography variant="body2" color="text.secondary">Needs immediate attention</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Schedule sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>In Progress</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'warning.main' }}>
              {incidentStats.inProgress}
            </Typography>
            <Typography variant="body2" color="text.secondary">Being investigated</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Resolved</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main' }}>
              {incidentStats.resolved}
            </Typography>
            <Typography variant="body2" color="text.secondary">Successfully resolved</Typography>
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
          <Tab icon={<BugReport />} label="All Incidents" />
          <Tab icon={<TimelineIcon />} label="Incident Trends" />
          <Tab icon={<Assessment />} label="Analytics" />
        </Tabs>
      </Card>

      {/* All Incidents Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            {/* Filters */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
              <TextField
                placeholder="Search incidents..."
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
                  <MenuItem value="Open">Open</MenuItem>
                  <MenuItem value="In Progress">In Progress</MenuItem>
                  <MenuItem value="Under Investigation">Under Investigation</MenuItem>
                  <MenuItem value="Resolved">Resolved</MenuItem>
                  <MenuItem value="Closed">Closed</MenuItem>
                </Select>
              </FormControl>
              <FormControl sx={{ minWidth: 120 }}>
                <InputLabel>Category</InputLabel>
                <Select
                  value={filterCategory}
                  onChange={(e) => setFilterCategory(e.target.value)}
                  label="Category"
                >
                  <MenuItem value="All">All</MenuItem>
                  <MenuItem value="Malware">Malware</MenuItem>
                  <MenuItem value="Data Breach">Data Breach</MenuItem>
                  <MenuItem value="Phishing">Phishing</MenuItem>
                  <MenuItem value="Insider Threat">Insider Threat</MenuItem>
                  <MenuItem value="Network Attack">Network Attack</MenuItem>
                  <MenuItem value="System Compromise">System Compromise</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Incidents Table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Incident ID</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Assigned To</TableCell>
                    <TableCell>Created Date</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredIncidents.map((incident) => (
                    <TableRow 
                      key={incident.id} 
                      hover 
                      sx={{ cursor: 'pointer' }}
                      onClick={() => handleIncidentClick(incident)}
                    >
                      <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                        {incident.id}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {incident.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {incident.description.substring(0, 60)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={incident.severity}
                          color={getSeverityColor(incident.severity)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={incident.status}
                          color={getStatusColor(incident.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={incident.priority}
                          color={getPriorityColor(incident.priority)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{incident.category}</TableCell>
                      <TableCell>{incident.assigned_to}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace' }}>
                        {incident.created_date}
                      </TableCell>
                      <TableCell>
                        <IconButton size="small" onClick={(e) => { e.stopPropagation(); handleIncidentClick(incident); }}>
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

      {/* Incident Trends Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              📈 Incident Creation vs Resolution Trends
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={incidentTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <ChartTooltip />
                  <Line type="monotone" dataKey="created" stroke="#ff4444" strokeWidth={2} name="Created" />
                  <Line type="monotone" dataKey="resolved" stroke="#00ff88" strokeWidth={2} name="Resolved" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Analytics Tab */}
      {activeTab === 2 && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🥧 Incident Categories
              </Typography>
              <Box sx={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categoryDistribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      dataKey="value"
                      label={(entry) => `${entry.name}: ${entry.value}`}
                    >
                      {categoryDistribution.map((entry, index) => (
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
                📊 Key Metrics
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Average Resolution Time
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                    {incidentStats.averageResolutionTime}h
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Total Estimated Cost
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'warning.main' }}>
                    ${incidents.reduce((sum, i) => sum + (i.estimated_cost || 0), 0).toLocaleString()}
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Incidents This Month
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, color: 'info.main' }}>
                    {incidents.length}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Incident Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Incident Details: {selectedIncident?.id}</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label={selectedIncident?.severity}
                color={getSeverityColor(selectedIncident?.severity || '')}
                size="small"
              />
              <Chip
                label={selectedIncident?.status}
                color={getStatusColor(selectedIncident?.status || '')}
                size="small"
              />
              <Chip
                label={selectedIncident?.priority}
                color={getPriorityColor(selectedIncident?.priority || '')}
                size="small"
              />
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedIncident && (
            <Box sx={{ display: 'grid', gap: 3 }}>
              <Alert severity={selectedIncident.severity === 'Critical' ? 'error' : 'warning'}>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {selectedIncident.title}
                </Typography>
                <Typography variant="body1">
                  {selectedIncident.description}
                </Typography>
              </Alert>

              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    📋 Incident Information
                  </Typography>
                  <Box sx={{ display: 'grid', gap: 1 }}>
                    <Typography variant="body2">
                      <strong>Category:</strong> {selectedIncident.category}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Assigned To:</strong> {selectedIncident.assigned_to}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Reporter:</strong> {selectedIncident.reporter}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Created:</strong> {selectedIncident.created_date}
                    </Typography>
                    <Typography variant="body2">
                      <strong>Last Updated:</strong> {selectedIncident.updated_date}
                    </Typography>
                    {selectedIncident.estimated_cost && (
                      <Typography variant="body2">
                        <strong>Estimated Cost:</strong> ${selectedIncident.estimated_cost.toLocaleString()}
                      </Typography>
                    )}
                  </Box>
                </Box>

                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    🎯 Impact Assessment
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 2 }}>
                    {selectedIncident.impact_assessment}
                  </Typography>
                  {selectedIncident.compliance_impact && (
                    <Alert severity="info" sx={{ mb: 2 }}>
                      <Typography variant="body2">
                        <strong>Compliance Impact:</strong> {selectedIncident.compliance_impact}
                      </Typography>
                    </Alert>
                  )}
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                  🏢 Affected Assets
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {selectedIncident.affected_assets.map((asset) => (
                    <Chip key={asset} label={asset} variant="outlined" size="small" />
                  ))}
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                  ⏰ Timeline
                </Typography>
                <List>
                  {selectedIncident.timeline.map((event) => (
                    <ListItem key={event.id}>
                      <ListItemIcon>
                        {getTimelineIcon(event.event_type)}
                      </ListItemIcon>
                      <ListItemText
                        primary={event.description}
                        secondary={`${event.timestamp} by ${event.user} ${event.details ? '- ' + event.details : ''}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </Box>

              {selectedIncident.resolution_summary && (
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    ✅ Resolution Summary
                  </Typography>
                  <Alert severity="success">
                    <Typography variant="body2">
                      {selectedIncident.resolution_summary}
                    </Typography>
                  </Alert>
                </Box>
              )}

              {selectedIncident.lessons_learned && (
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    💡 Lessons Learned
                  </Typography>
                  <Alert severity="info">
                    <Typography variant="body2">
                      {selectedIncident.lessons_learned}
                    </Typography>
                  </Alert>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          <Button 
            variant="contained" 
            color="warning"
            onClick={() => selectedIncident && updateIncidentStatus(selectedIncident.id, 'In Progress')}
          >
            Start Investigation
          </Button>
          <Button 
            variant="contained" 
            color="success"
            onClick={() => selectedIncident && updateIncidentStatus(selectedIncident.id, 'Resolved')}
          >
            Mark as Resolved
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SecurityIncidents; 