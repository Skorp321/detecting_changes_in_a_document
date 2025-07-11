import React from 'react';
import { Button, Space, Typography, Tooltip } from 'antd';
import { PlayCircleOutlined, LoadingOutlined } from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import { AnalysisButtonProps } from '../types';
import { analyzeDocuments } from '../services/api';
import toast from 'react-hot-toast';

const { Text } = Typography;

const AnalysisButton: React.FC<AnalysisButtonProps> = ({
  disabled: propDisabled = false,
  onAnalyze,
  className = '',
}) => {
  const {
    referenceDoc,
    clientDoc,
    isAnalyzing,
    setIsAnalyzing,
    setAnalysisResults,
    setError,
  } = useDocumentStore();

  const isDisabled = propDisabled || !referenceDoc || !clientDoc || isAnalyzing;

  const handleAnalyze = async () => {
    if (!referenceDoc || !clientDoc) {
      toast.error('Необходимо загрузить оба документа');
      return;
    }

    try {
      setIsAnalyzing(true);
      setError(null);
      
      const toastId = toast.loading('Анализ документов...');

      const response = await analyzeDocuments({
        referenceDoc,
        clientDoc,
      });

      if (response.success && response.data) {
        setAnalysisResults(response.data.changes);
        toast.success('Анализ завершен успешно', { id: toastId });
        
        // Show summary
        const { summary } = response.data;
        if (summary.criticalChanges > 0) {
          toast.error(
            `Найдено ${summary.criticalChanges} критических изменений из ${summary.totalChanges} общих`
          );
        } else {
          toast.success(
            `Найдено ${summary.totalChanges} изменений. Критических изменений нет.`
          );
        }
        
        onAnalyze?.();
      } else {
        throw new Error(response.error || 'Ошибка при анализе документов');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Неизвестная ошибка';
      setError(errorMessage);
      toast.error(`Ошибка анализа: ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getTooltipTitle = () => {
    if (!referenceDoc && !clientDoc) {
      return 'Загрузите эталонный документ и экземпляр клиента';
    }
    if (!referenceDoc) {
      return 'Загрузите эталонный документ';
    }
    if (!clientDoc) {
      return 'Загрузите экземпляр клиента';
    }
    if (isAnalyzing) {
      return 'Анализ в процессе...';
    }
    return 'Запустить анализ изменений';
  };

  return (
    <div className={`analysis-button ${className}`}>
      <Space direction="vertical" size="small" style={{ width: '100%' }}>
        <Tooltip title={getTooltipTitle()}>
          <Button
            type="primary"
            size="large"
            icon={isAnalyzing ? <LoadingOutlined /> : <PlayCircleOutlined />}
            disabled={isDisabled}
            onClick={handleAnalyze}
            loading={isAnalyzing}
            style={{ width: '100%', height: '48px' }}
          >
            {isAnalyzing ? 'Анализ в процессе...' : 'Анализировать изменения'}
          </Button>
        </Tooltip>
        
        {referenceDoc && clientDoc && (
          <div style={{ textAlign: 'center' }}>
            <Text type="secondary" style={{ fontSize: '12px' }}>
              Готов к анализу: {referenceDoc.name} ↔ {clientDoc.name}
            </Text>
          </div>
        )}
      </Space>
    </div>
  );
};

export default AnalysisButton; 