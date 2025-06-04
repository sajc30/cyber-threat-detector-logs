import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Chip,
  Tab,
  Tabs,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Tooltip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Alert,
  Divider,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Badge,
} from '@mui/material';
import {
  TrendingUp,
  Security,
  Speed,
  Assessment,
  Download,
  Refresh,
  PieChart,
  Map,
  BugReport,
  Shield,
  Psychology,
  Timeline,
  FindInPage,
  SmartToy,
  ExpandMore,
  Warning,
  CheckCircle,
  Error,
  Info,
  Visibility,
  Search,
  FilterList,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart as RechartsBarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ComposedChart,
  ReferenceLine,
} from 'recharts';

// Sample analytics data (in a real app, this would come from your backend)
const generateSampleData = () => {
  const now = new Date();
  const last30Days = Array.from({ length: 30 }, (_, i) => {
    const date = new Date(now);
    date.setDate(date.getDate() - (29 - i));
    return {
      date: date.toISOString().split('T')[0],
      day: date.toLocaleDateString('en-US', { weekday: 'short' }),
      sqlInjection: Math.floor(Math.random() * 50) + 10,
      xss: Math.floor(Math.random() * 40) + 5,
      bruteForce: Math.floor(Math.random() * 30) + 8,
      directoryTraversal: Math.floor(Math.random() * 20) + 3,
      total: 0,
      responseTime: Math.random() * 100 + 50,
      successRate: Math.random() * 20 + 80,
    };
  });

  // Calculate totals
  last30Days.forEach(day => {
    day.total = day.sqlInjection + day.xss + day.bruteForce + day.directoryTraversal;
  });

  return last30Days;
};

const threatTypeDistribution = [
  { name: 'SQL Injection', value: 342, color: '#f44336', severity: 'High' },
  { name: 'Cross-Site Scripting', value: 287, color: '#ff9800', severity: 'Medium' },
  { name: 'Brute Force Attack', value: 156, color: '#2196f3', severity: 'Medium' },
  { name: 'Directory Traversal', value: 89, color: '#9c27b0', severity: 'Low' },
  { name: 'Code Injection', value: 67, color: '#4caf50', severity: 'High' },
  { name: 'CSRF', value: 45, color: '#00bcd4', severity: 'Medium' },
];

const geographicData = [
  { country: 'China', attacks: 145, lat: 35.8617, lng: 104.1954 },
  { country: 'Russia', attacks: 123, lat: 61.5240, lng: 105.3188 },
  { country: 'United States', attacks: 98, lat: 37.0902, lng: -95.7129 },
  { country: 'Brazil', attacks: 76, lat: -14.2350, lng: -51.9253 },
  { country: 'India', attacks: 65, lat: 20.5937, lng: 78.9629 },
  { country: 'Germany', attacks: 54, lat: 51.1657, lng: 10.4515 },
  { country: 'United Kingdom', attacks: 43, lat: 55.3781, lng: -3.4360 },
  { country: 'Iran', attacks: 38, lat: 32.4279, lng: 53.6880 },
];

const severityRadarData = [
  { subject: 'Critical', A: 85, B: 110, fullMark: 150 },
  { subject: 'High', A: 120, B: 130, fullMark: 150 },
  { subject: 'Medium', A: 95, B: 100, fullMark: 150 },
  { subject: 'Low', A: 45, B: 85, fullMark: 150 },
  { subject: 'Info', A: 25, B: 40, fullMark: 150 },
];

const topAttackers = [
  { ip: '192.168.1.100', attacks: 45, country: 'CN', lastSeen: '2 hours ago' },
  { ip: '10.0.0.45', attacks: 38, country: 'RU', lastSeen: '4 hours ago' },
  { ip: '172.16.0.23', attacks: 32, country: 'US', lastSeen: '1 hour ago' },
  { ip: '203.0.113.15', attacks: 28, country: 'BR', lastSeen: '30 min ago' },
  { ip: '198.51.100.8', attacks: 24, country: 'DE', lastSeen: '6 hours ago' },
];

