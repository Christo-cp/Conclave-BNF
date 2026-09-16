import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Link, useLocation } from 'react-router'
import { Ambulance, AlertTriangle, ArrowRight, Check, CircleDot, Clock3, Hospital, MapPin, RefreshCw, Route, Siren, Wifi, WifiOff, X } from 'lucide-react'
import { api, ApiError, type CrewView, type GeoPoint, type RouteComparison, type RouteOption } from './lib/api'
import { MissionMap } from './components/mission-map'
import { RealtimeClient, realtimeUrl } from './lib/realtime'
import './CrewScreens.css'

const CACHE_KEY = 'conclave_crew_view'

type Connection = 'LIVE' | 'DEGRADED'

const STATE_LABELS: Record<string, string> = {
  EN_ROUTE_TO_PATIENT: 'START NAVIGATION',
  ON_SCENE: 'ARRIVED AT INCIDENT',
  PATIENT_ON_BOARD: 'CONFIRM PATIENT PICKUP',
  EN_ROUTE_TO_HOSPITAL: 'DEPART FOR HOSPITAL',
  ARRIVED: 'ARRIVED AT HOSPITAL',
  HANDOVER: 'BEGIN HANDOVER',
  COMPLETED: 'COMPLETE MISSION',
}

const TABS = [
  { path: '/ambulance', label: 'Overview' },
  { path: '/ambulance/mission', label: 'Mission' },
  { path: '/ambulance/navigation', label: 'Navigation' },
  { path: '/ambulance/patient', label: 'Patient' },
  { path: '/ambulance/hospital', label: 'Hospital' },
]

function readCache(): CrewView | null {
  try { const raw = window.localStorage.getItem(CACHE_KEY); return raw ? (JSON.parse(raw) as CrewView) : null } catch { return null }
}

function writeCache(view: CrewView) {
  try { window.localStorage.setItem(CACHE_KEY, JSON.stringify(view)) } catch { /* private mode or blocked storage is non-fatal */ }
}

function minutes(seconds: number | null | undefined) {
  return seconds == null ? null : Math.round(seconds / 60)
}

function GpsChip({ view }: { view: CrewView }) {
  const gps = view.ambulance?.gps_state ?? 'UNKNOWN'
  const age = view.ambulance?.gps_age_s
  if (gps === 'FRESH') return <span className="crew-chip ok"><CircleDot size={13} /> GPS FRESH{age != null && ` · ${Math.round(age)}s`}</span>
  if (gps === 'STALE') return <span className="crew-chip warn"><AlertTriangle size={13} /> GPS STALE{age != null && ` · ${Math.round(age)}s`}</span>
  return <span className="crew-chip unknown"><AlertTriangle size={13} /> GPS UNKNOWN</span>
}

