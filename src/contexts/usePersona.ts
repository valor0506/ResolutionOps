import { createContext, useContext } from 'react'
import type { DemoPersona } from '../types/domain'

export interface PersonaContextValue {
  persona: DemoPersona | null
  permissions: string[]
  roleDisplay: string
  loading: boolean
  switchPersona: (personaId: string) => Promise<void>
  hasPermission: (permission: string) => boolean
}

export const PersonaContext = createContext<PersonaContextValue>({
  persona: null,
  permissions: [],
  roleDisplay: '',
  loading: true,
  switchPersona: async () => {},
  hasPermission: () => false,
})

export function usePersona() {
  return useContext(PersonaContext)
}
