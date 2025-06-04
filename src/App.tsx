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
import { getDemoStatus } from './services/api';

const theme = createTheme();

const App: React.FC = () => {
  const [demoStatus, setDemoStatus] = useState<boolean>(false);

  useEffect(() => {
    const fetchDemoStatus = async () => {
      const status = await getDemoStatus();
      setDemoStatus(status);
    };

    fetchDemoStatus();
  }, []);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Toaster />
        <Navbar />
        <Sidebar />
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/real-time-monitoring" element={<RealTimeMonitoring />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/active-threats" element={<ActiveThreats />} />
          <Route path="/security-incidents" element={<SecurityIncidents />} />
          <Route path="/digital-forensics" element={<DigitalForensics />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
};

export default App; 