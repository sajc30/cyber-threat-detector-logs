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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Stepper,
  Step,
  StepLabel,
} from '@mui/material';
import {
  Visibility,
  Security,
  FindInPage,
  Storage,
  Computer,
  Memory,
  CloudDownload,
  Assessment,
  Fingerprint,
  Timeline,
  BugReport,
  Shield,
  CheckCircle,
  Schedule,
  Warning,
  Info,
  Add,
  Refresh,
  Download,
  Upload,
} from '@mui/icons-material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as ChartTooltip, ResponsiveContainer, LineChart, Line } from 'recharts';

// Types
interface ForensicCase {
  id: string;
  title: string;
  description: string;
  status: 'Open' | 'In Progress' | 'Analysis' | 'Report' | 'Closed';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  created_date: string;
  updated_date: string;
  investigator: string;
  evidence_count: number;
  findings: string[];
  timeline: string[];
  report_status: 'Pending' | 'Draft' | 'Review' | 'Final';
}

interface Evidence {
  id: string;
  case_id: string;
  name: string;
  type: 'Disk Image' | 'Memory Dump' | 'Network Capture' | 'File System' | 'Log Files' | 'Registry';
  size: string;
  hash: string;
  collected_date: string;
  source: string;
  chain_of_custody: string[];
  analysis_status: 'Pending' | 'In Progress' | 'Complete';
}