export function CrewWorkspace() {
  const location = useLocation()
  const [view, setView] = useState<CrewView | null>(null)
  const [missionId, setMissionId] = useState<string | null>(null)
  const [options, setOptions] = useState<RouteComparison | null>(null)
  const [connection, setConnection] = useState<Connection>('LIVE')
  const [fromCache, setFromCache] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [ticking, setTicking] = useState(false)
  const tickIndex = useRef(0)

  const load = useCallback(async (id?: string) => {
    try {
      let target = id ?? missionId
      if (!target) {
        const missions = await api.missions()
        if (missions.length === 0) { setError('No mission is assigned to this ambulance.'); setConnection('LIVE'); return }
        target = missions[0].id
        setMissionId(target)
      }
      const next = await api.crewView(target)
      setView(next); writeCache(next); setFromCache(false); setConnection('LIVE'); setError(null)
    } catch (cause) {
      const cached = readCache()
      if (cached) { setView(cached); setFromCache(true) }
      setConnection('DEGRADED')
      setError(cause instanceof ApiError ? cause.message : 'The command service could not be reached.')
    }
  }, [missionId])

  useEffect(() => { void load() }, [load])

  useEffect(() => {
    const token = api.getToken(); const ambulanceId = view?.ambulance?.id
    if (!token || !ambulanceId) return
    const client = new RealtimeClient(realtimeUrl(token), () => { void load() }, async () => { await load() }, [`ambulance:${ambulanceId}`])
    client.connect()
    return () => client.stop()
  }, [view?.ambulance?.id, load])

  const refreshOptions = useCallback(async () => {
    if (!missionId) return
    try { setOptions(await api.routeOptions(missionId)) } catch { setOptions(null) }
  }, [missionId])

  useEffect(() => { void refreshOptions() }, [refreshOptions, view?.mission.state_version, view?.route?.id])

  const geometry = useMemo<GeoPoint[]>(() => view?.route?.geometry ?? options?.current?.geometry ?? [], [view?.route?.geometry, options?.current?.geometry])
  const alternative = useMemo<GeoPoint[] | null>(() => {
    if (!options?.recommended_variant) return null
    return options.alternatives.find((item) => item.variant === options.recommended_variant)?.geometry ?? null
  }, [options])

  async function advance(target: string) {
    if (!view) return
    setBusy(true)
    try { await api.patchMission(view.mission.id, target, view.mission.state_version); await load() } catch (cause) { setError(cause instanceof ApiError ? cause.message : 'The mission state could not be updated.') } finally { setBusy(false) }
  }

  async function respond(accepted: boolean) {
    if (!view?.assignment) return
    setBusy(true)
    try {
      if (accepted) await api.acceptAssignment(view.assignment.id)
      else await api.rejectAssignment(view.assignment.id)
      await load()
    } catch (cause) { setError(cause instanceof ApiError ? cause.message : 'The assignment response could not be recorded.') } finally { setBusy(false) }
  }

  async function applyReroute(option: RouteOption) {
    if (!view) return
    setBusy(true)
    try { await api.reroute(view.mission.id, option.variant, view.mission.state_version); await load(); await refreshOptions() } catch (cause) { setError(cause instanceof ApiError ? cause.message : 'The reroute could not be applied.') } finally { setBusy(false) }
  }

  useEffect(() => {
    if (!ticking || !view?.ambulance?.id || geometry.length === 0) return
    const ambulanceId = view.ambulance.id
    const timer = window.setInterval(() => {
      tickIndex.current = (tickIndex.current + 1) % geometry.length
      const point = geometry[tickIndex.current]
      void api.updateAmbulanceLocation(ambulanceId, point.lat, point.lng).catch(() => setConnection('DEGRADED'))
    }, 3000)
    return () => window.clearInterval(timer)
  }, [ticking, view?.ambulance?.id, geometry])

  if (!view) {
    return <div className="crew-shell"><div className="crew-empty"><Ambulance size={30} /><h2>No mission loaded</h2><p>{error ?? 'Loading the assigned mission from the command service.'}</p><button className="crew-button" type="button" onClick={() => void load()}><RefreshCw size={15} /> RETRY</button></div></div>
  }

  const panel = TABS.some((tab) => tab.path === location.pathname) ? location.pathname : '/ambulance'

  return (
    <div className="crew-shell">
      <header className="crew-header">
        <div>
          <div className="crew-eyebrow"><Siren size={13} /> {view.incident?.incident_type ?? 'MISSION'} · {view.incident?.severity ?? 'SEVERITY UNKNOWN'}</div>
          <h1>{view.mission.mission_code}</h1>
          <p>{view.mission.status.replaceAll('_', ' ')} · leg {view.mission.active_leg.replaceAll('_', ' ').toLowerCase()}</p>
        </div>
        <div className="crew-header-meta">
          <span className={`crew-chip ${connection === 'LIVE' ? 'ok' : 'warn'}`}>{connection === 'LIVE' ? <><Wifi size={13} /> LIVE</> : <><WifiOff size={13} /> CONNECTION DEGRADED</>}</span>
          <GpsChip view={view} />
          <span className="crew-chip simulated"><CircleDot size={13} /> {view.mission.data_mode}</span>
        </div>
      </header>

      {fromCache && <div className="crew-banner warn" role="status"><WifiOff size={16} /> Showing the last confirmed mission from this device. Verify when the connection returns.</div>}
      {error && <div className="crew-banner error" role="alert"><AlertTriangle size={16} /> <span>{error}</span><button type="button" onClick={() => setError(null)} aria-label="Dismiss"><X size={14} /></button></div>}

      <nav className="crew-tabs" aria-label="Crew screens">
        {TABS.map((tab) => <Link key={tab.path} to={tab.path} className={`crew-tab ${panel === tab.path ? 'active' : ''}`}>{tab.label}</Link>)}
      </nav>

      {panel === '/ambulance' && <OverviewPanel view={view} busy={busy} onRespond={respond} onAdvance={advance} />}
      {panel === '/ambulance/mission' && <MissionPanel view={view} />}
      {panel === '/ambulance/navigation' && <NavigationPanel view={view} geometry={geometry} alternative={alternative} options={options} busy={busy} ticking={ticking} onTick={setTicking} onAdvance={advance} onReroute={applyReroute} />}
      {panel === '/ambulance/patient' && <PatientPanel view={view} busy={busy} onAdvance={advance} />}
      {panel === '/ambulance/hospital' && <HospitalPanel view={view} busy={busy} onAdvance={advance} />}
    </div>
  )
}

