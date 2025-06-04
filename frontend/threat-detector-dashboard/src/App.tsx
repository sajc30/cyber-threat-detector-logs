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
// Security Center Pages
import ActiveThreats from './pages/ActiveThreats';
import SecurityIncidents from './pages/SecurityIncidents';
import DigitalForensics from './pages/DigitalForensics';

// Services
import websocketService, { ConnectionStatus } from './services/websocketService';
import { getDemoStatus } from './services/api';

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
  const demoStatus = getDemoStatus();
  
  const getStatusColor = () => {
    if (demoStatus.isDemoMode) return 'info';
    switch (status.status) {
      case 'connected': return 'success';
      case 'connecting': return 'warning';
      case 'disconnected': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getStatusIcon = () => {
    if (demoStatus.isDemoMode) return '🎭';
    switch (status.status) {
      case 'connected': return '🟢';
      case 'connecting': return '🟡';
      case 'disconnected': return '⚪';
      case 'error': return '🔴';
      default: return '⚪';
    }
  };

  const getStatusText = () => {
    if (demoStatus.isDemoMode) return 'DEMO MODE';
    return `API: ${status.status.toUpperCase()}`;
  };

  const getStatusMessage = () => {
    if (demoStatus.isDemoMode) {
      return 'Running with mock data for demonstration';
    }
    return status.message;
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
        label={getStatusText()}
        color={getStatusColor()}
        variant="filled"
        size="small"
        sx={{ 
          fontFamily: 'monospace',
          fontWeight: 'bold',
          backdropFilter: 'blur(10px)',
          backgroundColor: demoStatus.isDemoMode ? '#2196f320' : 
                          status.status === 'connected' ? '#00ff8820' : undefined
        }}
      />
      {getStatusMessage() && (
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
          {getStatusMessage()}
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
    const demoStatus = getDemoStatus();
    console.log('🚀 Initializing CyberGuard AI Dashboard...');
    console.log('🎭 Demo Status:', demoStatus);
    
    if (demoStatus.isDemoMode) {
      // Demo mode - set status accordingly
      setConnectionStatus({ 
        status: 'connected', 
        message: 'Demo mode active - using mock data' 
      });
      console.log('🎭 Demo Mode: Application initialized with mock data');
    } else {
      // Regular mode - keep WebSocket disabled for now as discussed
      setConnectionStatus({ 
        status: 'connected', 
        message: 'API Connected (WebSocket disabled)' 
      });
      console.log('⚙️ Regular Mode: Application initialized with API-only mode');
    }

    // Cleanup on unmount
    return () => {
      console.log('🧹 App cleanup...');
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
              <Route path="/active-threats" element={<ActiveThreats />} />
              <Route path="/security-incidents" element={<SecurityIncidents />} />
              <Route path="/digital-forensics" element={<DigitalForensics />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;
