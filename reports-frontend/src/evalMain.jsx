import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import LLMEvalReport from './components/LLMEvalReport.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <LLMEvalReport />
  </StrictMode>,
)
