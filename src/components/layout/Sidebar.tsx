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
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

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

export function Sidebar() {
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

      {/* User area — placeholder until auth */}
      <div className="px-3 py-4 border-t border-slate-800/60">
        <div className="flex items-center gap-3 px-3 py-2">
          <div className="h-8 w-8 rounded-full bg-slate-700/60 flex items-center justify-center text-xs font-medium text-slate-400">
            ?
          </div>
          <div>
            <p className="text-[13px] text-slate-400 font-medium">Sign in</p>
            <p className="text-[11px] text-slate-600">Not authenticated</p>
          </div>
        </div>
      </div>
    </aside>
  )
}
