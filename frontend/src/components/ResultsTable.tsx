import React, { useState, useMemo } from 'react';
import { 
  Table, 
  Button, 
  Space, 
  Typography, 
  Tag, 
  Tooltip,
  Card,
  Dropdown,
  Modal,
  Input,
  Empty,
  Spin
} from 'antd';
import { 
  ExportOutlined, 
  DownloadOutlined,
  EyeOutlined,
  SearchOutlined,
  FilterOutlined
} from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import { ResultsTableProps, AnalysisResult, ExportFormat } from '../types';
import { exportResults } from '../services/api';
import toast from 'react-hot-toast';

const { Text, Paragraph } = Typography;
const { Search } = Input;

// Функция для рендеринга подсвеченного текста
const renderHighlightedText = (text: string) => {
  if (!text) return <Text type="secondary">Пусто</Text>;
  
  // Заменяем маркеры подсветки на JSX элементы
  const parts = text.split(/(\[-\].*?\[\/\-\]|\[\+\].*?\[\/\+\])/);
  
  return (
    <span>
      {parts.map((part, index) => {
        if (part.startsWith('[-]') && part.endsWith('[/-]')) {
          // Удаленный текст
          const content = part.slice(3, -4);
          return (
            <span key={index} style={{ 
              backgroundColor: '#ffcdd2', 
              textDecoration: 'line-through',
              color: '#d32f2f',
              padding: '2px 4px',
              borderRadius: '3px',
              margin: '0 1px'
            }}>
              {content}
            </span>
          );
        } else if (part.startsWith('[+]') && part.endsWith('[/+]')) {
          // Добавленный текст
          const content = part.slice(3, -4);
          return (
            <span key={index} style={{ 
              backgroundColor: '#c8e6c9', 
              color: '#2e7d32',
              padding: '2px 4px',
              borderRadius: '3px',
              margin: '0 1px'
            }}>
              {content}
            </span>
          );
        } else {
          // Обычный текст
          return <span key={index}>{part}</span>;
        }
      })}
    </span>
  );
};

