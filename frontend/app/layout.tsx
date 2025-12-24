import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Agent Framework + Generative UI',
  description: 'Integrated AI agent system with dynamic UI generation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="font-sans">{children}</body>
    </html>
  )
}
