import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Strategic Political Donation Platform',
  description: 'GiveWell for Politics - Find high-impact donation opportunities',
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
