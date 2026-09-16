export type DataMode = 'SIMULATED' | 'LIVE' | 'REPLAY' | 'UNKNOWN'
export type ViewState = 'idle' | 'loading' | 'success' | 'error' | 'stale'

export interface Incident { id: string; incident_code: string; incident_type: string; severity: string; latitude: number; longitude: number; address_text?: string | null; patient_count: number; notes?: string | null; data_mode: DataMode }
export interface Candidate { code: string; ambulance_id?: string; score: number | null; rank: number | null; eligible: boolean; reasons: string[]; eta_s?: number; equipment?: string[]; data_mode?: DataMode; age_s?: number }
export interface HospitalCandidate extends Candidate { hospital_id?: string; resources?: Record<string, number | null> }
export interface RouteResult { id: string; incident_id: string; provider: string; distance_m: number; duration_seconds: number; traffic_duration_seconds: number; confidence: number; fallback_used: boolean }
export interface AcceptanceRequest { id: string; incident_id: string; hospital_id: string; status: string; state_version?: number; data_mode?: DataMode }
export interface Mission { id: string; incident_id: string; status: string; state_version: number; destination?: { code?: string; name?: string } | null; data_mode?: DataMode; updated_at?: string }
export interface ResourceSnapshot { code?: string; resource_type?: string; total?: number | null; total_capacity?: number | null; available?: number | null; available_capacity?: number | null; reserved?: number | null; reserved_capacity?: number | null; updated_at?: string; last_updated_at?: string; data_mode?: DataMode }
export interface AmbulanceRecord { id: string; ambulance_code: string; vehicle_type: string; status: string; latitude?: number | null; longitude?: number | null; gps_updated_at?: string | null; crew_summary?: Record<string, string> | null; data_mode: DataMode; version: number }
export interface HospitalRecord { id: string; hospital_code: string; name: string; latitude: number; longitude: number; status: string; emergency_capable: boolean; data_mode: DataMode; capabilities?: { code: string; status: string }[]; resources?: ResourceSnapshot[] }
export interface AlertRecord { id: string; incident_id?: string | null; type: string; severity: string; message: string; payload: Record<string, unknown>; created_at: string; status: string; data_mode: DataMode }
export interface GeoPoint { lat: number; lng: number }
export type GpsState = 'FRESH' | 'STALE' | 'UNKNOWN'
export interface CrewMission { id: string; mission_code: string; status: string; state_version: number; active_leg: 'TO_PATIENT' | 'TO_HOSPITAL'; next_states: string[]; data_mode: DataMode }
export interface CrewIncident { id: string; incident_code: string; incident_type: string; severity: string; address_text?: string | null; patient_count: number; point: GeoPoint | null; requirements: { code: string; level: string }[] }
export interface CrewAmbulance { id: string; ambulance_code: string; status: string; point: GeoPoint | null; gps_age_s: number | null; gps_stale: boolean | null; gps_state: GpsState }
export interface CrewDestination { id: string; hospital_code: string; name: string; point: GeoPoint | null }
export interface CrewRoute { id: string; distance_m: number; duration_seconds: number; traffic_duration_seconds: number; confidence: number; provider: string; geometry: GeoPoint[]; data_mode: DataMode }
export interface CrewView { mission: CrewMission; assignment: { id: string; status: string } | null; incident: CrewIncident | null; ambulance: CrewAmbulance | null; destination: CrewDestination | null; acceptance: { id: string; status: string } | null; reservations: { id: string; status: string; resource_type: string | null }[]; route: CrewRoute | null }
export interface RouteOption { variant: string; label: string; distance_m: number; duration_seconds: number; traffic_duration_seconds: number; confidence: number; provider: string; data_mode: DataMode; geometry: GeoPoint[]; route_id?: string }
export interface RouteComparison { mission_id: string; active_leg: string; current: RouteOption | null; alternatives: RouteOption[]; recommended_variant: string | null; saving_seconds: number | null; significant: boolean; threshold_seconds: number; data_mode: DataMode }
export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

const TOKEN_KEY = 'conclave_access_token'
async function request<T>(path: string, init?: RequestInit): Promise<T> { const headers = new Headers(init?.headers); headers.set('Content-Type', 'application/json'); const token = api.getToken(); if (token) headers.set('Authorization', `Bearer ${token}`); const response = await fetch(`/api/v1${path}`, { ...init, headers }); const body = await response.json().catch(() => null) as { detail?: string; message?: string; error?: { message?: string } } | null; if (response.status === 401) { api.clearToken(); window.dispatchEvent(new Event('conclave:auth-expired')) } if (!response.ok) throw new ApiError(response.status, body?.error?.message ?? body?.detail ?? body?.message ?? `Request failed (${response.status})`); return body as T }
function idempotencyKey() { return `web-${crypto.randomUUID()}` }

