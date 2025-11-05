'use client';

import Uploader from '@/components/Uploader';

export default function UploadForm() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-zinc-50 py-8 px-4 sm:px-6 lg:px-8 flex flex-col">
      <div className="max-w-3xl mx-auto flex-1">
        {/* Header Section */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-2xl shadow-lg mb-5 transform hover:scale-105 transition-transform duration-300">
            <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2 bg-gradient-to-r from-emerald-600 to-teal-700 bg-clip-text text-transparent">
            CSV Sales Processor
          </h1>
          <p className="text-base text-gray-600 max-w-xl mx-auto">
            Upload CSV files for department sales aggregation
          </p>
        </div>

        {/* Upload Section */}
        <Uploader />
      </div>

      {/* Footer */}
      <footer className="mt-12 text-center">
        <p className="text-sm text-gray-500">
          by <span className="font-semibold text-gray-700">Abrham Wube</span>
        </p>
      </footer>
    </div>
  );
}
