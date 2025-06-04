import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Toaster } from 'react-hot-toast';
import { Box, Chip, Typography } from '@mui/material';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import RealTimeMonitoring from './pages/RealTimeMonitoring';
import Analytics from './pages/Analytics';
import Settings from './pages/Settings';

// Services
import websocketService, { ConnectionStatus } from './services/websocketService';

// Dark cybersecurity theme
const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#00ff88',
      dark: '#00cc6a',
      light: '#33ff99'
    },
    secondary: {
      main: '#ff4444',
      dark: '#cc3333',
      light: '#ff6666'
    },
    background: {
      default: '#0a0a0a',
      paper: '#1a1a1a'
    },
    text: {
      primary: '#ffffff',
      secondary: '#cccccc'
    }
  },
  typography: {
    fontFamily: '"Roboto Mono", "Courier New", monospace',
    h4: {
      fontWeight: 700,
      color: '#00ff88'
    },
    h6: {
      fontWeight: 600,
      color: '#00ff88'
    }
  },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'linear-gradient(145deg, #1a1a1a 0%, #2d2d2d 100%)',
          border: '1px solid #333',
        }
      }
    },
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 600
        }
      }
    }
  }
});

// Connection status indicator component
const ConnectionIndicator: React.FC<{ status: ConnectionStatus }> = ({ status }) => {
  const getStatusColor = () => {
    switch (status.status) {
      case 'connected': return 'success';
      case 'connecting': return 'warning';
      case 'disconnected': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = () => {
    switch (status.status) {
      case 'connected': return '🟢';
      case 'connecting': return '🟡';
      case 'disconnected': return '⚪';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <Box sx={{ 
      position: 'fixed', 
      bottom: 16, 
      right: 16, 
      zIndex: 1200,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-end',
      gap: 1
    }}>
      <Chip
        icon={<span>{getStatusIcon()}</span>}
        label={`API: ${status.status.toUpperCase()}`}
        color={getStatusColor()}
        variant="filled"
        size="small"
        sx={{ 
          fontFamily: 'monospace',
          fontWeight: 'bold',
          backdropFilter: 'blur(10px)',
          backgroundColor: status.status === 'connected' ? '#00ff8820' : undefined
        }}
      />
      {status.message && (
        <Typography 
          variant="caption" 
          sx={{ 
            color: 'text.secondary',
            fontFamily: 'monospace',
            backgroundColor: 'rgba(0,0,0,0.7)',
            padding: '2px 8px',
            borderRadius: 1,
            backdropFilter: 'blur(10px)',
            maxWidth: '200px',
            textAlign: 'right'
          }}
        >
          {status.message}
        </Typography>
      )}
    </Box>
  );
};

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({ 
    status: 'disconnected' 
  });

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  useEffect(() => {
    console.log('🚀 Initializing CyberGuard AI Dashboard...');
    
    // Temporarily disabled WebSocket for basic functionality
    // TODO: Re-enable when implementing WebSocket integration
    /*
    // Set up WebSocket callbacks
    websocketService.setCallbacks({
      onConnectionStatusChange: (status: ConnectionStatus) => {
        console.log('📡 Connection status changed:', status);
        setConnectionStatus(status);
      },
      onThreatAlert: (alert) => {
        console.log('🚨 Threat alert in App:', alert);
      },
      onPriorityAlert: (alert) => {
        console.log('🚨🚨 Priority alert in App:', alert);
      },
      onSystemMetricsUpdate: (metrics) => {
        console.log('📊 System metrics updated:', metrics);
      },
      onActiveUsersUpdate: (users, count) => {
        console.log('👥 Active users updated:', users, count);
      },
      onError: (error) => {
        console.error('❌ WebSocket error in App:', error);
      }
    });

    // Connect to WebSocket
    const connectWebSocket = async () => {
      try {
        console.log('🔌 Connecting to real-time service...');
        await websocketService.connect('CyberAdmin');
        console.log('✅ Real-time connection established successfully');
      } catch (error) {
        console.error('❌ Failed to connect to real-time service:', error);
      }
    };

    connectWebSocket();
    */

    // Set initial status as connected for API-only mode
    setConnectionStatus({ 
      status: 'connected', 
      message: 'API Connected (WebSocket disabled)' 
    });

    // Cleanup on unmount
    return () => {
      console.log('🧹 App cleanup...');
      // websocketService.disconnect(); // Disabled
    };
  }, []);

  return (
    <ThemeProvider theme={darkTheme}>
      <CssBaseline />
      <Router>
        {/* Real-time notification toaster */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#1a1a1a',
              color: '#fff',
              border: '1px solid #333',
              borderRadius: '8px',
              fontFamily: '"Roboto Mono", monospace',
              fontSize: '14px'
            },
            success: {
              iconTheme: {
                primary: '#00ff88',
                secondary: '#000'
              },
              style: {
                border: '1px solid #00ff88'
              }
            },
            error: {
              iconTheme: {
                primary: '#ff4444',
                secondary: '#000'
              },
              style: {
                border: '1px solid #ff4444'
              }
            }
          }}
        />
        
        {/* Connection status indicator */}
        <ConnectionIndicator status={connectionStatus} />
        
        {/* Main application layout */}
        <Box sx={{ display: 'flex', minHeight: '100vh' }}>
          {/* Navigation Bar */}
          <Navbar onMenuClick={toggleSidebar} />
          
          {/* Sidebar */}
          <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
          
          {/* Main Content */}
          <Box
            component="main"
            sx={{
              flexGrow: 1,
              p: 3,
              mt: 8, // Account for navbar height
              ml: sidebarOpen ? 0 : 0, // Sidebar handled by MUI Drawer
              transition: 'margin-left 0.3s ease-in-out',
            }}
          >
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/monitoring" element={<RealTimeMonitoring />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