// New Advanced Analytics Data
const threatIntelligence = [
  {
    id: 'TI-001',
    indicator: '192.168.1.100',
    type: 'IP Address',
    threatLevel: 'High',
    firstSeen: '2024-01-15',
    lastSeen: '2 hours ago',
    occurrences: 47,
    associatedCampaigns: ['APT-29', 'Lazarus Group'],
    reputation: 'Malicious',
    confidence: 95,
    tags: ['botnet', 'c2-server', 'apt'],
    description: 'Known C&C server associated with APT-29 operations'
  },
  {
    id: 'TI-002',
    indicator: 'malware.example.com',
    type: 'Domain',
    threatLevel: 'Critical',
    firstSeen: '2024-01-10',
    lastSeen: '30 min ago',
    occurrences: 23,
    associatedCampaigns: ['Operation Aurora'],
    reputation: 'Malicious',
    confidence: 99,
    tags: ['malware-distribution', 'phishing'],
    description: 'Active malware distribution domain'
  },
  {
    id: 'TI-003',
    indicator: 'SHA256:a1b2c3d4e5f6...',
    type: 'File Hash',
    threatLevel: 'Medium',
    firstSeen: '2024-01-12',
    lastSeen: '4 hours ago',
    occurrences: 12,
    associatedCampaigns: ['Unknown'],
    reputation: 'Suspicious',
    confidence: 78,
    tags: ['trojan', 'stealer'],
    description: 'Suspicious executable with stealer capabilities'
  }
];

const predictiveAnalytics = {
  nextWeekPrediction: {
    sqlInjection: { predicted: 145, confidence: 87, trend: 'increasing' },
    xss: { predicted: 98, confidence: 82, trend: 'stable' },
    bruteForce: { predicted: 67, confidence: 91, trend: 'decreasing' },
    total: { predicted: 310, confidence: 85, trend: 'increasing' }
  },
  riskFactors: [
    { factor: 'Increased scanning activity', impact: 'High', probability: 89 },
    { factor: 'New vulnerability disclosure', impact: 'Critical', probability: 65 },
    { factor: 'Holiday period approaching', impact: 'Medium', probability: 95 },
    { factor: 'Geopolitical tensions', impact: 'High', probability: 71 }
  ],
  modelAccuracy: {
    last30Days: 89.3,
    last7Days: 92.1,
    yesterday: 94.7
  }
};

const forensicCases = [
  {
    id: 'CASE-001',
    title: 'Advanced Persistent Threat Investigation',
    status: 'Active',
    priority: 'Critical',
    assignee: 'Security Team Alpha',
    createdDate: '2024-01-15',
    lastUpdate: '2 hours ago',
    findings: 'Multiple compromised endpoints detected',
    indicators: 12,
    timeline: 'Day 5 of investigation'
  },
  {
    id: 'CASE-002',
    title: 'SQL Injection Campaign Analysis',
    status: 'Under Review',
    priority: 'High',
    assignee: 'Analyst John Doe',
    createdDate: '2024-01-18',
    lastUpdate: '1 day ago',
    findings: 'Automated attack pattern identified',
    indicators: 8,
    timeline: 'Day 2 of investigation'
  },
  {
    id: 'CASE-003',
    title: 'Insider Threat Assessment',
    status: 'Closed',
    priority: 'Medium',
    assignee: 'HR Security Team',
    createdDate: '2024-01-10',
    lastUpdate: '3 days ago',
    findings: 'No malicious activity confirmed',
    indicators: 3,
    timeline: 'Completed in 7 days'
  }
];

const mlInsights = [
  {
    type: 'Anomaly Detection',
    title: 'Unusual Traffic Pattern Detected',
    confidence: 94,
    impact: 'High',
    description: 'Machine learning model detected a 340% increase in traffic from Eastern Europe',
    recommendation: 'Implement geo-blocking for suspicious regions',
    timestamp: '2 hours ago'
  },
  {
    type: 'Behavioral Analysis',
    title: 'Admin Account Privilege Escalation',
    confidence: 87,
    impact: 'Critical',
    description: 'AI detected unusual privilege escalation pattern for admin account "sa_admin"',
    recommendation: 'Immediately review admin account activities and reset credentials',
    timestamp: '4 hours ago'
  },
  {
    type: 'Pattern Recognition',
    title: 'Coordinated Attack Campaign',
    confidence: 91,
    impact: 'High',
    description: 'Multiple IP addresses showing coordinated attack behavior',
    recommendation: 'Implement IP range blocking and enhance monitoring',
    timestamp: '6 hours ago'
  }
];

