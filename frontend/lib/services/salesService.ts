import axios, { AxiosProgressEvent } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ProcessingMetrics {
  processing_time_ms: number;
  rows_processed: number;
  rows_skipped: number;
  departments_count: number;
  peak_memory_mb: number;
}

export interface UploadResponse {
  job_id: string;
  status: string;
  download_url: string;
  message?: string;
  metrics?: ProcessingMetrics;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  download_url?: string;
  error_message?: string;
  metrics?: ProcessingMetrics;
}

export class SalesService {
  private baseURL: string;

  constructor(baseURL: string = API_URL) {
    this.baseURL = baseURL;
  }

  /**
   * Upload CSV file and process it
   * @param file - CSV file to upload
   * @param onProgress - Optional progress callback
   * @returns Promise with upload response
   */
  async uploadCSV(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<UploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post<UploadResponse>(
        `${this.baseURL}/api/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent: AxiosProgressEvent) => {
            if (progressEvent.total && onProgress) {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              onProgress(percentCompleted);
            }
          },
        }
      );

      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.error || 'Upload failed. Please try again.'
      );
    }
  }

  /**
   * Get job status by job ID
   * @param jobId - Job ID to check status for
   * @returns Promise with job status response
   */
  async getJobStatus(jobId: string): Promise<JobStatusResponse> {
    try {
      const response = await axios.get<JobStatusResponse>(
        `${this.baseURL}/api/status/${jobId}`
      );
      return response.data;
    } catch (error: any) {
      throw new Error(
        error.response?.data?.error || 'Failed to fetch job status.'
      );
    }
  }
}

// Export singleton instance
export const salesService = new SalesService();

