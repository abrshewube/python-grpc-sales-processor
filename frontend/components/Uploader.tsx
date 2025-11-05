'use client';

import { useCallback } from 'react';
import { useFileUpload } from '@/lib/hooks/useFileUpload';
import { formatFileSize } from '@/lib/utils/fileUtils';

export default function Uploader() {
  const {
    file,
    uploading,
    progress,
    error,
    jobId,
    downloadUrl,
    status,
    metrics,
    message,
    handleFileSelect,
    handleUpload,
    reset,
  } = useFileUpload();

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files[0]) {
        handleFileSelect(e.target.files[0]);
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    },
    [handleFileSelect]
  );

  const handleUploadClick = useCallback(async () => {
    await handleUpload();
  }, [handleUpload]);

  const formatTime = (ms: number): string => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  return (
    <div className="bg-white rounded-xl shadow-xl overflow-hidden transform transition-all duration-300">
      <div className="p-6 sm:p-8">
        {/* Drag & Drop Zone */}
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          className={`border-2 border-dashed rounded-xl p-10 text-center transition-all duration-300 ${
            uploading
              ? 'border-gray-300 opacity-50 pointer-events-none'
              : 'border-gray-300 hover:border-emerald-400 hover:bg-emerald-50/30 cursor-pointer'
          }`}
        >
          {!file ? (
            <>
              <div className="flex justify-center mb-5">
                <div className="w-20 h-20 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-full flex items-center justify-center shadow-sm">
                  <svg className="w-10 h-10 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                </div>
              </div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">
                Drop your CSV file here
              </h3>
              <p className="text-sm text-gray-500 mb-5">or click to browse</p>
              <label className="inline-flex items-center px-5 py-2.5 bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200 cursor-pointer">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Choose File
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleFileChange}
                  disabled={uploading}
                  className="hidden"
                />
              </label>
              <p className="text-xs text-gray-400 mt-4">CSV files only</p>
            </>
          ) : (
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-3 animate-bounce">
                <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="text-center">
                <p className="text-base font-semibold text-gray-800 mb-1">{file.name}</p>
                <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                <button
                  onClick={reset}
                  className="mt-2 text-xs text-emerald-600 hover:text-emerald-700 font-medium"
                >
                  Change file
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {uploading && (
          <div className="mt-5 animate-fadeIn">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-xs font-medium text-gray-700 flex items-center">
                <svg className="animate-spin -ml-1 mr-1.5 h-3.5 w-3.5 text-emerald-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Uploading...
              </span>
              <span className="text-xs font-bold text-emerald-600">{progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden shadow-inner">
              <div
                className="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 h-2 rounded-full transition-all duration-300 ease-out shadow-sm"
                style={{ width: `${progress}%` }}
              >
                <div className="h-full w-full bg-white opacity-30 animate-pulse"></div>
              </div>
            </div>
          </div>
        )}

        {/* Processing Status */}
        {jobId && status === 'processing' && (
          <div className="mt-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg animate-slideIn">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <svg className="animate-spin h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-bold text-blue-800 mb-1">Processing...</h3>
                <p className="text-xs text-blue-700">{message || 'Your file is being processed in the background.'}</p>
                <p className="text-xs text-gray-500 mt-2 font-mono">Job ID: {jobId}</p>
              </div>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border-l-4 border-red-500 rounded-lg animate-slideIn">
            <div className="flex items-center">
              <svg className="w-4 h-4 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-sm text-red-700 font-medium">{error}</p>
            </div>
          </div>
        )}

        {/* Success Message with Details */}
        {jobId && status === 'completed' && downloadUrl && (
          <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border-2 border-green-200 rounded-lg animate-slideIn shadow-md">
            <div className="flex items-start">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
              <div className="ml-3 flex-1">
                <h3 className="text-sm font-bold text-green-800 mb-1">Processing Complete!</h3>
                <p className="text-xs text-green-700 mb-3">Your file has been processed successfully.</p>
                
                {/* Processing Metrics */}
                {metrics && (
                  <div className="bg-white rounded-md p-3 mb-3 border border-green-200">
                    <p className="text-xs text-gray-700 mb-2 font-semibold">Processing Details:</p>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Processing Time:</span>
                        <span className="font-semibold text-gray-800">{formatTime(metrics.processing_time_ms)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Rows Processed:</span>
                        <span className="font-semibold text-gray-800">{metrics.rows_processed.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Rows Skipped:</span>
                        <span className="font-semibold text-gray-800">{metrics.rows_skipped.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Departments:</span>
                        <span className="font-semibold text-gray-800">{metrics.departments_count}</span>
                      </div>
                      {metrics.peak_memory_mb > 0 && (
                        <div className="flex justify-between col-span-2">
                          <span className="text-gray-600">Peak Memory:</span>
                          <span className="font-semibold text-gray-800">{metrics.peak_memory_mb} MB</span>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* Download Link */}
                <div className="flex flex-col sm:flex-row gap-2 mb-3">
                  <a
                    href={downloadUrl}
                    download
                    className="inline-flex items-center justify-center px-4 py-2.5 bg-gradient-to-r from-green-500 to-emerald-600 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transform hover:scale-105 transition-all duration-200 text-sm"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download Processed File
                  </a>
                  <button
                    onClick={reset}
                    className="inline-flex items-center justify-center px-4 py-2.5 bg-white text-gray-700 font-semibold rounded-lg border-2 border-gray-300 hover:border-gray-400 transition-all duration-200 text-sm"
                  >
                    Process Another File
                  </button>
                </div>

                {/* Job ID */}
                <div className="pt-2 border-t border-green-200">
                  <p className="text-xs text-gray-500 font-mono">Job ID: {jobId}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Button */}
        {file && !uploading && !jobId && (
          <div className="mt-5">
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-3 mb-3">
              <p className="text-xs text-emerald-800 font-medium mb-1">Ready to process</p>
              <p className="text-xs text-emerald-700">Click the button below to upload and process your CSV file. The system will aggregate sales by department.</p>
            </div>
            <button
              onClick={handleUploadClick}
              className="w-full py-3 px-6 bg-gradient-to-r from-emerald-500 via-teal-600 to-cyan-600 text-white text-sm font-bold rounded-lg shadow-lg hover:shadow-xl transform hover:scale-[1.01] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
            >
              <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Upload & Process CSV
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