const Analytics: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [timeRange, setTimeRange] = useState('30d');
  const [analyticsData, setAnalyticsData] = useState(generateSampleData());
  const [loading, setLoading] = useState(false);
  
  // New states for Phase 5B features
  const [selectedIntelligence, setSelectedIntelligence] = useState<any>(null);
  const [forensicDialogOpen, setForensicDialogOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<any>(null);
  const [huntingQuery, setHuntingQuery] = useState('');
  const [huntingResults, setHuntingResults] = useState<any[]>([]);

  const refreshData = () => {
    setLoading(true);
    setTimeout(() => {
      setAnalyticsData(generateSampleData());
      setLoading(false);
    }, 1000);
  };

  const exportReport = () => {
    const reportData = {
      generated: new Date().toISOString(),
      timeRange,
      summary: {
        totalThreats: analyticsData.reduce((sum, day) => sum + day.total, 0),
        avgResponseTime: analyticsData.reduce((sum, day) => sum + day.responseTime, 0) / analyticsData.length,
        successRate: analyticsData.reduce((sum, day) => sum + day.successRate, 0) / analyticsData.length,
      },
      threatDistribution: threatTypeDistribution,
      topAttackers,
    };

    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `threat-analytics-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const totalThreats = analyticsData.reduce((sum, day) => sum + day.total, 0);
  const avgResponseTime = analyticsData.reduce((sum, day) => sum + day.responseTime, 0) / analyticsData.length;
  const successRate = analyticsData.reduce((sum, day) => sum + day.successRate, 0) / analyticsData.length;

  // New Phase 5B functions
  const handleThreatHunting = () => {
    if (!huntingQuery.trim()) return;
    
    // Simulate threat hunting results
    const mockResults = [
      {
        id: 'hunt-001',
        timestamp: '2024-01-20 14:30:25',
        source: '192.168.1.45',
        event: 'Suspicious PowerShell execution',
        severity: 'High',
        confidence: 89
      },
      {
        id: 'hunt-002',
        timestamp: '2024-01-20 14:25:12',
        source: '10.0.0.23',
        event: 'Unusual network connection pattern',
        severity: 'Medium',
        confidence: 76
      }
    ];
    
    setHuntingResults(mockResults);
  };

  const openForensicCase = (caseData: any) => {
    setSelectedCase(caseData);
    setForensicDialogOpen(true);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical': return 'error';
      case 'High': return 'warning';
      case 'Medium': return 'info';
      default: return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'error';
      case 'Under Review': return 'warning';
      case 'Closed': return 'success';
      default: return 'default';
    }
  };

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
            🔍 Advanced Threat Analytics & Intelligence
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered cybersecurity analytics with threat intelligence and forensic capabilities
          </Typography>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              label="Time Range"
              onChange={(e) => setTimeRange(e.target.value)}
            >
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
              <MenuItem value="90d">Last 90 Days</MenuItem>
              <MenuItem value="1y">Last Year</MenuItem>
            </Select>
          </FormControl>
          
          <Tooltip title="Refresh Data">
            <IconButton onClick={refreshData} disabled={loading}>
              <Refresh />
            </IconButton>
          </Tooltip>
          
          <Button
            variant="outlined"
            startIcon={<Download />}
            onClick={exportReport}
          >
            Export Report
          </Button>
        </Box>
      </Box>

      {/* AI Insights Alert */}
      <Alert 
        severity="warning" 
        sx={{ mb: 3 }}
        icon={<SmartToy />}
      >
        <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
          🤖 AI Insight: Potential coordinated attack detected
        </Typography>
        Machine learning algorithms identified unusual patterns suggesting a coordinated attack campaign. 
        Confidence: 94% | Recommended action: Immediate investigation
      </Alert>

      {/* Enhanced Summary Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', lg: 'repeat(5, 1fr)' },
          gap: 3,
          mb: 3,
        }}
      >
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Security sx={{ mr: 1, color: 'error.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Total Threats
              </Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'error.main' }}>
              {totalThreats.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              +12.5% from last month
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Psychology sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                AI Predictions
              </Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
              {predictiveAnalytics.nextWeekPrediction.total.predicted}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Predicted next week ({predictiveAnalytics.nextWeekPrediction.total.confidence}% confidence)
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <FindInPage sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Active Cases
              </Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'warning.main' }}>
              {forensicCases.filter(c => c.status === 'Active').length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Forensic investigations
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Speed sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Model Accuracy
              </Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'info.main' }}>
              {predictiveAnalytics.modelAccuracy.yesterday.toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Yesterday's ML performance
            </Typography>
          </CardContent>
        </Card>

        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Shield sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Threat Intel
              </Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main' }}>
              {threatIntelligence.length}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Active indicators
            </Typography>
          </CardContent>
        </Card>
      </Box>

      {/* Enhanced Tabs for Advanced Analytics */}
      <Card sx={{ mb: 3 }}>
        <Tabs
          value={activeTab}
          onChange={(_, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab icon={<TrendingUp />} label="Threat Trends" />
          <Tab icon={<PieChart />} label="Distribution" />
          <Tab icon={<Psychology />} label="AI Predictions" />
          <Tab icon={<Shield />} label="Threat Intelligence" />
          <Tab icon={<FindInPage />} label="Forensic Cases" />
          <Tab icon={<Search />} label="Threat Hunting" />
          <Tab icon={<SmartToy />} label="ML Insights" />
        </Tabs>
      </Card>

      {/* Tab Content */}
      {activeTab === 0 && (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
            gap: 3,
            mb: 3,
          }}
        >
          {/* Threat Trends Chart */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                📈 Threat Trends Over Time
              </Typography>
              {loading ? (
                <LinearProgress sx={{ mb: 2 }} />
              ) : null}
              <Box sx={{ height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart data={analyticsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="day" stroke="#b0bec5" />
                    <YAxis stroke="#b0bec5" />
                    <ChartTooltip
                      contentStyle={{
                        backgroundColor: '#1a1f2e',
                        border: '1px solid #00e676',
                        borderRadius: '8px',
                      }}
                    />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="total"
                      fill="#f44336"
                      fillOpacity={0.3}
                      stroke="#f44336"
                      strokeWidth={2}
                      name="Total Threats"
                    />
                    <Line
                      type="monotone"
                      dataKey="sqlInjection"
                      stroke="#ff9800"
                      strokeWidth={2}
                      name="SQL Injection"
                    />
                    <Line
                      type="monotone"
                      dataKey="xss"
                      stroke="#2196f3"
                      strokeWidth={2}
                      name="XSS"
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          {/* Severity Radar Chart */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🎯 Threat Severity Analysis
              </Typography>
              <Box sx={{ height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={severityRadarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="subject" />
                    <PolarRadiusAxis />
                    <Radar
                      name="This Month"
                      dataKey="A"
                      stroke="#f44336"
                      fill="#f44336"
                      fillOpacity={0.3}
                    />
                    <Radar
                      name="Last Month"
                      dataKey="B"
                      stroke="#2196f3"
                      fill="#2196f3"
                      fillOpacity={0.3}
                    />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {activeTab === 1 && (
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' },
            gap: 3,
            mb: 3,
          }}
        >
          {/* Threat Type Distribution */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🥧 Threat Type Distribution
              </Typography>
              <Box sx={{ height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RechartsPieChart>
                    <Pie
                      data={threatTypeDistribution}
                      cx="50%"
                      cy="50%"
                      outerRadius={120}
                      fill="#8884d8"
                      dataKey="value"
                      label={(entry: any) => `${entry.name} ${(entry.percent * 100).toFixed(0)}%`}
                    >
                      {threatTypeDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <ChartTooltip />
                  </RechartsPieChart>
                </ResponsiveContainer>
              </Box>
            </CardContent>
          </Card>

          {/* Threat Details Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                📊 Detailed Breakdown
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Threat Type</TableCell>
                      <TableCell align="right">Count</TableCell>
                      <TableCell>Severity</TableCell>
                      <TableCell align="right">%</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {threatTypeDistribution.map((threat) => {
                      const total = threatTypeDistribution.reduce((sum, t) => sum + t.value, 0);
                      const percentage = ((threat.value / total) * 100).toFixed(1);
                      
                      return (
                        <TableRow key={threat.name}>
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Box
                                sx={{
                                  width: 12,
                                  height: 12,
                                  backgroundColor: threat.color,
                                  borderRadius: '50%',
                                  mr: 1,
                                }}
                              />
                              {threat.name}
                            </Box>
                          </TableCell>
                          <TableCell align="right">{threat.value}</TableCell>
                          <TableCell>
                            <Chip
                              label={threat.severity}
                              size="small" 
                              color={
                                threat.severity === 'High' ? 'error' :
                                threat.severity === 'Medium' ? 'warning' : 'success'
                              }
                            />
                          </TableCell>
                          <TableCell align="right">{percentage}%</TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* AI Predictions Tab */}
      {activeTab === 2 && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', lg: '1fr 1fr' }, gap: 3, mb: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🔮 Next Week Threat Predictions
              </Typography>
              <Box sx={{ mb: 3 }}>
                {Object.entries(predictiveAnalytics.nextWeekPrediction).map(([key, value]) => {
                  if (key === 'total') return null;
                  return (
                    <Box key={key} sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                          {key.replace(/([A-Z])/g, ' $1')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {value.predicted} threats ({value.confidence}% confidence)
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={value.confidence}
                        sx={{
                          height: 6,
                          borderRadius: 1,
                          '& .MuiLinearProgress-bar': {
                            backgroundColor: value.trend === 'increasing' ? 'error.main' : 
                                           value.trend === 'decreasing' ? 'success.main' : 'warning.main'
                          }
                        }}
                      />
                    </Box>
                  );
                })}
              </Box>
              
              <Divider sx={{ my: 2 }} />
              
              <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                🎯 Model Accuracy Trends
              </Typography>
              <Box>
                <Typography variant="body2" color="text.secondary">
                  Last 30 Days: {predictiveAnalytics.modelAccuracy.last30Days}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Last 7 Days: {predictiveAnalytics.modelAccuracy.last7Days}%
                </Typography>
                <Typography variant="body2" color="success.main">
                  Yesterday: {predictiveAnalytics.modelAccuracy.yesterday}%
                </Typography>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                ⚠️ Risk Factor Analysis
              </Typography>
              {predictiveAnalytics.riskFactors.map((risk, index) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                      <Typography sx={{ fontWeight: 500, flexGrow: 1 }}>
                        {risk.factor}
                      </Typography>
                      <Chip 
                        label={risk.impact} 
                        color={getPriorityColor(risk.impact) as any}
                        size="small" 
                        sx={{ mr: 1 }}
                      />
                      <Typography variant="body2" color="text.secondary">
                        {risk.probability}%
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Typography variant="body2" color="text.secondary">
                      Probability: {risk.probability}% | Impact Level: {risk.impact}
                    </Typography>
                  </AccordionDetails>
                </Accordion>
              ))}
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Threat Intelligence Tab */}
      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              🛡️ Active Threat Intelligence Indicators
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Indicator</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Threat Level</TableCell>
                    <TableCell>Confidence</TableCell>
                    <TableCell>Last Seen</TableCell>
                    <TableCell>Tags</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {threatIntelligence.map((intel) => (
                    <TableRow key={intel.id} hover>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                          {intel.indicator}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip label={intel.type} variant="outlined" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={intel.threatLevel} 
                          color={getPriorityColor(intel.threatLevel) as any}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2">{intel.confidence}%</Typography>
                          <LinearProgress
                            variant="determinate"
                            value={intel.confidence}
                            sx={{ ml: 1, width: 50, height: 4 }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {intel.lastSeen}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {intel.tags.map((tag) => (
                            <Chip key={tag} label={tag} size="small" variant="outlined" />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <IconButton 
                          size="small" 
                          onClick={() => setSelectedIntelligence(intel)}
                        >
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

      {/* Forensic Cases Tab */}
      {activeTab === 4 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              🔍 Active Forensic Investigations
            </Typography>
            <Box sx={{ display: 'grid', gap: 2 }}>
              {forensicCases.map((caseItem) => (
                <Paper
                  key={caseItem.id}
                  sx={{
                    p: 2,
                    cursor: 'pointer',
                    '&:hover': { backgroundColor: 'rgba(0, 255, 136, 0.05)' }
                  }}
                  onClick={() => openForensicCase(caseItem)}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                      {caseItem.title}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip 
                        label={caseItem.status} 
                        color={getStatusColor(caseItem.status) as any}
                        size="small"
                      />
                      <Chip 
                        label={caseItem.priority} 
                        color={getPriorityColor(caseItem.priority) as any}
                        size="small"
                      />
                    </Box>
                  </Box>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {caseItem.findings}
                  </Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2" color="text.secondary">
                      Assignee: {caseItem.assignee} | {caseItem.indicators} indicators
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      {caseItem.lastUpdate}
                    </Typography>
                  </Box>
                </Paper>
              ))}
            </Box>
          </CardContent>
        </Card>
      )}

      {/* Threat Hunting Tab */}
      {activeTab === 5 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              🎯 Advanced Threat Hunting
            </Typography>
            <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
              <TextField
                fullWidth
                placeholder="Enter hunting query (e.g., process.name:powershell AND network.protocol:tcp)"
                value={huntingQuery}
                onChange={(e) => setHuntingQuery(e.target.value)}
                InputProps={{
                  startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
              <Button 
                variant="contained" 
                onClick={handleThreatHunting}
                startIcon={<Search />}
              >
                Hunt
              </Button>
            </Box>
            
            {huntingResults.length > 0 && (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600 }}>
                  🎯 Hunting Results ({huntingResults.length} found)
                </Typography>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Timestamp</TableCell>
                        <TableCell>Source</TableCell>
                        <TableCell>Event</TableCell>
                        <TableCell>Severity</TableCell>
                        <TableCell>Confidence</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {huntingResults.map((result) => (
                        <TableRow key={result.id}>
                          <TableCell>{result.timestamp}</TableCell>
                          <TableCell>{result.source}</TableCell>
                          <TableCell>{result.event}</TableCell>
                          <TableCell>
                            <Chip 
                              label={result.severity} 
                              color={getPriorityColor(result.severity) as any}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{result.confidence}%</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {/* ML Insights Tab */}
      {activeTab === 6 && (
        <Box sx={{ display: 'grid', gap: 3 }}>
          {mlInsights.map((insight, index) => (
            <Card key={index}>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <SmartToy sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {insight.title}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip label={insight.type} variant="outlined" size="small" />
                    <Chip 
                      label={`${insight.confidence}% Confidence`} 
                      color="info" 
                      size="small"
                    />
                    <Chip 
                      label={insight.impact} 
                      color={getPriorityColor(insight.impact) as any}
                      size="small"
                    />
                  </Box>
                </Box>
                <Typography variant="body1" sx={{ mb: 2 }}>
                  {insight.description}
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  <Typography variant="body2">
                    <strong>Recommendation:</strong> {insight.recommendation}
                  </Typography>
                </Alert>
                <Typography variant="body2" color="text.secondary">
                  Generated {insight.timestamp}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      )}

      {/* Forensic Case Detail Dialog */}
      <Dialog
        open={forensicDialogOpen}
        onClose={() => setForensicDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Typography variant="h6">
            🔍 Forensic Case Details: {selectedCase?.title}
          </Typography>
        </DialogTitle>
        <DialogContent>
          {selectedCase && (
            <Box>
              <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2, mb: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Case ID</Typography>
                  <Typography variant="body1">{selectedCase.id}</Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip 
                    label={selectedCase.status} 
                    color={getStatusColor(selectedCase.status) as any}
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Priority</Typography>
                  <Chip 
                    label={selectedCase.priority} 
                    color={getPriorityColor(selectedCase.priority) as any}
                    size="small"
                  />
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary">Assignee</Typography>
                  <Typography variant="body1">{selectedCase.assignee}</Typography>
                </Box>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" color="text.secondary">Findings</Typography>
              <Typography variant="body1" sx={{ mb: 2 }}>{selectedCase.findings}</Typography>
              <Typography variant="body2" color="text.secondary">
                Investigation Timeline: {selectedCase.timeline}
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setForensicDialogOpen(false)}>Close</Button>
          <Button variant="contained">View Full Report</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default Analytics; 