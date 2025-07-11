import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, Layout, Typography } from 'antd';
import { Toaster } from 'react-hot-toast';
import DocumentUpload from './components/DocumentUpload';
import ResultsTable from './components/ResultsTable';
import AnalysisButton from './components/AnalysisButton';
import { useDocumentStore } from './stores/documentStore';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

const App: React.FC = () => {
  const { analysisResults, isAnalyzing } = useDocumentStore();

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
              </Routes>
            </div>
          </Content>
          
          <Footer className="app-footer">
            <div className="footer-content">
              <p>© 2024 Система анализа документов. Все права защищены.</p>
            </div>
          </Footer>
        </Layout>
      </Router>
      
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </ConfigProvider>
  );
};

export default App; 