import React, { useState, useEffect } from 'react';
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  Chip,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Avatar,
} from '@mui/material';
import {
  Security,
  Warning,
  TrendingUp,
  Computer,
  Speed,
  Shield,
  BugReport,
  Visibility,
  NetworkCheck,
  Refresh,
  MoreVert,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Area,
  AreaChart,
} from 'recharts';

// Mock data for demonstration
const threatTimelineData = [
  { time: '00:00', threats: 2, normal: 45 },
  { time: '04:00', threats: 1, normal: 38 },
  { time: '08:00', threats: 5, normal: 52 },
  { time: '12:00', threats: 8, normal: 48 },
  { time: '16:00', threats: 3, normal: 55 },
  { time: '20:00', threats: 6, normal: 42 },
];

const threatTypesData = [
  { name: 'Malware', value: 35, color: '#f44336' },
  { name: 'Phishing', value: 25, color: '#ff9800' },
  { name: 'DDoS', value: 20, color: '#ff5722' },
  { name: 'SQL Injection', value: 15, color: '#e91e63' },
  { name: 'Other', value: 5, color: '#9c27b0' },
];

const systemMetricsData = [
  { metric: 'CPU', value: 45 },
  { metric: 'Memory', value: 67 },
  { metric: 'Network', value: 23 },
  { metric: 'Disk I/O', value: 34 },
];

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color: 'primary' | 'success' | 'warning' | 'error';
  trend?: {
    value: number;
    direction: 'up' | 'down';
  };
}

const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  color,
  trend,
}) => {
  return (
    <Card
      sx={{
        height: '100%',
        transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: (theme) => theme.shadows[8],
        },
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="text.secondary" gutterBottom variant="overline">
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ mb: 1, fontWeight: 600 }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Avatar
            sx={{
              bgcolor: `${color}.main`,
              width: 48,
              height: 48,
            }}
          >
            {icon}
          </Avatar>
        </Box>
        {trend && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
            <TrendingUp
              sx={{
                color: trend.direction === 'up' ? 'success.main' : 'error.main',
                mr: 1,
                fontSize: 16,
                transform: trend.direction === 'down' ? 'rotate(180deg)' : 'none',
              }}
            />
            <Typography
              variant="caption"
              sx={{
                color: trend.direction === 'up' ? 'success.main' : 'error.main',
                fontWeight: 600,
              }}
            >
              {trend.value}% vs last hour
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

const Dashboard: React.FC = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [systemStatus, setSystemStatus] = useState('operational');

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const recentThreats = [
    {
      id: 1,
      type: 'SQL Injection',
      severity: 'High',
      source: '192.168.1.45',
      time: '2 min ago',
      status: 'blocked',
    },
    {
      id: 2,
      type: 'Malware Detection',
      severity: 'Critical',
      source: 'email-server-01',
      time: '5 min ago',
      status: 'quarantined',
    },
    {
      id: 3,
      type: 'Unauthorized Access',
      severity: 'Medium',
      source: '10.0.0.23',
      time: '12 min ago',
      status: 'investigating',
    },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
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

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ mb: 1, fontWeight: 600 }}>
          Security Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          {currentTime.toLocaleString()} • System Status: {systemStatus.toUpperCase()}
        </Typography>
      </Box>

      {/* Alert Banner */}
      <Alert
        severity="info"
        sx={{ mb: 3 }}
        action={
          <IconButton color="inherit" size="small">
            <Refresh />
          </IconButton>
        }
      >
        AI Threat Detection Model is active and monitoring 1,247 endpoints in real-time.
      </Alert>

      {/* Metrics Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: '1fr 1fr 1fr 1fr' },
          gap: 3,
          mb: 3,
        }}
      >
        <MetricCard
          title="Threats Detected"
          value="23"
          subtitle="Last 24 hours"
          icon={<Warning />}
          color="error"
          trend={{ value: 15, direction: 'down' }}
        />
        <MetricCard
          title="Systems Protected"
          value="1,247"
          subtitle="Active endpoints"
          icon={<Shield />}
          color="success"
          trend={{ value: 3, direction: 'up' }}
        />
        <MetricCard
          title="Detection Rate"
          value="99.7%"
          subtitle="Accuracy score"
          icon={<TrendingUp />}
          color="primary"
          trend={{ value: 0.2, direction: 'up' }}
        />
        <MetricCard
          title="Response Time"
          value="2.3s"
          subtitle="Average detection"
          icon={<Speed />}
          color="warning"
          trend={{ value: 12, direction: 'down' }}
        />
      </Box>

      {/* Charts Section */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
          gap: 3,
          mb: 3,
        }}
      >
        {/* Threat Timeline */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Threat Detection Timeline
              </Typography>
              <IconButton size="small">
                <MoreVert />
              </IconButton>
            </Box>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={threatTimelineData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#rgba(255,255,255,0.1)" />
                  <XAxis dataKey="time" stroke="#b0bec5" />
                  <YAxis stroke="#b0bec5" />
                  <ChartTooltip
                    contentStyle={{
                      backgroundColor: '#1a1f2e',
                      border: '1px solid #00e676',
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="normal"
                    stackId="1"
                    stroke="#4caf50"
                    fill="#4caf50"
                    fillOpacity={0.3}
                  />
                  <Area
                    type="monotone"
                    dataKey="threats"
                    stackId="1"
                    stroke="#f44336"
                    fill="#f44336"
                    fillOpacity={0.7}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>

        {/* Threat Types Distribution */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 2 }}>
              Threat Types
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={threatTypesData}
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {threatTypesData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <ChartTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Box>

      {/* Bottom Section */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
          gap: 3,
        }}
      >
        {/* Recent Threats */}
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Recent Threats
              </Typography>
              <Chip label="Real-time" color="success" size="small" />
            </Box>
            <List>
              {recentThreats.map((threat) => (
                <ListItem
                  key={threat.id}
                  sx={{
                    borderRadius: 1,
                    mb: 1,
                    backgroundColor: 'background.paper',
                    border: '1px solid',
                    borderColor: 'divider',
                  }}
                  secondaryAction={
                    <Chip
                      label={threat.status.toUpperCase()}
                      color={threat.status === 'blocked' ? 'success' : 'warning'}
                      size="small"
                    />
                  }
                >
                  <ListItemIcon>
                    <BugReport color="error" />
                  </ListItemIcon>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="body1" sx={{ fontWeight: 500 }}>
                          {threat.type}
                        </Typography>
                        <Chip
                          label={threat.severity}
                          color={getSeverityColor(threat.severity) as any}
                          size="small"
                        />
                      </Box>
                    }
                    secondary={
                      <Typography variant="body2" color="text.secondary">
                        Source: {threat.source} • {threat.time}
                      </Typography>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>

        {/* System Metrics */}
        <Card>
          <CardContent>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              System Performance
            </Typography>
            {systemMetricsData.map((metric) => (
              <Box key={metric.metric} sx={{ mb: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">{metric.metric}</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {metric.value}%
                  </Typography>
                </Box>
                <LinearProgress
                  variant="determinate"
                  value={metric.value}
                  sx={{
                    height: 8,
                    borderRadius: 1,
                    backgroundColor: 'grey.800',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor:
                        metric.value > 80
                          ? 'error.main'
                          : metric.value > 60
                          ? 'warning.main'
                          : 'success.main',
                    },
                  }}
                />
              </Box>
            ))}
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};

export default Dashboard; 