function NextActions({ view, busy, onAdvance }: { view: CrewView; busy: boolean; onAdvance: (target: string) => void }) {
  if (view.mission.next_states.length === 0) return <p className="crew-note">This mission has no further crew transitions.</p>
  return <div className="crew-actions">{view.mission.next_states.map((state) => <button key={state} className="crew-button primary" type="button" disabled={busy} onClick={() => onAdvance(state)}>{STATE_LABELS[state] ?? state.replaceAll('_', ' ')} <ArrowRight size={16} /></button>)}</div>
}

function OverviewPanel({ view, busy, onRespond, onAdvance }: { view: CrewView; busy: boolean; onRespond: (accepted: boolean) => void; onAdvance: (target: string) => void }) {
  const pending = view.assignment?.status === 'ASSIGNED'
  return <div className="crew-grid">
    <section className="crew-card">
      <h2>Assignment</h2>
      {view.assignment ? <>
        <p className="crew-status">{view.assignment.status.replaceAll('_', ' ')}</p>
        {pending && <div className="crew-actions"><button className="crew-button primary" type="button" disabled={busy} onClick={() => onRespond(true)}><Check size={16} /> ACCEPT</button><button className="crew-button danger" type="button" disabled={busy} onClick={() => onRespond(false)}><X size={16} /> REJECT</button></div>}
      </> : <p className="crew-note">No assignment record is attached to this mission.</p>}
    </section>
    <section className="crew-card">
      <h2>Next action</h2>
      <NextActions view={view} busy={busy} onAdvance={onAdvance} />
    </section>
    <section className="crew-card">
      <h2>Destination</h2>
      {view.destination ? <><p className="crew-status">{view.destination.hospital_code}</p><p className="crew-note">{view.destination.name}</p></> : <p className="crew-note">No destination has been confirmed yet.</p>}
    </section>
  </div>
}

function MissionPanel({ view }: { view: CrewView }) {
  const incident = view.incident
  return <div className="crew-grid">
    <section className="crew-card wide">
      <h2>Emergency mission</h2>
      {incident ? <>
        <p className="crew-status">{incident.incident_type} — {incident.severity}</p>
        <p className="crew-note"><MapPin size={14} /> {incident.address_text ?? 'Address not recorded'} · {incident.patient_count} patient(s)</p>
        <h3>Patient requirements</h3>
        {incident.requirements.length > 0
          ? <ul className="crew-requirements">{incident.requirements.map((item) => <li key={item.code}><Check size={14} /> {item.code} <small>{item.level}</small></li>)}</ul>
          : <p className="crew-note">No clinical requirements are recorded for this incident.</p>}
      </> : <p className="crew-note">Incident detail is unavailable.</p>}
    </section>
  </div>
}

function RouteFacts({ route }: { route: { distance_m: number; duration_seconds: number; traffic_duration_seconds: number; confidence: number; provider: string } | null }) {
  if (!route) return <p className="crew-note">No route has been calculated for this leg.</p>
  return <div className="crew-facts">
    <div><span>ETA</span><strong>{minutes(route.traffic_duration_seconds)} min</strong></div>
    <div><span>Distance</span><strong>{(route.distance_m / 1000).toFixed(1)} km</strong></div>
    <div><span>Free-flow</span><strong>{minutes(route.duration_seconds)} min</strong></div>
    <div><span>Confidence</span><strong>{Math.round(route.confidence * 100)}%</strong></div>
  </div>
}

