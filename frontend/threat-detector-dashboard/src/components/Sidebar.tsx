import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  Typography,
  Chip,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Timeline as MonitoringIcon,
  Analytics as AnalyticsIcon,
  Settings as SettingsIcon,
  Security,
  Visibility,
  Warning,
  BugReport,
} from '@mui/icons-material';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface MenuItem {
  id: string;
  text: string;
  icon: React.ReactNode;
  path: string;
  badge?: {
    text: string;
    color: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  };
}

const Sidebar: React.FC<SidebarProps> = ({ open, onClose }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems: MenuItem[] = [
    {
      id: 'dashboard',
      text: 'Dashboard',
      icon: <DashboardIcon />,
      path: '/',
    },
    {
      id: 'monitoring',
      text: 'Real-Time Monitoring',
      icon: <MonitoringIcon />,
      path: '/monitoring',
      badge: {
        text: 'LIVE',
        color: 'success',
      },
    },
    {
      id: 'analytics',
      text: 'Analytics',
      icon: <AnalyticsIcon />,
      path: '/analytics',
    },
    {
      id: 'settings',
      text: 'Settings',
      icon: <SettingsIcon />,
      path: '/settings',
    },
  ];

  const securityItems: MenuItem[] = [
    {
      id: 'threats',
      text: 'Active Threats',
      icon: <Warning />,
      path: '/active-threats',
      badge: {
        text: '3',
        color: 'error',
      },
    },
    {
      id: 'incidents',
      text: 'Security Incidents',
      icon: <BugReport />,
      path: '/security-incidents',
    },
    {
      id: 'forensics',
      text: 'Digital Forensics',
      icon: <Visibility />,
      path: '/digital-forensics',
    },
  ];

  const handleItemClick = (path: string) => {
    navigate(path);
    onClose();
  };

  const renderMenuItem = (item: MenuItem) => {
    const isActive = location.pathname === item.path;

    return (
      <ListItem key={item.id} disablePadding>
        <ListItemButton
          onClick={() => handleItemClick(item.path)}
          sx={{
            borderRadius: 2,
            mx: 1,
            mb: 0.5,
            backgroundColor: isActive ? 'primary.main' : 'transparent',
            color: isActive ? 'primary.contrastText' : 'text.primary',
            '&:hover': {
              backgroundColor: isActive ? 'primary.dark' : 'action.hover',
            },
            transition: 'all 0.2s ease-in-out',
          }}
        >
          <ListItemIcon
            sx={{
              color: isActive ? 'primary.contrastText' : 'text.secondary',
              minWidth: 40,
            }}
          >
            {item.icon}
          </ListItemIcon>
          <ListItemText
            primary={item.text}
            sx={{
              '& .MuiListItemText-primary': {
                fontSize: '0.875rem',
                fontWeight: isActive ? 600 : 500,
              },
            }}
          />
          {item.badge && (
            <Chip
              label={item.badge.text}
              color={item.badge.color}
              size="small"
              sx={{
                height: 20,
                fontSize: '0.75rem',
                fontWeight: 600,
              }}
            />
          )}
        </ListItemButton>
      </ListItem>
    );
  };

  const drawerContent = (
    <Box sx={{ width: 280, pt: 2 }}>
      {/* Navigation Section */}
      <Box sx={{ px: 2, pb: 1 }}>
        <Typography
          variant="overline"
          sx={{
            color: 'text.secondary',
            fontWeight: 600,
            letterSpacing: 1,
          }}
        >
          Navigation
        </Typography>
      </Box>
      <List>
        {menuItems.map(renderMenuItem)}
      </List>

      <Divider sx={{ my: 2, mx: 2 }} />

      {/* Security Section */}
      <Box sx={{ px: 2, pb: 1 }}>
        <Typography
          variant="overline"
          sx={{
            color: 'text.secondary',
            fontWeight: 600,
            letterSpacing: 1,
          }}
        >
          Security Center
        </Typography>
      </Box>
      <List>
        {securityItems.map(renderMenuItem)}
      </List>

      <Divider sx={{ my: 2, mx: 2 }} />

      {/* System Info */}
      <Box sx={{ px: 2 }}>
        <Box
          sx={{
            p: 2,
            backgroundColor: 'background.paper',
            borderRadius: 2,
            border: '1px solid',
            borderColor: 'divider',
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <Security sx={{ color: 'success.main', mr: 1, fontSize: 16 }} />
            <Typography variant="caption" color="success.main" fontWeight={600}>
              SYSTEM SECURED
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
            AI Model: Active<br />
            Last Scan: 2 min ago<br />
            Threats Blocked: 127
          </Typography>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Drawer
      anchor="left"
      open={open}
      onClose={onClose}
      variant="temporary"
      sx={{
        '& .MuiDrawer-paper': {
          backgroundColor: 'background.default',
          borderRight: '1px solid rgba(0, 230, 118, 0.12)',
          backgroundImage: 'linear-gradient(rgba(0, 230, 118, 0.02), rgba(0, 230, 118, 0.02))',
        },
      }}
    >
      {drawerContent}
    </Drawer>
  );
};

export default Sidebar; 