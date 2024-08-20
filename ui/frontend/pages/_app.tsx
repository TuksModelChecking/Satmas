import type { AppProps } from 'next/app'
import { ReactFlowProvider } from '@xyflow/react'

import '../styles/globals.css'

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ReactFlowProvider>
      <Component {...pageProps} />
    </ReactFlowProvider>
  )
}

export default MyApp
