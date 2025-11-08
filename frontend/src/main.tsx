import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import './styles/global.css'

// Performance monitoring
if (import.meta.env.MODE === 'development') {
  import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
    getCLS(console.log)
    getFID(console.log)
    getFCP(console.log)
    getLCP(console.log)
    getTTFB(console.log)
  })
}

// Error boundary for better error handling
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('='.repeat(80))
    console.error('APPLICATION ERROR CAUGHT BY ERROR BOUNDARY')
    console.error('='.repeat(80))
    console.error('Error:', error)
    console.error('Error Message:', error.message)
    console.error('Error Stack:', error.stack)
    console.error('Component Stack:', errorInfo.componentStack)
    console.error('='.repeat(80))
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          backgroundColor: '#0a0a0a',
          color: '#ff6b6b',
          fontFamily: 'monospace',
          padding: '20px'
        }}>
          <div style={{ maxWidth: '800px', width: '100%' }}>
            <h2>🚨 Application Error</h2>
            <p>Something went wrong. Please check the console for details or refresh the page.</p>

            {this.state.error && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                backgroundColor: 'rgba(255, 107, 107, 0.1)',
                border: '1px solid #ff6b6b',
                borderRadius: '5px',
                fontSize: '14px',
                maxHeight: '300px',
                overflow: 'auto'
              }}>
                <h3 style={{ marginTop: 0, fontSize: '16px' }}>Error Details:</h3>
                <p><strong>Message:</strong> {this.state.error.message}</p>
                <details>
                  <summary style={{ cursor: 'pointer', marginTop: '10px' }}>Stack Trace</summary>
                  <pre style={{
                    marginTop: '10px',
                    padding: '10px',
                    backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    borderRadius: '3px',
                    fontSize: '12px',
                    overflow: 'auto'
                  }}>
                    {this.state.error.stack}
                  </pre>
                </details>
              </div>
            )}

            <button
              onClick={() => window.location.reload()}
              style={{
                marginTop: '20px',
                padding: '10px 20px',
                backgroundColor: '#ff6b6b',
                color: 'white',
                border: 'none',
                borderRadius: '5px',
                cursor: 'pointer',
                fontSize: '16px'
              }}
            >
              Reload Page
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Remove loading spinner once app loads
const removeLoadingSpinner = () => {
  const loadingContainer = document.getElementById('loading-container')
  if (loadingContainer) {
    loadingContainer.style.opacity = '0'
    setTimeout(() => {
      loadingContainer.remove()
      document.body.classList.add('loaded')
    }, 500)
  }
}

const root = ReactDOM.createRoot(document.getElementById('root')!)

root.render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
)

// Remove loading spinner after a short delay to ensure smooth transition
setTimeout(removeLoadingSpinner, 100)