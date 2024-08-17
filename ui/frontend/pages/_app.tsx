import type { AppProps } from 'next/app'
import { ReactFlowProvider } from '@xyflow/react'
import { ThemeProvider } from '@/components/themeProvider'

import '../styles/globals.css'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="light"
      enableSystem
      disableTransitionOnChange
    >
      <ReactFlowProvider>
        <Component {...pageProps} />
      </ReactFlowProvider>
    </ThemeProvider>
  )
}

export default MyApp
