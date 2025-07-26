import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import ProfileInput from './components/ProfileInput';
import CompatibilityReport from './components/CompatibilityReport';
import LoadingSpinner from './components/LoadingSpinner';

// Services
import api from './services/api';

// Styles
import './styles/main.css';

function App() {
  const [currentStep, setCurrentStep] = useState('input'); // 'input', 'loading', 'results'
  const [profiles, setProfiles] = useState([]);
  const [reportData, setReportData] = useState(null);
  const [zodiacSigns, setZodiacSigns] = useState([]);
  const [loading, setLoading] = useState(false);

  // Load zodiac signs on mount
  useEffect(() => {
    const loadZodiacSigns = async () => {
      try {
        const response = await api.getZodiacSigns();
        setZodiacSigns(response.data.signs);
      } catch (error) {
        console.error('Failed to load zodiac signs:', error);
      }
    };
    
    loadZodiacSigns();
  }, []);

  const handleAnalyzeTeam = async (profileInputs) => {
    setLoading(true);
    setCurrentStep('loading');
    
    try {
      const response = await api.analyzeTeam(profileInputs);
      setReportData(response.data);
      setCurrentStep('results');
    } catch (error) {
      console.error('Analysis failed:', error);
      setCurrentStep('input');
      // Error toast will be handled by the API service
    } finally {
      setLoading(false);
    }
  };

  const handleStartOver = () => {
    setCurrentStep('input');
    setReportData(null);
    setProfiles([]);
  };

  return (
    <Router>
      <div className="app">
        <Toaster position="top-center" />
        
        {/* Cosmic Background */}
        <div className="cosmic-background">
          <div className="stars"></div>
          <div className="shooting-star"></div>
        </div>

        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={
              <motion.div
                key={currentStep}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="main-container"
              >
                {currentStep === 'input' && (
                  <ProfileInput
                    onAnalyze={handleAnalyzeTeam}
                    zodiacSigns={zodiacSigns}
                    loading={loading}
                  />
                )}
                
                {currentStep === 'loading' && (
                  <LoadingSpinner />
                )}
                
                {currentStep === 'results' && reportData && (
                  <CompatibilityReport
                    reportData={reportData}
                    onStartOver={handleStartOver}
                  />
                )}
              </motion.div>
            } />
            
            <Route path="/report/:reportId" element={
              <SharedReport />
            } />
          </Routes>
        </AnimatePresence>
      </div>
    </Router>
  );
}

// Component for shared reports
function SharedReport() {
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const reportId = window.location.pathname.split('/')[2];
  
  useEffect(() => {
    const loadReport = async () => {
      try {
        const response = await api.getReport(reportId);
        setReportData(response.data);
      } catch (error) {
        console.error('Failed to load report:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (reportId) {
      loadReport();
    }
  }, [reportId]);
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  if (!reportData) {
    return (
      <div className="error-container">
        <h2>Report Not Found</h2>
        <p>This report may have expired or the link is invalid.</p>
        <button 
          onClick={() => window.location.href = '/'}
          className="btn-primary"
        >
          Create New Report
        </button>
      </div>
    );
  }
  
  return (
    <CompatibilityReport
      reportData={reportData}
      onStartOver={() => window.location.href = '/'}
      isSharedView={true}
    />
  );
}

export default App;