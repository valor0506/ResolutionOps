import { Routes, Route } from 'react-router-dom'
import { AppLayout } from './components/layout/AppLayout'
import { OverviewPage } from './pages/OverviewPage'
import { CasesPage } from './pages/CasesPage'
import { CaseDetailPage } from './pages/CaseDetailPage'
import { CustomersPage } from './pages/CustomersPage'
import { KnowledgeBasePage } from './pages/KnowledgeBasePage'
import { IntegrationsPage } from './pages/IntegrationsPage'
import { ReportsPage } from './pages/ReportsPage'
import { SettingsPage } from './pages/SettingsPage'

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route index element={<OverviewPage />} />
        <Route path="cases" element={<CasesPage />} />
        <Route path="cases/:caseId" element={<CaseDetailPage />} />
        <Route path="customers" element={<CustomersPage />} />
        <Route path="knowledge-base" element={<KnowledgeBasePage />} />
        <Route path="integrations" element={<IntegrationsPage />} />
        <Route path="reports" element={<ReportsPage />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
    </Routes>
  )
}