const DigitalForensics: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedCase, setSelectedCase] = useState<ForensicCase | null>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  // Mock data
  const [cases, setCases] = useState<ForensicCase[]>([
    {
      id: 'FOR-001',
      title: 'Advanced Persistent Threat Investigation',
      description: 'Deep forensic analysis of compromised domain controller and lateral movement patterns',
      status: 'In Progress',
      priority: 'Critical',
      created_date: '2024-01-18 10:00:00',
      updated_date: '2024-01-20 14:30:00',
      investigator: 'Dr. Sarah Chen',
      evidence_count: 8,
      findings: [
        'PowerShell execution artifacts found',
        'Lateral movement via WMI detected',
        'Data staging in temp directories',
        'Encrypted communication channels identified'
      ],
      timeline: ['Initial compromise detected', 'Domain admin compromise', 'Data exfiltration attempt'],
      report_status: 'Draft'
    },
    {
      id: 'FOR-002',
      title: 'Insider Threat Data Exfiltration',
      description: 'Investigation of suspicious employee data access and potential intellectual property theft',
      status: 'Analysis',
      priority: 'High',
      created_date: '2024-01-19 09:15:00',
      updated_date: '2024-01-20 11:20:00',
      investigator: 'Mike Rodriguez',
      evidence_count: 5,
      findings: [
        'Unusual file access patterns after hours',
        'Large file downloads to personal devices',
        'Use of unauthorized cloud storage',
        'Deletion of browser history and logs'
      ],
      timeline: ['Access anomaly detected', 'File activity analysis', 'User behavior investigation'],
      report_status: 'Pending'
    },
    {
      id: 'FOR-003',
      title: 'Ransomware Impact Assessment',
      description: 'Complete forensic analysis of ransomware attack vector and encrypted file recovery',
      status: 'Closed',
      priority: 'Critical',
      created_date: '2024-01-15 08:30:00',
      updated_date: '2024-01-19 16:45:00',
      investigator: 'Alex Kim',
      evidence_count: 12,
      findings: [
        'Email-based initial infection vector',
        'Macro-enabled document execution',
        'Network propagation via SMB shares',
        'Encryption algorithm identified as AES-256'
      ],
      timeline: ['Infection detected', 'Containment measures', 'Recovery operations', 'Lessons learned'],
      report_status: 'Final'
    }
  ]);

  const [evidence, setEvidence] = useState<Evidence[]>([
    {
      id: 'EVD-001',
      case_id: 'FOR-001',
      name: 'DC-01_Full_Disk_Image.dd',
      type: 'Disk Image',
      size: '500 GB',
      hash: 'sha256:a1b2c3d4e5f6...',
      collected_date: '2024-01-18 12:00:00',
      source: 'Domain Controller DC-01',
      chain_of_custody: ['Initial Collection: John Doe', 'Transfer: Jane Smith', 'Analysis: Sarah Chen'],
      analysis_status: 'In Progress'
    },
    {
      id: 'EVD-002',
      case_id: 'FOR-001',
      name: 'Memory_Dump_DC01.mem',
      type: 'Memory Dump',
      size: '16 GB',
      hash: 'sha256:b2c3d4e5f6g7...',
      collected_date: '2024-01-18 12:15:00',
      source: 'Domain Controller DC-01',
      chain_of_custody: ['Initial Collection: John Doe', 'Analysis: Sarah Chen'],
      analysis_status: 'Complete'
    },
    {
      id: 'EVD-003',
      case_id: 'FOR-002',
      name: 'Employee_Workstation.img',
      type: 'Disk Image',
      size: '256 GB',
      hash: 'sha256:c3d4e5f6g7h8...',
      collected_date: '2024-01-19 14:30:00',
      source: 'Employee Workstation WS-045',
      chain_of_custody: ['Initial Collection: Mike Rodriguez', 'Analysis: Mike Rodriguez'],
      analysis_status: 'In Progress'
    }
  ]);

  const forensicStats = {
    totalCases: cases.length,
    activeCases: cases.filter(c => c.status !== 'Closed').length,
    evidenceItems: evidence.length,
    analysisComplete: evidence.filter(e => e.analysis_status === 'Complete').length
  };

  const analysisData = [
    { tool: 'Autopsy', cases: 15, status: 'Active' },
    { tool: 'Volatility', cases: 8, status: 'Active' },
    { tool: 'Sleuth Kit', cases: 12, status: 'Active' },
    { tool: 'YARA', cases: 6, status: 'Active' }
  ];

  const getSeverityColor = (priority: string) => {
    switch (priority) {
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
      case 'Analysis': return 'info';
      case 'Report': return 'primary';
      case 'Closed': return 'success';
      default: return 'default';
    }
  };

  const getEvidenceIcon = (type: string) => {
    switch (type) {
      case 'Disk Image': return <Storage />;
      case 'Memory Dump': return <Memory />;
      case 'Network Capture': return <CloudDownload />;
      case 'File System': return <Computer />;
      case 'Log Files': return <Assessment />;
      case 'Registry': return <Fingerprint />;
      default: return <FindInPage />;
    }
  };

  const handleCaseClick = (forensicCase: ForensicCase) => {
    setSelectedCase(forensicCase);
    setDetailsDialogOpen(true);
  };

  const filteredCases = cases.filter(c => {
    const matchesStatus = filterStatus === 'All' || c.status === filterStatus;
    const matchesSearch = searchTerm === '' || 
      c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.description.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesStatus && matchesSearch;
  });

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 1, display: 'flex', alignItems: 'center' }}>
            <Visibility sx={{ mr: 2, color: 'info.main' }} />
            Digital Forensics
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Advanced digital investigation and evidence analysis
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button variant="contained" startIcon={<Add />}>
            New Case
          </Button>
          <Button variant="outlined" startIcon={<Refresh />}>
            Refresh
          </Button>
        </Box>
      </Box>

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
              <BugReport sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Total Cases</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'primary.main' }}>
              {forensicStats.totalCases}
            </Typography>
            <Typography variant="body2" color="text.secondary">Active investigations</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Schedule sx={{ mr: 1, color: 'warning.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Active</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'warning.main' }}>
              {forensicStats.activeCases}
            </Typography>
            <Typography variant="body2" color="text.secondary">In progress</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <Storage sx={{ mr: 1, color: 'info.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Evidence</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'info.main' }}>
              {forensicStats.evidenceItems}
            </Typography>
            <Typography variant="body2" color="text.secondary">Collected items</Typography>
          </CardContent>
        </Card>
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircle sx={{ mr: 1, color: 'success.main' }} />
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Analyzed</Typography>
            </Box>
            <Typography variant="h3" sx={{ fontWeight: 700, color: 'success.main' }}>
              {forensicStats.analysisComplete}
            </Typography>
            <Typography variant="body2" color="text.secondary">Complete analysis</Typography>
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
          <Tab icon={<BugReport />} label="Active Cases" />
          <Tab icon={<Storage />} label="Evidence" />
          <Tab icon={<Assessment />} label="Analysis Tools" />
        </Tabs>
      </Card>

      {/* Active Cases Tab */}
      {activeTab === 0 && (
        <Card>
          <CardContent>
            {/* Filters */}
            <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
              <TextField
                placeholder="Search cases..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                sx={{ minWidth: 200 }}
              />
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
                  <MenuItem value="Analysis">Analysis</MenuItem>
                  <MenuItem value="Report">Report</MenuItem>
                  <MenuItem value="Closed">Closed</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {/* Cases Table */}
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Case ID</TableCell>
                    <TableCell>Title</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Investigator</TableCell>
                    <TableCell>Evidence</TableCell>
                    <TableCell>Created</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {filteredCases.map((case_item) => (
                    <TableRow 
                      key={case_item.id} 
                      hover 
                      sx={{ cursor: 'pointer' }}
                      onClick={() => handleCaseClick(case_item)}
                    >
                      <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                        {case_item.id}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {case_item.title}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {case_item.description.substring(0, 50)}...
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={case_item.status}
                          color={getStatusColor(case_item.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={case_item.priority}
                          color={getSeverityColor(case_item.priority)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>{case_item.investigator}</TableCell>
                      <TableCell>
                        <Chip
                          label={`${case_item.evidence_count} items`}
                          variant="outlined"
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace' }}>
                        {case_item.created_date.split(' ')[0]}
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
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

      {/* Evidence Tab */}
      {activeTab === 1 && (
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
              🗃️ Evidence Collection
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Evidence ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Size</TableCell>
                    <TableCell>Case</TableCell>
                    <TableCell>Analysis</TableCell>
                    <TableCell>Collected</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {evidence.map((item) => (
                    <TableRow key={item.id} hover>
                      <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>
                        {item.id}
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          {getEvidenceIcon(item.type)}
                          <Typography variant="body2" sx={{ ml: 1 }}>
                            {item.name}
                          </Typography>
                        </Box>
                      </TableCell>
                      <TableCell>{item.type}</TableCell>
                      <TableCell>{item.size}</TableCell>
                      <TableCell>
                        <Chip label={item.case_id} variant="outlined" size="small" />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={item.analysis_status}
                          color={item.analysis_status === 'Complete' ? 'success' : 'warning'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace' }}>
                        {item.collected_date.split(' ')[0]}
                      </TableCell>
                      <TableCell>
                        <IconButton size="small">
                          <Download />
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

      {/* Analysis Tools Tab */}
      {activeTab === 2 && (
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                🔧 Analysis Tools Status
              </Typography>
              <List>
                {analysisData.map((tool) => (
                  <ListItem key={tool.tool}>
                    <ListItemIcon>
                      <Assessment color="primary" />
                    </ListItemIcon>
                    <ListItemText
                      primary={tool.tool}
                      secondary={`${tool.cases} active analyses`}
                    />
                    <Chip
                      label={tool.status}
                      color="success"
                      size="small"
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                📊 Case Progress
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {['Evidence Collection', 'Initial Analysis', 'Deep Investigation', 'Report Generation'].map((stage, index) => (
                  <Box key={stage}>
                    <Typography variant="body2" sx={{ mb: 1 }}>
                      {stage}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={(4 - index) * 25}
                      sx={{ height: 8, borderRadius: 1 }}
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}

      {/* Case Details Dialog */}
      <Dialog
        open={detailsDialogOpen}
        onClose={() => setDetailsDialogOpen(false)}
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Case Details: {selectedCase?.id}</Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label={selectedCase?.status}
                color={getStatusColor(selectedCase?.status || '')}
                size="small"
              />
              <Chip
                label={selectedCase?.priority}
                color={getSeverityColor(selectedCase?.priority || '')}
                size="small"
              />
            </Box>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedCase && (
            <Box sx={{ display: 'grid', gap: 3 }}>
              <Alert severity="info">
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  {selectedCase.title}
                </Typography>
                <Typography variant="body1">
                  {selectedCase.description}
                </Typography>
              </Alert>

              <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    📋 Case Information
                  </Typography>
                  <Typography variant="body2"><strong>Investigator:</strong> {selectedCase.investigator}</Typography>
                  <Typography variant="body2"><strong>Created:</strong> {selectedCase.created_date}</Typography>
                  <Typography variant="body2"><strong>Updated:</strong> {selectedCase.updated_date}</Typography>
                  <Typography variant="body2"><strong>Evidence Count:</strong> {selectedCase.evidence_count} items</Typography>
                  <Typography variant="body2"><strong>Report Status:</strong> {selectedCase.report_status}</Typography>
                </Box>

                <Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                    🔍 Key Findings
                  </Typography>
                  <List dense>
                    {selectedCase.findings.map((finding, index) => (
                      <ListItem key={index}>
                        <ListItemIcon>
                          <Shield color="warning" />
                        </ListItemIcon>
                        <ListItemText primary={finding} />
                      </ListItem>
                    ))}
                  </List>
                </Box>
              </Box>

              <Box>
                <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 2 }}>
                  ⏰ Investigation Timeline
                </Typography>
                <Stepper orientation="vertical">
                  {selectedCase.timeline.map((step, index) => (
                    <Step key={index} active>
                      <StepLabel>{step}</StepLabel>
                    </Step>
                  ))}
                </Stepper>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Close</Button>
          <Button variant="contained" color="primary">
            Generate Report
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DigitalForensics; 