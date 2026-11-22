import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Renewable Energy Grid Dashboard',
  description: 'Real-time telemetry and monitoring for renewable energy sources',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
