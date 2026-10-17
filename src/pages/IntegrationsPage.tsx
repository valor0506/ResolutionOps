import { Plug, ExternalLink } from 'lucide-react'

const futureIntegrations = [
  { name: 'Jira', description: 'Sync engineering tickets and bug reports', status: 'Planned' },
  { name: 'Slack', description: 'Receive alerts and send customer updates', status: 'Planned' },
  { name: 'PagerDuty', description: 'Correlate incidents with active cases', status: 'Planned' },
  { name: 'Datadog', description: 'Pull application logs and metrics', status: 'Planned' },
]

export function IntegrationsPage() {
  return (
    <div className="p-8 max-w-7xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Integrations</h1>
        <p className="text-sm text-slate-500 mt-1">
          Connect external tools — currently using in-app synthetic data
        </p>
      </div>

      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 mb-6">
        <p className="text-sm text-amber-800">
          <strong>Demo mode:</strong> The initial version uses synthetic data and an in-app knowledge base.
          Integration interfaces are designed so real services can be added later.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {futureIntegrations.map((integration) => (
          <div
            key={integration.name}
            className="rounded-xl border border-slate-200 bg-white p-5 flex items-start gap-4"
          >
            <div className="rounded-lg bg-slate-100 p-2.5">
              <Plug className="h-5 w-5 text-slate-400" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold text-slate-900">{integration.name}</h3>
                <span className="text-[11px] font-medium text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                  {integration.status}
                </span>
              </div>
              <p className="text-xs text-slate-500 mt-1">{integration.description}</p>
            </div>
            <ExternalLink className="h-4 w-4 text-slate-300 mt-0.5" />
          </div>
        ))}
      </div>
    </div>
  )
}
