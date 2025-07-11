import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Card, Typography, Button, Progress, Alert, Space } from 'antd';
import { InboxOutlined, FileOutlined, DeleteOutlined } from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import { DocumentUploadProps } from '../types';
import toast from 'react-hot-toast';

const { Title, Text } = Typography;

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onFilesChange,
  disabled = false,
  className = '',
}) => {
  const {
    referenceDoc,
    clientDoc,
    uploadProgress,
    error,
    setReferenceDoc,
    setClientDoc,
    setUploadProgress,
    setError,
  } = useDocumentStore();

  const validateFile = useCallback((file: File): boolean => {
    const allowedTypes = [
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
    ];
    const maxSize = 10 * 1024 * 1024; // 10MB

    if (!allowedTypes.includes(file.type)) {
      setError('Поддерживаются только файлы .pdf, .docx, .txt');
      return false;
    }

    if (file.size > maxSize) {
      setError('Размер файла не должен превышать 10MB');
      return false;
    }

    return true;
  }, [setError]);

  const onDropReference = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        if (file && validateFile(file)) {
          setReferenceDoc(file);
          setUploadProgress('reference', 100);
          toast.success('Эталонный документ загружен');
          onFilesChange?.({ reference: file, client: clientDoc });
        }
      }
    },
    [validateFile, setReferenceDoc, setUploadProgress, onFilesChange, clientDoc]
  );

  const onDropClient = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        const file = acceptedFiles[0];
        if (file && validateFile(file)) {
          setClientDoc(file);
          setUploadProgress('client', 100);
          toast.success('Экземпляр клиента загружен');
          onFilesChange?.({ reference: referenceDoc, client: file });
        }
      }
    },
    [validateFile, setClientDoc, setUploadProgress, onFilesChange, referenceDoc]
  );

  const {
    getRootProps: getReferenceRootProps,
    getInputProps: getReferenceInputProps,
    isDragActive: isReferenceDragActive,
  } = useDropzone({
    onDrop: onDropReference,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: false,
    disabled,
  });

  const {
    getRootProps: getClientRootProps,
    getInputProps: getClientInputProps,
    isDragActive: isClientDragActive,
  } = useDropzone({
    onDrop: onDropClient,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
    },
    multiple: false,
    disabled,
  });

  const removeFile = useCallback(
    (type: 'reference' | 'client') => {
      if (type === 'reference') {
        setReferenceDoc(null);
        setUploadProgress('reference', 0);
        onFilesChange?.({ reference: null, client: clientDoc });
        toast.success('Эталонный документ удален');
      } else {
        setClientDoc(null);
        setUploadProgress('client', 0);
        onFilesChange?.({ reference: referenceDoc, client: null });
        toast.success('Экземпляр клиента удален');
      }
    },
    [setReferenceDoc, setClientDoc, setUploadProgress, onFilesChange, referenceDoc, clientDoc]
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`document-upload ${className}`}>
      {error && (
        <Alert
          message="Ошибка загрузки"
          description={error}
          type="error"
          showIcon
          closable
          onClose={() => setError(null)}
          style={{ marginBottom: 16 }}
        />
      )}

      <div className="upload-container" style={{ display: 'flex', gap: '16px' }}>
        {/* Reference document upload */}
        <Card
          title={
            <Space>
              <FileOutlined />
              <Title level={5} style={{ margin: 0 }}>
                Эталонный документ
              </Title>
            </Space>
          }
          style={{ flex: 1 }}
        >
          {referenceDoc ? (
            <div className="file-info">
              <div className="file-details">
                <Text strong>{referenceDoc.name}</Text>
                <br />
                <Text type="secondary">{formatFileSize(referenceDoc.size)}</Text>
              </div>
              {uploadProgress.reference > 0 && uploadProgress.reference < 100 && (
                <Progress percent={uploadProgress.reference} size="small" />
              )}
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => removeFile('reference')}
                disabled={disabled}
                style={{ marginTop: 8 }}
              >
                Удалить
              </Button>
            </div>
          ) : (
            <div
              {...getReferenceRootProps()}
              className={`dropzone ${isReferenceDragActive ? 'active' : ''}`}
              style={{
                border: '2px dashed #d9d9d9',
                borderRadius: '6px',
                padding: '40px 20px',
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: isReferenceDragActive ? '#f0f8ff' : '#fafafa',
                transition: 'all 0.3s ease',
              }}
            >
              <input {...getReferenceInputProps()} />
              <InboxOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
              <div style={{ marginTop: 16 }}>
                <Text>
                  {isReferenceDragActive
                    ? 'Отпустите файл здесь'
                    : 'Нажмите или перетащите файл сюда'}
                </Text>
                <br />
                <Text type="secondary">Поддерживаются файлы .pdf, .docx, .txt</Text>
              </div>
            </div>
          )}
        </Card>

        {/* Client document upload */}
        <Card
          title={
            <Space>
              <FileOutlined />
              <Title level={5} style={{ margin: 0 }}>
                Экземпляр клиента
              </Title>
            </Space>
          }
          style={{ flex: 1 }}
        >
          {clientDoc ? (
            <div className="file-info">
              <div className="file-details">
                <Text strong>{clientDoc.name}</Text>
                <br />
                <Text type="secondary">{formatFileSize(clientDoc.size)}</Text>
              </div>
              {uploadProgress.client > 0 && uploadProgress.client < 100 && (
                <Progress percent={uploadProgress.client} size="small" />
              )}
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={() => removeFile('client')}
                disabled={disabled}
                style={{ marginTop: 8 }}
              >
                Удалить
              </Button>
            </div>
          ) : (
            <div
              {...getClientRootProps()}
              className={`dropzone ${isClientDragActive ? 'active' : ''}`}
              style={{
                border: '2px dashed #d9d9d9',
                borderRadius: '6px',
                padding: '40px 20px',
                textAlign: 'center',
                cursor: 'pointer',
                backgroundColor: isClientDragActive ? '#f0f8ff' : '#fafafa',
                transition: 'all 0.3s ease',
              }}
            >
              <input {...getClientInputProps()} />
              <InboxOutlined style={{ fontSize: '48px', color: '#d9d9d9' }} />
              <div style={{ marginTop: 16 }}>
                <Text>
                  {isClientDragActive
                    ? 'Отпустите файл здесь'
                    : 'Нажмите или перетащите файл сюда'}
                </Text>
                <br />
                <Text type="secondary">Поддерживаются файлы .pdf, .docx, .txt</Text>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default DocumentUpload; 