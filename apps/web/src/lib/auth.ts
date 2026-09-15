export type Role = 'DISPATCHER' | 'HOSPITAL' | 'AMBULANCE_CREW' | 'DEMO_CONTROLLER'

export type AuthContext = {
  token: string
  role: Role | null
  roles: Role[]
  demoFallback: boolean
}

const ROLE_ALIASES: Record<string, Role> = {
  dispatcher: 'DISPATCHER',
  hospital: 'HOSPITAL',
  ambulance: 'AMBULANCE_CREW',
  ambulance_crew: 'AMBULANCE_CREW',
  crew: 'AMBULANCE_CREW',
  demo: 'DEMO_CONTROLLER',
  demo_controller: 'DEMO_CONTROLLER',
}

function decodePayload(token: string): Record<string, unknown> | null {
  try {
    const payload = token.split('.')[1]
    if (!payload) return null
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '='))) as Record<string, unknown>
  } catch {
    return null
  }
}

function normalizeRoles(value: unknown): Role[] {
  const values = Array.isArray(value) ? value : typeof value === 'string' ? [value] : []
  return values.flatMap((item) => {
    if (typeof item !== 'string') return []
    const role = ROLE_ALIASES[item.toLowerCase()]
    return role ? [role] : []
  })
}

export function getAuthContext(token: string | null): AuthContext | null {
  if (!token) return null
  const payload = decodePayload(token)
  const roles = normalizeRoles(payload?.roles ?? payload?.role ?? payload?.user_role)
  return { token, role: roles[0] ?? null, roles, demoFallback: roles.length === 0 }
}

export function rolePath(role: Role | null): string {
  if (role === 'HOSPITAL') return '/hospital'
  if (role === 'AMBULANCE_CREW') return '/ambulance'
  if (role === 'DEMO_CONTROLLER') return '/demo'
  return '/dispatch'
}
