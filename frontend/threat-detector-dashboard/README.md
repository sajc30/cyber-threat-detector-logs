# 🔒 CyberGuard AI - Threat Detection Dashboard

A modern, real-time cybersecurity threat detection dashboard built with React, TypeScript, and Material-UI. This frontend provides an intuitive interface for monitoring, analyzing, and responding to cybersecurity threats in real-time.

## 🎯 Features

### 🚀 **Real-Time Monitoring**
- **Live Threat Detection**: Continuous monitoring with AI-powered threat analysis
- **Interactive Log Analysis**: Manual log entry testing and automated monitoring
- **Real-Time Charts**: Dynamic threat timeline visualization
- **Performance Metrics**: Live statistics and response time monitoring

### 📊 **Comprehensive Dashboard**
- **Security Overview**: Key metrics and system status at a glance
- **Threat Analytics**: Detailed threat type distribution and trends
- **System Performance**: Resource utilization and health monitoring
- **Recent Threats**: Live feed of detected threats with severity levels

### 🎨 **Modern UI/UX**
- **Dark Cybersecurity Theme**: Professional dark theme with cybersecurity aesthetics
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile
- **Material-UI Components**: Beautiful, accessible, and professional interface
- **Interactive Charts**: Using Recharts for dynamic data visualization

### 🔄 **Real-Time Updates**
- **Backend Integration**: Seamless communication with Flask API
- **Mock Data Mode**: Graceful fallback when backend is unavailable
- **Auto-Refresh**: Live updates and real-time threat monitoring
- **WebSocket Ready**: Architecture prepared for WebSocket integration

## 🛠️ Technology Stack

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development with excellent IDE support
- **Material-UI (MUI)** - Professional component library
- **Recharts** - Responsive chart library for data visualization
- **Axios** - HTTP client for API communication
- **React Router** - Client-side routing for navigation

## 📋 Prerequisites

- **Node.js 16+** and **npm 8+**
- **Backend API** running on `http://localhost:5001` (optional - has mock mode)

## 🚀 Quick Start

### 1. Installation

```bash
cd frontend/threat-detector-dashboard
npm install
```

### 2. Start Development Server

```bash
npm start
```

The application will open in your browser at `http://localhost:3000`

### 3. Production Build

```bash
npm run build
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
REACT_APP_API_URL=http://localhost:5001
REACT_APP_ENV=development
```

### API Configuration

The dashboard automatically detects backend availability:

- **🟢 Backend Online**: Uses live Flask API for real threat detection
- **🔴 Backend Offline**: Uses intelligent mock data for demonstration

## 📱 Usage Guide

### Dashboard Overview

The main dashboard provides:

1. **System Status**: Real-time health indicators
2. **Key Metrics**: Threats detected, systems protected, detection rate
3. **Threat Timeline**: Visual representation of threat activity
4. **Recent Threats**: Live feed of security incidents
5. **System Performance**: Resource utilization monitoring

### Real-Time Monitoring

Access via **Navigation → Real-Time Monitoring**:

1. **Start Monitoring**: Enables automatic log simulation
2. **Manual Analysis**: Enter custom log entries for analysis
3. **Live Charts**: Watch threat levels in real-time
4. **Threat Statistics**: Monitor detection rates and performance

#### Sample Log Entries for Testing

```
GET /admin HTTP/1.1 404 192.168.1.100
SELECT * FROM users WHERE id=1; DROP TABLE users;--
Failed login attempt for user admin from 192.168.1.50
Multiple failed SSH attempts from 10.0.0.45
Malicious file upload attempt: exploit.php
```

### Navigation Features

- **Dashboard**: Main overview with key metrics
- **Real-Time Monitoring**: Live threat detection interface
- **Analytics**: Advanced threat analysis (Coming Soon)
- **Settings**: System configuration (Coming Soon)

## 🎨 UI Components

### Theme Features

- **Dark Mode**: Cybersecurity-focused dark theme
- **Color Coding**: Intuitive threat level colors
  - 🔴 **Critical**: Immediate attention required
  - 🟠 **High**: High priority threats
  - 🔵 **Medium**: Moderate risk level
  - 🟢 **Low/Safe**: Normal activity