const ResultsTable: React.FC<ResultsTableProps> = ({
  results: propResults,
  loading = false,
  onExport,
  className = '',
}) => {
  const { analysisResults, isAnalyzing } = useDocumentStore();
  const [searchText, setSearchText] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all');
  const [isDetailModalVisible, setIsDetailModalVisible] = useState(false);
  const [selectedResult, setSelectedResult] = useState<AnalysisResult | null>(null);
  const [exportLoading, setExportLoading] = useState(false);

  const results = propResults || analysisResults || [];

  const filteredResults = useMemo(() => {
    return results.filter(result => {
      const matchesSearch = !searchText || 
        result.originalText.toLowerCase().includes(searchText.toLowerCase()) ||
        result.modifiedText.toLowerCase().includes(searchText.toLowerCase()) ||
        result.llmComment.toLowerCase().includes(searchText.toLowerCase());
      
      const matchesSeverity = selectedSeverity === 'all' || result.severity === selectedSeverity;
      
      return matchesSearch && matchesSeverity;
    });
  }, [results, searchText, selectedSeverity]);

  const handleExport = async (format: ExportFormat) => {
    if (results.length === 0) {
      toast.error('Нет данных для экспорта');
      return;
    }

    try {
      setExportLoading(true);
      await exportResults(results, format);
      toast.success(`Экспорт в формат ${format.toUpperCase()} завершен`);
      onExport?.(format);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Ошибка экспорта';
      toast.error(`Ошибка экспорта: ${errorMessage}`);
    } finally {
      setExportLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'red';
      case 'high': return 'orange';
      case 'medium': return 'yellow';
      case 'low': return 'green';
      default: return 'default';
    }
  };

  const getSeverityText = (severity: string) => {
    switch (severity) {
      case 'critical': return 'Критический';
      case 'high': return 'Высокий';
      case 'medium': return 'Средний';
      case 'low': return 'Низкий';
      default: return severity;
    }
  };

  const getChangeTypeText = (type: string) => {
    switch (type) {
      case 'addition': return 'Добавление';
      case 'deletion': return 'Удаление';
      case 'modification': return 'Изменение';
      default: return type;
    }
  };

  const showDetailModal = (result: AnalysisResult) => {
    setSelectedResult(result);
    setIsDetailModalVisible(true);
  };

  const exportMenuItems = [
    {
      key: 'csv',
      label: 'Экспорт в CSV',
      icon: <ExportOutlined />,
      onClick: () => handleExport('csv'),
    },
    {
      key: 'pdf',
      label: 'Экспорт в PDF',
      icon: <ExportOutlined />,
      onClick: () => handleExport('pdf'),
    },
    {
      key: 'word',
      label: 'Экспорт в Word',
      icon: <ExportOutlined />,
      onClick: () => handleExport('word'),
    },
  ];

  const severityFilterItems = [
    { key: 'all', label: 'Все уровни' },
    { key: 'critical', label: 'Критический' },
    { key: 'high', label: 'Высокий' },
    { key: 'medium', label: 'Средний' },
    { key: 'low', label: 'Низкий' },
  ];

  const columns = [
    {
              title: 'Редакция СБЛ',
      dataIndex: 'originalText',
      key: 'originalText',
      width: '25%',
      render: (text: string, record: AnalysisResult) => (
        <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
          <div style={{ fontSize: '13px', lineHeight: '1.4' }}>
            {record.highlightedOriginal ? 
              renderHighlightedText(record.highlightedOriginal) : 
              (text || <Text type="secondary">Пусто</Text>)
            }
          </div>
        </div>
      ),
    },
    {
              title: 'Редакция лизингополучателя',
      dataIndex: 'modifiedText',
      key: 'modifiedText',
      width: '25%',
      render: (text: string, record: AnalysisResult) => (
        <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
          <div style={{ fontSize: '13px', lineHeight: '1.4' }}>
            {record.highlightedModified ? 
              renderHighlightedText(record.highlightedModified) : 
              (text || <Text type="secondary">Пусто</Text>)
            }
          </div>
        </div>
      ),
    },
    {
      title: 'Комментарии LLM',
      dataIndex: 'llmComment',
      key: 'llmComment',
      width: '30%',
      render: (text: string) => (
        <div style={{ maxHeight: '100px', overflowY: 'auto' }}>
          <Paragraph
            ellipsis={{ rows: 3, expandable: true, symbol: 'больше' }}
            style={{ margin: 0 }}
          >
            {text}
          </Paragraph>
        </div>
      ),
    },
    {
      title: 'Необходимые согласования',
      dataIndex: 'requiredServices',
      key: 'requiredServices',
      width: '15%',
      render: (services: string[]) => (
        <div>
          {services.map(service => (
            <Tag key={service} color="blue" style={{ marginBottom: 4 }}>
              {service}
            </Tag>
          ))}
        </div>
      ),
    },
    {
      title: 'Действия',
      key: 'actions',
      width: '5%',
      render: (_: any, record: AnalysisResult) => (
        <Space size="small">
          <Tooltip title="Подробнее">
            <Button
              type="text"
              icon={<EyeOutlined />}
              onClick={() => showDetailModal(record)}
              size="small"
            />
          </Tooltip>
          <Tag color={getSeverityColor(record.severity)}>
            {getSeverityText(record.severity)}
          </Tag>
        </Space>
      ),
    },
  ];

  if (loading || isAnalyzing) {
    return (
      <Card className={className}>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text>Анализ документов...</Text>
          </div>
        </div>
      </Card>
    );
  }

  if (results.length === 0) {
    return (
      <Card className={className}>
        <Empty
          description="Нет результатов анализа"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  return (
    <div className={`results-table ${className}`}>
      <Card>
        <div className="table-header" style={{ marginBottom: 16 }}>
          <Space wrap>
            <Search
              placeholder="Поиск по тексту..."
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
              style={{ width: 300 }}
              prefix={<SearchOutlined />}
            />
            
            <Dropdown
              menu={{
                items: severityFilterItems,
                onClick: ({ key }) => setSelectedSeverity(key),
              }}
            >
              <Button icon={<FilterOutlined />}>
                Уровень: {severityFilterItems.find(item => item.key === selectedSeverity)?.label}
              </Button>
            </Dropdown>

            <Dropdown
              menu={{ items: exportMenuItems }}
              disabled={exportLoading || results.length === 0}
            >
              <Button 
                icon={<DownloadOutlined />}
                loading={exportLoading}
              >
                Экспорт
              </Button>
            </Dropdown>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={filteredResults}
          rowKey="id"
          pagination={{
            total: filteredResults.length,
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) =>
              `${range[0]}-${range[1]} из ${total} результатов`,
          }}
          scroll={{ x: 1200 }}
          size="middle"
        />
      </Card>

      <Modal
        title="Детали изменения"
        open={isDetailModalVisible}
        onCancel={() => setIsDetailModalVisible(false)}
        footer={null}
        width={800}
      >
        {selectedResult && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <Space>
                <Tag color={getSeverityColor(selectedResult.severity)}>
                  {getSeverityText(selectedResult.severity)}
                </Tag>
                <Tag color="purple">
                  {getChangeTypeText(selectedResult.changeType)}
                </Tag>
                <Text type="secondary">
                  Уверенность: {Math.round(selectedResult.confidence * 100)}%
                </Text>
              </Space>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>Редакция СБЛ:</Text>
              <Paragraph style={{ background: '#f5f5f5', padding: 8, marginTop: 8 }}>
                {selectedResult.originalText}
              </Paragraph>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>Редакция лизингополучателя:</Text>
              <Paragraph style={{ background: '#f0f8ff', padding: 8, marginTop: 8 }}>
                {selectedResult.modifiedText}
              </Paragraph>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>Комментарии LLM:</Text>
              <Paragraph style={{ marginTop: 8 }}>
                {selectedResult.llmComment}
              </Paragraph>
            </div>

            <div>
              <Text strong>Необходимые согласования:</Text>
              <div style={{ marginTop: 8 }}>
                {selectedResult.requiredServices.map(service => (
                  <Tag key={service} color="blue">
                    {service}
                  </Tag>
                ))}
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
};

export default ResultsTable; 