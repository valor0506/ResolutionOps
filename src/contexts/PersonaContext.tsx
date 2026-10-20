import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import { apiFetch } from '../lib/api'
import type { DemoPersona, CurrentPersonaResponse } from '../types/domain'
import { PersonaContext } from './usePersona'

export function PersonaProvider({ children }: { children: ReactNode }) {
  const [persona, setPersona] = useState<DemoPersona | null>(null)
  const [permissions, setPermissions] = useState<string[]>([])
  const [roleDisplay, setRoleDisplay] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let ignore = false
    apiFetch<CurrentPersonaResponse>('/auth/me')
      .then((data) => {
        if (!ignore) {
          setPersona(data.persona)
          setPermissions(data.permissions)
          setRoleDisplay(data.role_display)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!ignore) setLoading(false)
      })
    return () => {
      ignore = true
    }
  }, [])

  const switchPersona = async (personaId: string) => {
    const data = await apiFetch<CurrentPersonaResponse>(`/auth/switch/${personaId}`, {
      method: 'POST',
    })
    setPersona(data.persona)
    setPermissions(data.permissions)
    setRoleDisplay(data.role_display)
  }

  const hasPermission = (permission: string) => permissions.includes(permission)

  return (
    <PersonaContext.Provider value={{ persona, permissions, roleDisplay, loading, switchPersona, hasPermission }}>
      {children}
    </PersonaContext.Provider>
  )
}