### Interactive Elements

- **Responsive Cards**: Hover effects and smooth animations
- **Live Indicators**: Pulsing status indicators
- **Progress Bars**: Visual system performance metrics
- **Charts**: Interactive threat timeline and distribution

## 🔗 API Integration

### Endpoints Used

```typescript
// Threat Detection
POST /api/detect              // Single log analysis
POST /api/detect/batch         // Batch log analysis

// System Monitoring
GET /api/health               // System health check
GET /api/stats                // Performance statistics
GET /api/metrics              // System metrics

// Admin Functions
POST /api/admin/reload_model  // Hot model reloading
GET /api/test                 // Test endpoint
```

### Type Definitions

```typescript
interface ThreatDetectionResult {
  threat_detected: boolean;
  threat_level: string;
  threat_score: number;
  confidence: number;
  inference_time_ms: number;
  features_extracted: number;
  log_entry: string;
  timestamp: string;
}
```

## 🧪 Testing Features

### Mock Data Mode

When the backend is unavailable, the dashboard automatically switches to mock mode:

- **Realistic Threat Simulation**: Intelligent mock threat detection
- **Variable Response Times**: Simulated processing delays
- **Threat Distribution**: Realistic threat type distribution
- **Performance Metrics**: Mock system performance data

### Sample Scenarios

1. **SQL Injection Detection**: `SELECT * FROM users WHERE id=1; DROP TABLE users;--`
2. **Failed Login Attempts**: `Failed login attempt for user admin from 192.168.1.50`
3. **File Upload Threats**: `Malicious file upload attempt: exploit.php`
4. **Network Intrusion**: `Multiple failed SSH attempts from 10.0.0.45`

## 📊 Performance Metrics

The dashboard tracks and displays:

- **Response Time**: Average AI model inference time
- **Detection Rate**: Percentage of threats detected
- **System Health**: Backend availability and model status
- **Throughput**: Logs processed per minute
- **Accuracy**: Detection confidence scores

## 🔮 Future Enhancements

### Phase 5 Roadmap

- **WebSocket Integration**: True real-time communication
- **Advanced Analytics**: Machine learning insights
- **Threat Intelligence**: External threat data integration
- **Alert System**: Email/SMS notifications
- **User Management**: Role-based access control
- **Export Features**: PDF reports and data export
- **Mobile App**: Native iOS/Android applications

### Planned Features

- **Threat Investigation**: Detailed forensic analysis
- **Incident Response**: Automated response workflows
- **Compliance Reports**: SOX, GDPR, HIPAA reporting
- **Network Topology**: Visual network mapping
- **Threat Hunting**: Advanced search capabilities

## 🐛 Troubleshooting

### Common Issues

1. **Backend Connection Failed**
   ```
   Error: Network Error
   Solution: Ensure Flask server is running on port 5001
   ```

2. **Charts Not Displaying**
   ```
   Error: Chart rendering issues
   Solution: Check browser compatibility and refresh page
   ```

3. **Real-Time Updates Stopped**
   ```
   Issue: Monitoring inactive
   Solution: Click "Start Monitoring" button
   ```

### Debug Mode

Enable debug logging in browser console:

```javascript
localStorage.setItem('debug', 'true');
```

## 🤝 Contributing

This is part of the **AI-Enhanced System-Log-Based Cybersecurity Threat Detector** project:

1. **Phase 0**: ✅ Infrastructure Setup
2. **Phase 1**: ✅ Data Acquisition & Processing
3. **Phase 2**: ✅ AI Model Training
4. **Phase 3**: ✅ Backend API Development
5. **Phase 4**: ✅ Frontend Dashboard (This Phase)
6. **Phase 5**: 🚀 Advanced Features & Deployment

## 📜 License

MIT License - See LICENSE file for details.

## 🙋‍♂️ Support

For questions or issues:

1. Check the troubleshooting section
2. Review backend API documentation
3. Ensure all dependencies are installed
4. Verify environment configuration

---

**🔒 CyberGuard AI** - Advanced threat detection at your fingertips!