export const api = {
  getToken: () => window.localStorage.getItem(TOKEN_KEY),
  setToken: (token: string) => window.localStorage.setItem(TOKEN_KEY, token),
  clearToken: () => window.localStorage.removeItem(TOKEN_KEY),
  login: (email: string, password: string) => request<{ access_token: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  createIncident: (payload: { incident_type: string; severity: string; latitude: number; longitude: number; address_text: string; patient_count: number; notes: string }) => request<Incident>('/incidents', { method: 'POST', body: JSON.stringify(payload) }),
  addRequirement: (incidentId: string, code: string) => request<{ id: string }>(`/incidents/${incidentId}/requirements`, { method: 'POST', body: JSON.stringify({ code, level: 'REQUIRED' }) }),
  matchAmbulances: (incidentId: string) => request<Candidate[]>('/dispatch/ambulances/match', { method: 'POST', body: JSON.stringify({ incident_id: incidentId }) }),
  confirmAmbulance: (ambulanceId: string, incidentId: string) => request<{ id: string }>('/dispatch/ambulances/' + ambulanceId + '/confirm', { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() }, body: JSON.stringify({ incident_id: incidentId }) }),
  matchHospitals: (incidentId: string) => request<HospitalCandidate[]>('/dispatch/hospitals/match', { method: 'POST', body: JSON.stringify({ incident_id: incidentId }) }),
  calculateRoute: (incidentId: string, hospitalId?: string) => request<RouteResult>('/routes/calculate', { method: 'POST', body: JSON.stringify({ incident_id: incidentId, hospital_id: hospitalId }) }),
  me: () => request<{ id: string; name: string; email: string; roles: string[] }>('/auth/me'),
  createAcceptance: (incidentId: string, hospitalId: string) => request<AcceptanceRequest>('/acceptance-requests', { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() }, body: JSON.stringify({ incident_id: incidentId, hospital_id: hospitalId }) }),
  acceptAcceptance: (requestId: string) => request<AcceptanceRequest>(`/acceptance-requests/${requestId}/accept`, { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() } }),
  rejectAcceptance: (requestId: string, reason: string) => request<AcceptanceRequest>(`/acceptance-requests/${requestId}/reject`, { method: 'POST', headers: { 'Idempotency-Key': idempotencyKey() }, body: JSON.stringify({ reason }) }),
  mission: (missionId: string) => request<Mission>(`/missions/${missionId}`),
  patchMission: (missionId: string, status: string, stateVersion: number) => request<Mission>(`/missions/${missionId}`, { method: 'PATCH', body: JSON.stringify({ status, state_version: stateVersion }) }),
  resources: (hospitalId: string) => request<ResourceSnapshot[]>(`/hospitals/${hospitalId}/resources`),
  simulation: (action: string) => {
    const paths: Record<string, string> = {
      RESET_SCENARIO: 'reset',
      TRAFFIC_CHANGE: 'traffic-change',
      HOSPITAL_REJECT: 'hospital-reject',
      RESOURCE_LOSS: 'resource-lost',
      RECONNECT_STREAM: 'heartbeat',
    }
    return request<{ mode: string }>(`/admin/simulation/${paths[action] ?? action}`, { method: 'POST', body: JSON.stringify({}) })
  },
  missions: () => request<Mission[]>('/missions'),
  crewView: (missionId: string) => request<CrewView>(`/missions/${missionId}/crew-view`),
  routeOptions: (missionId: string) => request<RouteComparison>(`/missions/${missionId}/route-options`),
  reroute: (missionId: string, variant: string, stateVersion: number) => request<{ mission_id: string; state_version: number; applied: RouteOption }>(`/missions/${missionId}/reroute`, { method: 'POST', body: JSON.stringify({ variant, state_version: stateVersion }) }),
  acceptAssignment: (assignmentId: string) => request<{ id: string; status: string }>(`/ambulance-assignments/${assignmentId}/accept`, { method: 'POST' }),
  rejectAssignment: (assignmentId: string) => request<{ id: string; status: string }>(`/ambulance-assignments/${assignmentId}/reject`, { method: 'POST' }),
  updateAmbulanceLocation: (ambulanceId: string, lat: number, lng: number) => request<AmbulanceRecord>(`/ambulances/${ambulanceId}/location`, { method: 'POST', body: JSON.stringify({ latitude: lat, longitude: lng }) }),
  ambulances: () => request<AmbulanceRecord[]>('/ambulances'),
  hospitals: () => request<HospitalRecord[]>('/hospitals'),
  getHospital: (hospitalId: string) => request<HospitalRecord>(`/hospitals/${hospitalId}`),
  alerts: () => request<AlertRecord[]>('/alerts/active'),
}
