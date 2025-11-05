/**
 * Custom hooks for sales processing
 */

import { useState, useCallback, useEffect } from 'react';
import { salesService, UploadResponse, ProcessingMetrics } from '@/lib/services/salesService';
import { validateCSVFile } from '@/lib/utils/fileUtils';

export interface UseFileUploadReturn {
  file: File | null;
  uploading: boolean;
  progress: number;
  error: string | null;
  jobId: string | null;
  downloadUrl: string | null;
  status: string | null;
  metrics: ProcessingMetrics | null;
  message: string | null;
  setFile: (file: File | null) => void;
  handleFileSelect: (file: File) => void;
  handleUpload: () => Promise<void>;
  reset: () => void;
}

export const useFileUpload = (): UseFileUploadReturn => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [jobId, setJobId] = useState<string | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<ProcessingMetrics | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Poll for job status when processing
  useEffect(() => {
    if (!jobId || status !== 'processing') {
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const statusResponse = await salesService.getJobStatus(jobId);
        setStatus(statusResponse.status);
        
        if (statusResponse.metrics) {
          setMetrics(statusResponse.metrics);
        }
        
        if (statusResponse.download_url) {
          setDownloadUrl(statusResponse.download_url);
        }
        
        if (statusResponse.error_message) {
          setError(statusResponse.error_message);
        }
        
        // Stop polling when completed or error
        if (statusResponse.status === 'completed' || statusResponse.status === 'error') {
          clearInterval(pollInterval);
        }
      } catch (err: any) {
        console.error('Error polling job status:', err);
        // Continue polling even on error
      }
    }, 1000); // Poll every second

    return () => clearInterval(pollInterval);
  }, [jobId, status]);

  const handleFileSelect = useCallback((selectedFile: File) => {
    if (!validateCSVFile(selectedFile)) {
      setError('Please upload a CSV file');
      return;
    }
    setFile(selectedFile);
    setError(null);
    setJobId(null);
    setDownloadUrl(null);
    setStatus(null);
    setMetrics(null);
    setMessage(null);
  }, []);

  const handleUpload = useCallback(async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const response: UploadResponse = await salesService.uploadCSV(
        file,
        (progressValue) => {
          setProgress(progressValue);
        }
      );

      setJobId(response.job_id);
      setStatus(response.status);
      setMessage(response.message || null);
      
      if (response.download_url) {
        setDownloadUrl(response.download_url);
      }
      
      if (response.metrics) {
        setMetrics(response.metrics);
      }
      
      setProgress(100);
    } catch (err: any) {
      setError(err.message || 'Upload failed. Please try again.');
      setProgress(0);
    } finally {
      setUploading(false);
    }
  }, [file]);

  const reset = useCallback(() => {
    setFile(null);
    setJobId(null);
    setDownloadUrl(null);
    setStatus(null);
    setMetrics(null);
    setMessage(null);
    setError(null);
    setProgress(0);
  }, []);

  return {
    file,
    uploading,
    progress,
    error,
    jobId,
    downloadUrl,
    status,
    metrics,
    message,
    setFile,
    handleFileSelect,
    handleUpload,
    reset,
  };
};

