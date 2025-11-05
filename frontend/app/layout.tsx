import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CSV Sales Processor - Department Sales Aggregation',
  description: 'Upload and process CSV files to get instant department-wise sales aggregation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  )
}

