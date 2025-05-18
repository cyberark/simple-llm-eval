import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import SummaryReport from './components/SummaryReport.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SummaryReport />
  </StrictMode>,
)
