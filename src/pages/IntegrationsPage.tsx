import {
  Plug,
  ExternalLink,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Database,
  MessageSquare,
  Bell,
  BarChart3,
  FileText,
  Shield,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

interface Integration {
  name: string
  description: string
  status: 'Connected' | 'Planned' | 'Coming Soon'
  icon: LucideIcon
  category: string
  details: string
}

const integrations: Integration[] = [
  {
    name: 'In-App Knowledge Base',
    description: 'Searchable runbooks, diagnostic playbooks, and resolution history',
    status: 'Connected',
    icon: FileText,
    category: 'Knowledge',
    details: '4 articles indexed • Auto-correlated with case symptoms',
  },
  {
    name: 'Deterministic Diagnostic Engine',
    description: 'Safe, read-only queries against synthetic databases and log stores',
    status: 'Connected',
    icon: Database,
    category: 'Diagnostics',
    details: '5 diagnostic tools available • Results appended to evidence timeline',
  },
  {
    name: 'Google Gemini AI',
    description: 'Intelligent intake parsing, root-cause investigation, handoff generation, and case Q&A',
    status: 'Connected',
    icon: Shield,
    category: 'AI',
    details: 'Gemini 2.5 Flash • Deterministic fallback when API key is absent',
  },
  {
    name: 'Jira',
    description: 'Sync engineering tickets and bug reports bidirectionally',
    status: 'Planned',
    icon: FileText,
    category: 'Ticketing',
    details: 'Create JIRA issues from Engineering Handoffs • Sync resolution status',
  },
  {
    name: 'Slack',
    description: 'Real-time alerts for severity escalations and customer updates',
    status: 'Planned',
    icon: MessageSquare,
    category: 'Notifications',
    details: 'Channel notifications on case state changes • DM approvals for handoff sign-off',
  },
  {
    name: 'PagerDuty',
    description: 'Correlate active incidents with customer-reported cases',
    status: 'Planned',
    icon: Bell,
    category: 'Incident Management',
    details: 'Auto-link PagerDuty incidents to case evidence timeline',
  },
  {
    name: 'Datadog',
    description: 'Pull application metrics, APM traces, and error logs into case evidence',
    status: 'Coming Soon',
    icon: BarChart3,
    category: 'Observability',
    details: 'Log search by trace ID • Metric correlation dashboards',
  },
  {
    name: 'Salesforce Service Cloud',
    description: 'Import customer support tickets and account context from Salesforce',
    status: 'Coming Soon',
    icon: Plug,
    category: 'CRM',
    details: 'Case sync • Account history • SLA tracking from Salesforce objects',
  },
]

const statusConfig = {
  Connected: {
    icon: CheckCircle2,
    className: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    dotColor: 'bg-emerald-500',
  },
  Planned: {
    icon: Clock,
    className: 'bg-blue-50 text-blue-700 border-blue-200',
    dotColor: 'bg-blue-400',
  },
  'Coming Soon': {
    icon: AlertTriangle,
    className: 'bg-slate-50 text-slate-500 border-slate-200',
    dotColor: 'bg-slate-400',
  },
}

export function IntegrationsPage() {
  const connectedCount = integrations.filter((i) => i.status === 'Connected').length
  const plannedCount = integrations.filter((i) => i.status !== 'Connected').length

  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-slate-100 flex items-center justify-center">
            <Plug className="h-5 w-5 text-slate-600" />
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">Integrations</h1>
            <p className="text-sm text-slate-500 mt-0.5">
              Connected services and planned platform integrations
            </p>
          </div>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div className="rounded-xl border border-emerald-200 bg-emerald-50/50 p-4 flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 text-emerald-600" />
          <div>
            <p className="text-lg font-bold text-emerald-900">{connectedCount}</p>
            <p className="text-[11px] text-emerald-700 font-medium">Active Integrations</p>
          </div>
        </div>
        <div className="rounded-xl border border-blue-200 bg-blue-50/50 p-4 flex items-center gap-3">
          <Clock className="h-5 w-5 text-blue-600" />
          <div>
            <p className="text-lg font-bold text-blue-900">{plannedCount}</p>
            <p className="text-[11px] text-blue-700 font-medium">Planned / Coming Soon</p>
          </div>
        </div>
        <div className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 flex items-center gap-3">
          <Database className="h-5 w-5 text-slate-500" />
          <div>
            <p className="text-lg font-bold text-slate-900">{integrations.length}</p>
            <p className="text-[11px] text-slate-600 font-medium">Total Integration Slots</p>
          </div>
        </div>
      </div>

      {/* Demo Notice */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 mb-6">
        <p className="text-sm text-amber-800">
          <strong>Demo mode:</strong> Active integrations use in-app synthetic data and the built-in knowledge base.
          Planned integrations show the interface design — real API connections require configuration and credentials.
        </p>
      </div>

      {/* Integration Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {integrations.map((integration) => {
          const statusCfg = statusConfig[integration.status]
          const StatusIcon = statusCfg.icon

          return (
            <div
              key={integration.name}
              className={`rounded-xl border bg-white p-5 flex items-start gap-4 transition-colors ${
                integration.status === 'Connected'
                  ? 'border-emerald-200/80 hover:border-emerald-300'
                  : 'border-slate-200 hover:border-slate-300'
              }`}
            >
              <div className={`rounded-lg p-2.5 ${
                integration.status === 'Connected' ? 'bg-emerald-50' : 'bg-slate-100'
              }`}>
                <integration.icon className={`h-5 w-5 ${
                  integration.status === 'Connected' ? 'text-emerald-600' : 'text-slate-400'
                }`} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="text-sm font-semibold text-slate-900">{integration.name}</h3>
                  <span className={`text-[10px] font-semibold px-2 py-0.5 rounded-full border ${statusCfg.className}`}>
                    <span className="flex items-center gap-1">
                      <StatusIcon className="h-2.5 w-2.5" />
                      {integration.status}
                    </span>
                  </span>
                </div>
                <p className="text-xs text-slate-500">{integration.description}</p>
                <p className="text-[11px] text-slate-400 mt-1.5 font-medium">{integration.details}</p>
                <span className="inline-block mt-1.5 text-[10px] font-medium text-slate-400 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                  {integration.category}
                </span>
              </div>
              <ExternalLink className="h-4 w-4 text-slate-300 mt-0.5 shrink-0" />
            </div>
          )
        })}
      </div>
    </div>
  )
}
