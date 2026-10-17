import { User, Bell, Shield, Database } from 'lucide-react'

const settingSections = [
  { name: 'Profile', description: 'Your account and role settings', icon: User },
  { name: 'Notifications', description: 'Alert preferences and channels', icon: Bell },
  { name: 'Security', description: 'Authentication, roles, and audit log', icon: Shield },
  { name: 'Data & Storage', description: 'Firestore connection and seed data', icon: Database },
]

export function SettingsPage() {
  return (
    <div className="p-8 max-w-3xl">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">
          Application configuration and user preferences
        </p>
      </div>

      <div className="space-y-3">
        {settingSections.map((section) => (
          <div
            key={section.name}
            className="rounded-xl border border-slate-200 bg-white p-5 flex items-center gap-4 hover:border-slate-300 transition-colors cursor-pointer"
          >
            <div className="rounded-lg bg-slate-100 p-2.5">
              <section.icon className="h-5 w-5 text-slate-500" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-slate-900">{section.name}</h3>
              <p className="text-xs text-slate-500 mt-0.5">{section.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
