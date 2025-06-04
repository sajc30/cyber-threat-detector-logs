import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Badge,
  Box,
  Chip,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Shield as ShieldIcon,
  NotificationsActive,
  Security,
  Warning,
} from '@mui/icons-material';

interface NavbarProps {
  onMenuClick: () => void;
}

const Navbar: React.FC<NavbarProps> = ({ onMenuClick }) => {
  const [threatCount] = React.useState(3); // Mock threat count
  const [systemStatus] = React.useState('operational'); // operational, warning, critical

  const getStatusColor = () => {
    switch (systemStatus) {
      case 'operational':
        return 'success';
      case 'warning':
        return 'warning';
      case 'critical':
        return 'error';
      default:
        return 'default';
    }
  };

  const getStatusIcon = () => {
    switch (systemStatus) {
      case 'operational':
        return <Security />;
      case 'warning':
        return <Warning />;
      case 'critical':
        return <Warning />;
      default:
        return <Security />;
    }
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        zIndex: (theme) => theme.zIndex.drawer + 1,
        background: 'linear-gradient(135deg, #1a1f2e 0%, #2d3748 100%)',
        borderBottom: '1px solid rgba(0, 230, 118, 0.2)',
      }}
    >
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Left side - Menu and Brand */}
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            onClick={onMenuClick}
            edge="start"
            sx={{ mr: 2 }}
          >
            <MenuIcon />
          </IconButton>
          
          <ShieldIcon sx={{ mr: 1, color: 'primary.main' }} />
          <Typography
            variant="h6"
            noWrap
            component="div"
            sx={{
              fontWeight: 600,
              background: 'linear-gradient(45deg, #00e676, #4caf50)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            CyberGuard AI
          </Typography>
          
          <Typography
            variant="body2"
            sx={{ 
              ml: 2, 
              color: 'text.secondary',
              display: { xs: 'none', md: 'block' }
            }}
          >
            Threat Detection System
          </Typography>
        </Box>

        {/* Right side - Status and Notifications */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* System Status */}
          <Tooltip title={`System Status: ${systemStatus.toUpperCase()}`}>
            <Chip
              icon={getStatusIcon()}
              label={systemStatus.toUpperCase()}
              color={getStatusColor() as any}
              variant="outlined"
              size="small"
              sx={{
                display: { xs: 'none', sm: 'flex' },
                fontWeight: 600,
                textTransform: 'uppercase',
              }}
            />
          </Tooltip>

          {/* Threat Notifications */}
          <Tooltip title={`${threatCount} active threats detected`}>
            <IconButton color="inherit">
              <Badge badgeContent={threatCount} color="error">
                <NotificationsActive />
              </Badge>
            </IconButton>
          </Tooltip>

          {/* Real-time indicator */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: 'primary.main',
                animation: 'pulse 2s infinite',
                '@keyframes pulse': {
                  '0%': {
                    opacity: 1,
                  },
                  '50%': {
                    opacity: 0.5,
                  },
                  '100%': {
                    opacity: 1,
                  },
                },
              }}
            />
            <Typography
              variant="caption"
              sx={{ 
                color: 'primary.main',
                fontWeight: 500,
                display: { xs: 'none', md: 'block' }
              }}
            >
              LIVE
            </Typography>
          </Box>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar; 