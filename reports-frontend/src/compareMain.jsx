import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import CompareReport from './components/CompareReport.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <CompareReport />
  </StrictMode>,
)