function NavigationPanel({ view, geometry, alternative, options, busy, ticking, onTick, onAdvance, onReroute }: {
  view: CrewView; geometry: GeoPoint[]; alternative: GeoPoint[] | null; options: RouteComparison | null
  busy: boolean; ticking: boolean; onTick: (value: boolean) => void; onAdvance: (target: string) => void; onReroute: (option: RouteOption) => void
}) {
  const recommended = options?.alternatives.find((item) => item.variant === options.recommended_variant) ?? null
  return <div className="crew-grid">
    <section className="crew-card wide">
      <h2>Navigation</h2>
      <MissionMap
        incident={view.incident?.point ? { ...view.incident.point, label: view.incident.incident_code, sublabel: 'INCIDENT' } : null}
        ambulance={view.ambulance?.point ? { ...view.ambulance.point, label: view.ambulance.ambulance_code, sublabel: view.mission.status.replaceAll('_', ' '), stale: view.ambulance.gps_state !== 'FRESH' } : null}
        hospital={view.destination?.point ? { ...view.destination.point, label: view.destination.hospital_code, sublabel: 'DESTINATION' } : null}
        route={geometry.length > 0 ? geometry : null}
        alternativeRoute={alternative}
        dataMode={view.mission.data_mode}
        height={380}
      />
      <RouteFacts route={view.route ?? options?.current ?? null} />
      <div className="crew-actions">
        <NextActions view={view} busy={busy} onAdvance={onAdvance} />
        <button className={`crew-button ${ticking ? 'danger' : ''}`} type="button" onClick={() => onTick(!ticking)}>{ticking ? 'STOP SIMULATED GPS' : 'START SIMULATED GPS'}</button>
      </div>
      <p className="crew-note"><CircleDot size={13} /> Position updates are SIMULATED and replay the route geometry. They are not a real GPS fix.</p>
    </section>
    <section className="crew-card">
      <h2>Route options</h2>
      {options?.significant && recommended
        ? <div className="crew-reroute" role="status">
            <strong><AlertTriangle size={16} /> ROUTE CHANGE DETECTED</strong>
            <div className="crew-compare">
              <div><span>Current</span><strong>{minutes(options.current?.traffic_duration_seconds)} min</strong></div>
              <div><span>Alternative</span><strong>{minutes(recommended.traffic_duration_seconds)} min</strong></div>
              <div><span>Saving</span><strong>{minutes(options.saving_seconds)} min</strong></div>
            </div>
            <div className="crew-actions">
              <button className="crew-button primary" type="button" disabled={busy} onClick={() => onReroute(recommended)}><Route size={15} /> ACCEPT REROUTE</button>
            </div>
          </div>
        : <p className="crew-note">{options ? `No alternative saves more than ${minutes(options.threshold_seconds)} min on this leg.` : 'Route options are unavailable.'}</p>}
      {options?.alternatives.map((item) => <div key={item.variant} className="crew-option"><span>{item.label}</span><strong>{minutes(item.traffic_duration_seconds)} min</strong><small>{(item.distance_m / 1000).toFixed(1)} km</small></div>)}
    </section>
  </div>
}

function PatientPanel({ view, busy, onAdvance }: { view: CrewView; busy: boolean; onAdvance: (target: string) => void }) {
  const onScene = view.mission.status === 'ON_SCENE'
  return <div className="crew-grid">
    <section className="crew-card wide">
      <h2>Patient</h2>
      <p className="crew-status">{view.mission.status.replaceAll('_', ' ')}</p>
      {onScene
        ? <><p className="crew-note">Confirm pickup to move the mission to PATIENT ON BOARD. The destination leg is routed after that.</p><NextActions view={view} busy={busy} onAdvance={onAdvance} /></>
        : <p className="crew-note">Pickup confirmation becomes available once the mission reaches ON SCENE.</p>}
      <h3>Requirements</h3>
      {view.incident && view.incident.requirements.length > 0
        ? <ul className="crew-requirements">{view.incident.requirements.map((item) => <li key={item.code}><Check size={14} /> {item.code} <small>{item.level}</small></li>)}</ul>
        : <p className="crew-note">No clinical requirements are recorded.</p>}
    </section>
  </div>
}

function HospitalPanel({ view, busy, onAdvance }: { view: CrewView; busy: boolean; onAdvance: (target: string) => void }) {
  return <div className="crew-grid">
    <section className="crew-card wide">
      <h2>Destination hospital</h2>
      {view.destination ? <>
        <p className="crew-status"><Hospital size={18} /> {view.destination.hospital_code} — {view.destination.name}</p>
        <div className="crew-facts">
          <div><span>Acceptance</span><strong>{view.acceptance?.status ?? 'NOT REQUESTED'}</strong></div>
          <div><span>ETA</span><strong>{view.route ? `${minutes(view.route.traffic_duration_seconds)} min` : 'UNKNOWN'}</strong></div>
        </div>
        <h3>Reserved resources</h3>
        {view.reservations.length > 0
          ? <ul className="crew-requirements">{view.reservations.map((item) => <li key={item.id}><Check size={14} /> {item.resource_type ?? 'RESOURCE'} <small>{item.status}</small></li>)}</ul>
          : <p className="crew-note">No resource reservation is recorded for this mission.</p>}
        <NextActions view={view} busy={busy} onAdvance={onAdvance} />
      </> : <>
        <p className="crew-note">No destination has been confirmed. The dispatcher confirms the hospital after acceptance.</p>
        <p className="crew-note"><Clock3 size={13} /> Destination, acceptance and reservation state are server-authoritative and are never assumed here.</p>
      </>}
    </section>
  </div>
}

export default CrewWorkspace
