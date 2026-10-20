import { useState, useEffect } from 'react'
import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  FolderOpen,
  Users,
  BookOpen,
  Plug,
  BarChart3,
  Settings,
  Shield,
  ChevronDown,
  Check,
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'
import { usePersona } from '../../contexts/usePersona'
import { apiFetch } from '../../lib/api'
import type { PersonaListResponse, DemoPersona } from '../../types/domain'

interface NavItem {
  name: string
  href: string
  icon: LucideIcon
}

const navigation: NavItem[] = [
  { name: 'Overview', href: '/', icon: LayoutDashboard },
  { name: 'Cases', href: '/cases', icon: FolderOpen },
  { name: 'Customers', href: '/customers', icon: Users },
  { name: 'Knowledge Base', href: '/knowledge-base', icon: BookOpen },
  { name: 'Integrations', href: '/integrations', icon: Plug },
  { name: 'Reports', href: '/reports', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]

const roleColors: Record<string, string> = {
  support_engineer: 'bg-blue-500/20 text-blue-400 border-blue-500/30',
  support_lead: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  platform_engineer: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
}

export function Sidebar() {
  const { persona, roleDisplay, switchPersona } = usePersona()
  const [showSwitcher, setShowSwitcher] = useState(false)
  const [allPersonas, setAllPersonas] = useState<DemoPersona[]>([])

  useEffect(() => {
    let ignore = false
    apiFetch<PersonaListResponse>('/auth/personas')
      .then((data) => {
        if (!ignore) setAllPersonas(data.personas)
      })
      .catch(() => {})
    return () => {
      ignore = true
    }
  }, [])

  const handleSwitch = async (personaId: string) => {
    await switchPersona(personaId)
    setShowSwitcher(false)
  }

  return (
    <aside className="flex flex-col w-60 bg-[#0c1222] text-slate-300 min-h-screen border-r border-slate-800">
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-5 h-16 border-b border-slate-800/60">
        <Shield className="h-7 w-7 text-blue-400 shrink-0" />
        <span className="text-[15px] font-semibold text-white tracking-tight">
          ResolutionOps
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            end={item.href === '/'}
            className={({ isActive }) =>
              [
                'flex items-center gap-3 px-3 py-2 rounded-lg text-[13px] font-medium transition-colors',
                isActive
                  ? 'bg-slate-800/80 text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40',
              ].join(' ')
            }
          >
            <item.icon className="h-[18px] w-[18px] shrink-0" />
            {item.name}
          </NavLink>
        ))}
      </nav>

      {/* Demo Persona Switcher */}
      <div className="px-3 py-4 border-t border-slate-800/60 relative">
        <button
          onClick={() => setShowSwitcher(!showSwitcher)}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800/40 transition-colors"
        >
          <div className="h-8 w-8 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-xs font-bold text-white shrink-0">
            {persona?.avatar_initials ?? '?'}
          </div>
          <div className="flex-1 text-left min-w-0">
            <p className="text-[13px] text-white font-medium truncate">
              {persona?.display_name ?? 'Loading...'}
            </p>
            <p className="text-[11px] text-slate-500 truncate">
              {roleDisplay || 'Not authenticated'}
            </p>
          </div>
          <ChevronDown className={`h-3.5 w-3.5 text-slate-500 transition-transform ${showSwitcher ? 'rotate-180' : ''}`} />
        </button>

        {/* Persona Dropdown */}
        {showSwitcher && (
          <div className="absolute bottom-full left-3 right-3 mb-2 bg-[#151d30] border border-slate-700 rounded-xl shadow-xl z-50 overflow-hidden">
            <div className="px-3 py-2 border-b border-slate-700/60">
              <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-500">
                Demo Role Switcher
              </p>
            </div>
            {allPersonas.map((p) => (
              <button
                key={p.id}
                onClick={() => handleSwitch(p.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 text-left transition-colors ${
                  persona?.id === p.id ? 'bg-slate-800/60' : 'hover:bg-slate-800/30'
                }`}
              >
                <div className="h-7 w-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-[10px] font-bold text-white shrink-0">
                  {p.avatar_initials}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-[12px] text-white font-medium truncate">{p.display_name}</p>
                  <span className={`inline-block text-[9px] font-semibold px-1.5 py-0.5 rounded border mt-0.5 ${roleColors[p.role] ?? 'text-slate-400'}`}>
                    {p.role.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                {persona?.id === p.id && (
                  <Check className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                )}
              </button>
            ))}
          </div>
        )}
      </div>
    </aside>
  )
}
