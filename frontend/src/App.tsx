import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, Layout, Typography } from 'antd';
import { Toaster } from 'react-hot-toast';
import { DocumentUpload, ResultsTable, AnalysisButton } from './components/LazyComponents';
import { useDocumentStore } from './stores/documentStore';
import { initWebVitals } from './services/webVitals';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const { analysisResults, isAnalyzing } = useDocumentStore();

  useEffect(() => {
    // Инициализация Web Vitals мониторинга
    initWebVitals();
  }, []);

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
        },
      }}
    >
      <Router>
        <Layout className="app-layout">
          <Header className="app-header">
            <Title level={2} style={{ color: 'white', margin: 0 }}>
              Система анализа изменений в документах
            </Title>
          </Header>
          
          <Content className="app-content">
            <div className="container">
              <Routes>
                <Route path="/" element={
                  <div className="main-content">
                    <div className="upload-section">
                      <Title level={3}>Загрузка документов</Title>
                      <DocumentUpload />
                      <div className="analysis-button-container">
                        <AnalysisButton />
                      </div>
                    </div>
                    
                    {(analysisResults || isAnalyzing) && (
                      <div className="results-section">
                        <Title level={3}>Результаты анализа</Title>
                        <ResultsTable />
                      </div>
                    )}
                  </div>
                } />
                
                <Route path="/results" element={
                  <div className="results-page">
                    <Title level={2}>Результаты анализа</Title>
                    <ResultsTable />
                  </div>
                } />
              </Routes>
            </div>
          </Content>
          
          <Footer className="app-footer">
            <div className="footer-content">
              <p>&copy; 2024 Система анализа изменений в документах</p>
            </div>
          </Footer>
        </Layout>
      </Router>
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 5000,
          style: {
            background: '#fff',
            color: '#333',
            borderRadius: '8px',
            border: '1px solid #d9d9d9',
          },
        }}
      />
    </ConfigProvider>
  );
};

export default App; 