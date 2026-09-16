import { useEffect, useState } from 'react'
import { BrowserRouter, Link, Navigate, useLocation } from 'react-router'
import {
  Activity,
  AlertTriangle,
  Ambulance,
  ArrowRight,
  Check,
  CircleDot,
  Clock3,
  FilePlus2,
  Hospital,
  Info,
  LogOut,
  MapPin,
  Menu,
  Navigation,
  RefreshCw,
  ShieldCheck,
  Siren,
  Wifi,
  X,
  Zap,
} from 'lucide-react'
import { api, ApiError, type AlertRecord, type AmbulanceRecord, type Candidate, type HospitalRecord, type Incident, type HospitalCandidate, type RouteResult } from './lib/api'
import { CandidateList, type ViewState } from './components/decision-state'
import './App.css'
import { DemoControllerScreen, HospitalScreen, AmbulanceScreen } from './RoleScreens'
import { getAuthContext, rolePath } from './lib/auth'

type Screen = 'login' | 'new' | 'detail'

const demoCredentials = { email: 'dispatcher.demo@demo.invalid', password: 'demo-password-change-me' }

function App() {
  const location = useLocation()
  const [screen, setScreen] = useState<Screen>(api.getToken() ? 'new' : 'login')
  const [incident, setIncident] = useState<Incident | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [mobileNav, setMobileNav] = useState(false)

  useEffect(() => {
    const handleAuthExpired = () => {
      setIncident(null)
      setScreen('login')
      setError('Your session expired. Sign in again to continue.')
    }
    window.addEventListener('conclave:auth-expired', handleAuthExpired)
    return () => window.removeEventListener('conclave:auth-expired', handleAuthExpired)
  }, [])

  function handleLogout() {
    api.clearToken()
    setIncident(null)
    setScreen('login')
  }

  if (screen === 'login') return <LoginScreen onLogin={() => setScreen('new')} />

  const auth = getAuthContext(api.getToken())
  const role = auth?.role ?? 'DISPATCHER'
  if (role !== 'DISPATCHER' && role !== 'DEMO_CONTROLLER' && location.pathname === '/') return <Navigate to={rolePath(role)} replace />
  if (role === 'DEMO_CONTROLLER' && location.pathname === '/') return <Navigate to="/demo" replace />
  if (location.pathname === '/hospital' && role === 'HOSPITAL') return <RoleShell auth={auth}><HospitalScreen /></RoleShell>
  if (location.pathname === '/ambulance' && role === 'AMBULANCE_CREW') return <RoleShell auth={auth}><AmbulanceScreen /></RoleShell>
  if (location.pathname === '/demo' && role === 'DEMO_CONTROLLER') return <RoleShell auth={auth}><DemoControllerScreen /></RoleShell>
  if (location.pathname === '/ambulances') return <RoleShell auth={auth}><AmbulanceFleetScreen /></RoleShell>
  if (location.pathname === '/hospitals') return <RoleShell auth={auth}><HospitalNetworkScreen /></RoleShell>
  if (location.pathname === '/alerts') return <RoleShell auth={auth}><ActiveAlertsScreen /></RoleShell>

  return (
    <div className="app-shell">
      <header className="topbar">
         <button className="mobile-menu" type="button" aria-label={mobileNav ? 'Close navigation' : 'Open navigation'} aria-expanded={mobileNav} aria-controls="operations-navigation" onClick={() => setMobileNav((value) => !value)}><Menu aria-hidden="true" size={20} /></button>
        <button className="brand" type="button" onClick={() => setScreen('new')} aria-label="Go to dispatch console">
          <span className="brand-mark"><Siren size={19} /></span>
          <span><strong>CONCLAVE</strong><small>EMERGENCY COMMAND</small></span>
        </button>
        <div className="topbar-meta">
          <span className="connection"><span className="live-dot" /> API CONNECTED</span>
          <span className="operator"><span className="avatar">DD</span> Dispatcher Demo</span>
          <button className="icon-button" type="button" aria-label="Log out" onClick={handleLogout}><LogOut size={17} /></button>
        </div>
      </header>
      <div className="app-body">
         <aside id="operations-navigation" className={`sidebar ${mobileNav ? 'sidebar-open' : ''}`} aria-label="Operations navigation">
          <div className="sidebar-heading">OPERATIONS</div>
           <Link className={`nav-item ${location.pathname.startsWith('/dispatch') ? 'active' : ''}`} to="/dispatch" onClick={() => { setScreen('new'); setMobileNav(false) }}><Activity size={17} /> Dispatch console</Link>
           {role === 'HOSPITAL' && <Link className={`nav-item ${location.pathname === '/hospital' ? 'active' : ''}`} to="/hospital"><Hospital size={17} /> Hospital intake</Link>}
           {role === 'AMBULANCE_CREW' && <Link className={`nav-item ${location.pathname === '/ambulance' ? 'active' : ''}`} to="/ambulance"><Ambulance size={17} /> Crew mission</Link>}
           {role === 'DEMO_CONTROLLER' && <Link className={`nav-item ${location.pathname === '/demo' ? 'active' : ''}`} to="/demo"><Zap size={17} /> Demo controls</Link>}
           <Link className={`nav-item ${location.pathname === '/ambulances' ? 'active' : ''}`} to="/ambulances"><Ambulance size={17} /> Ambulance fleet</Link>
           <Link className={`nav-item ${location.pathname === '/hospitals' ? 'active' : ''}`} to="/hospitals"><Hospital size={17} /> Hospital network</Link>
           <Link className={`nav-item ${location.pathname === '/alerts' ? 'active' : ''}`} to="/alerts"><AlertTriangle size={17} /> Active alerts</Link>
           <div className="sidebar-footer"><div className="sidebar-heading">SYSTEM</div><span><Wifi size={14} /> {auth?.demoFallback ? 'DEMO ROLE FALLBACK' : `JWT ROLE: ${role}`}</span><span><ShieldCheck size={14} /> Audit logging on</span></div>
        </aside>
        <main className="main-content">
          {error && <div className="global-alert" role="alert"><AlertTriangle size={18} /><span>{error}</span><button type="button" onClick={() => setError(null)} aria-label="Dismiss alert"><X size={16} /></button></div>}
           {auth?.demoFallback && <div className="fallback-note" role="status"><CircleDot size={14} /> DEMO FALLBACK: JWT has no role claim. Dispatcher workspace is shown.</div>}
           {screen === 'new' && <NewIncident onCreated={(next) => { setIncident(next); setScreen('detail') }} onError={setError} />}
          {screen === 'detail' && incident && <IncidentDetail incident={incident} onBack={() => setScreen('new')} onError={setError} />}
        </main>
      </div>
    </div>
  )
}

function DataState({ state, message, empty }: { state: ViewState; message: string; empty?: boolean }) {
  if (state === 'loading') return <div className="state-banner" role="status">Loading authoritative data...</div>
  if (state === 'error') return <div className="state-banner state-error" role="alert">{message}</div>
  if (empty) return <div className="empty-state" role="status"><Info size={20} /><strong>No active records</strong><span>{message}</span></div>
  return null
}

function AmbulanceFleetScreen() {
  const [items, setItems] = useState<AmbulanceRecord[]>([]); const [state, setState] = useState<ViewState>('loading'); const [message, setMessage] = useState('')
  const load = async () => { setState('loading'); try { setItems(await api.ambulances()); setState('success') } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Ambulance fleet could not be loaded.') } }
  useEffect(() => { void load() }, [])
  return <><div className="page-heading role-heading"><div><div className="eyebrow"><Ambulance size={13} /> OPERATIONS / FLEET</div><h1>Ambulance fleet</h1><p>Live units, assignment state, equipment context, and GPS freshness from the dispatch database.</p></div><button className="secondary-button" onClick={load}><RefreshCw size={15} /> REFRESH FLEET</button></div><section className="workspace-panel data-panel"><div className="panel-kicker"><Ambulance size={16} /> AUTHORITATIVE FLEET FEED <span>SIMULATED</span></div><DataState state={state} message={message} empty={state === 'success' && items.length === 0} /><div className="data-table" aria-label="Ambulance fleet">{items.map((item) => <article className="data-row" key={item.id}><div><strong>{item.ambulance_code}</strong><span>{item.vehicle_type} · {item.crew_summary?.level ?? 'Crew data unavailable'}</span></div><span className={`state-chip state-${item.status.toLowerCase()}`}>{item.status.replaceAll('_', ' ')}</span><span>{item.latitude != null ? `${item.latitude.toFixed(3)}, ${item.longitude?.toFixed(3)}` : 'LOCATION UNKNOWN'}</span><span>{item.gps_updated_at ? new Date(item.gps_updated_at).toLocaleTimeString() : 'GPS UNKNOWN'}</span><span className="status-pill simulated">{item.data_mode}</span></article>)}</div></section></>
}

function HospitalNetworkScreen() {
  const [items, setItems] = useState<HospitalRecord[]>([]); const [state, setState] = useState<ViewState>('loading'); const [message, setMessage] = useState('')
  const load = async () => { setState('loading'); try { const hospitals = await api.hospitals(); setItems(await Promise.all(hospitals.map(async (hospital) => ({ ...hospital, ...(await api.getHospital(hospital.id)) } as HospitalRecord)))); setState('success') } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Hospital network could not be loaded.') } }
  useEffect(() => { void load() }, [])
  return <><div className="page-heading role-heading"><div><div className="eyebrow"><Hospital size={13} /> OPERATIONS / NETWORK</div><h1>Hospital network</h1><p>Emergency capability and current resource state from the same records used by hospital matching.</p></div><button className="secondary-button" onClick={load}><RefreshCw size={15} /> REFRESH NETWORK</button></div><DataState state={state} message={message} empty={state === 'success' && items.length === 0} /><div className="network-grid">{items.map((hospital) => <article className="hospital-card" key={hospital.id}><div className="hospital-card-head"><div><strong>{hospital.hospital_code}</strong><h2>{hospital.name}</h2></div><span className={`state-chip state-${hospital.status.toLowerCase()}`}>{hospital.status.replaceAll('_', ' ')}</span></div><div className="hospital-meta"><span>{hospital.emergency_capable ? 'EMERGENCY CAPABLE' : 'EMERGENCY UNKNOWN'}</span><span>{hospital.latitude.toFixed(3)}, {hospital.longitude.toFixed(3)}</span></div><div className="capability-list">{hospital.capabilities?.map((capability) => <span key={capability.code}>{capability.code} · {capability.status}</span>) ?? <span>CAPABILITIES UNKNOWN</span>}</div><div className="resource-list">{hospital.resources?.map((resource) => <div key={resource.resource_type}><span>{resource.resource_type}</span><strong>{resource.available_capacity ?? 'UNKNOWN'}</strong><small>available</small></div>) ?? <span>RESOURCE DATA UNKNOWN</span>}</div><span className="status-pill simulated">{hospital.data_mode}</span></article>)}</div></>
}

function ActiveAlertsScreen() {
  const [items, setItems] = useState<AlertRecord[]>([]); const [state, setState] = useState<ViewState>('loading'); const [message, setMessage] = useState('')
  const load = async () => { setState('loading'); try { setItems(await api.alerts()); setState('success') } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Active alerts could not be loaded.') } }
  useEffect(() => { void load() }, [])
  return <><div className="page-heading role-heading"><div><div className="eyebrow"><AlertTriangle size={13} /> OPERATIONS / ALERTS</div><h1>Active alerts</h1><p>Persisted system alerts tied to fleet, hospital, reservation, and mission state.</p></div><button className="secondary-button" onClick={load}><RefreshCw size={15} /> REFRESH ALERTS</button></div><section className="workspace-panel data-panel"><div className="panel-kicker"><AlertTriangle size={16} /> ACTIVE SYSTEM EVENTS <span>{items.length} ACTIVE</span></div><DataState state={state} message={message} empty={state === 'success' && items.length === 0} /><div className="alert-list">{items.map((alert) => <article className="alert-row" key={alert.id}><div className={`alert-icon alert-${alert.severity.toLowerCase()}`}><AlertTriangle size={17} /></div><div><strong>{alert.message}</strong><span>{alert.type.replaceAll('_', ' ')} · {new Date(alert.created_at).toLocaleString()}</span></div><span className={`state-chip state-${alert.severity.toLowerCase()}`}>{alert.severity}</span><span className="status-pill simulated">{alert.data_mode}</span></article>)}</div></section></>
}

function RoleShell({ auth, children }: { auth: ReturnType<typeof getAuthContext>; children: React.ReactNode }) {
  return <div className="app-shell"><header className="topbar"><Link className="brand" to={rolePath(auth?.role ?? null)}><span className="brand-mark"><Siren size={19} /></span><span><strong>CONCLAVE</strong><small>EMERGENCY COMMAND</small></span></Link><div className="topbar-meta"><span className="connection"><span className="live-dot" /> {auth?.demoFallback ? 'DEMO FALLBACK' : 'JWT ROLE ACTIVE'}</span><span className="operator">{auth?.role ?? 'DISPATCHER'}</span></div></header><main className="main-content">{children}</main></div>
}

function LoginScreen({ onLogin }: { onLogin: () => void }) {
  const [email, setEmail] = useState(demoCredentials.email)
  const [password, setPassword] = useState(demoCredentials.password)
  const [state, setState] = useState<ViewState>('idle')
  const [error, setError] = useState<string | null>(null)

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setState('loading'); setError(null)
    try { const result = await api.login(email, password); api.setToken(result.access_token); onLogin() } catch (cause) { setState('error'); setError(cause instanceof ApiError ? cause.message : 'The command service could not be reached.') }
  }

  return <div className="login-page"><div className="login-grid" /><div className="login-panel">
    <div className="login-brand"><span className="brand-mark large"><Siren size={28} /></span><div><strong>CONCLAVE</strong><small>EMERGENCY COMMAND</small></div></div>
    <div className="demo-ribbon"><CircleDot size={14} /> DEMO MODE <span>·</span> SYNTHETIC DATA ONLY</div>
    <h1>Dispatch with<br /><em>confidence.</em></h1><p className="login-copy">A decision-support console for coordinating emergency response when every minute matters.</p>
    <form onSubmit={submit} className="login-form"><label htmlFor="email">Operator email</label><input id="email" type="email" autoComplete="username" value={email} onChange={(event) => setEmail(event.target.value)} required />
      <label htmlFor="password">Password</label><input id="password" type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
      {error && <div className="form-error" role="alert"><AlertTriangle size={15} /> {error}</div>}
      <button className="primary-button full" type="submit" disabled={state === 'loading'}>{state === 'loading' ? <><RefreshCw className="spin" size={16} /> AUTHENTICATING</> : <>ENTER COMMAND CENTER <ArrowRight size={17} /></>}</button>
    </form><p className="login-note">Demo access prefilled · all records are clearly marked simulated</p>
  </div><div className="login-rail"><span>OPERATIONS / 01</span><span>EST. 2026</span></div></div>
}

function NewIncident({ onCreated, onError }: { onCreated: (incident: Incident) => void; onError: (message: string) => void }) {
  const [type, setType] = useState('TRAUMA'); const [severity, setSeverity] = useState('CRITICAL'); const [address, setAddress] = useState('MG Road & Residency Road, Bengaluru'); const [notes, setNotes] = useState('High-speed road traffic collision. Patient requires advanced respiratory support.'); const [state, setState] = useState<ViewState>('idle')
  async function submit(event: React.FormEvent<HTMLFormElement>) { event.preventDefault(); setState('loading')
    try { const next = await api.createIncident({ incident_type: type, severity, latitude: 12.9716, longitude: 77.5946, address_text: address, patient_count: 1, notes }); await Promise.all([api.addRequirement(next.id, 'ICU'), api.addRequirement(next.id, 'VENTILATOR')]); onCreated(next) } catch (cause) { setState('error'); onError(cause instanceof ApiError ? cause.message : 'Could not create the incident. Check the API connection.') }
  }
  return <><div className="page-heading"><div><div className="eyebrow"><span className="live-dot" /> DISPATCH CONSOLE / NEW INCIDENT</div><h1>Start an emergency response</h1><p>Capture the situation first. The system will evaluate suitable resources against mandatory requirements.</p></div><div className="demo-stamp"><CircleDot size={14} /> DEMO MODE</div></div>
    <div className="workflow"><span className="step current"><b>01</b> INCIDENT</span><span className="line" /><span className="step"><b>02</b> AMBULANCE</span><span className="line" /><span className="step"><b>03</b> DESTINATION</span><span className="line" /><span className="step"><b>04</b> RESOURCES</span></div>
    <form className="incident-layout" onSubmit={submit}><section className="form-panel"><div className="panel-kicker"><FilePlus2 size={17} /> INCIDENT INTAKE <span>REQUIRED FIELDS</span></div><div className="form-grid"><div className="field wide"><label htmlFor="incident-type">Incident type</label><select id="incident-type" value={type} onChange={(event) => setType(event.target.value)}><option>TRAUMA</option><option>MEDICAL</option><option>MATERNITY</option><option>FIRE</option></select></div><div className="field"><label htmlFor="severity">Severity</label><select id="severity" value={severity} onChange={(event) => setSeverity(event.target.value)}><option>CRITICAL</option><option>HIGH</option><option>MODERATE</option></select></div><div className="field wide"><label htmlFor="address">Location</label><div className="input-with-icon"><MapPin size={16} /><input id="address" value={address} onChange={(event) => setAddress(event.target.value)} required /></div><small>GPS coordinates will be resolved by the routing service</small></div><div className="field"><label htmlFor="patient-count">Patients</label><input id="patient-count" type="number" min="1" defaultValue="1" /></div><div className="field wide"><label htmlFor="notes">Dispatcher notes</label><textarea id="notes" rows={4} value={notes} onChange={(event) => setNotes(event.target.value)} /></div></div><div className="requirements"><div className="requirements-heading"><div><strong>Clinical requirements</strong><small>Used as hard constraints during matching</small></div><span className="required-label">REQUIRED</span></div><div className="requirement-tags"><span><Check size={14} /> ICU</span><span><Check size={14} /> VENTILATOR</span><span className="tag-muted">+ Add requirement</span></div></div></section><aside className="intake-aside"><div className="aside-illustration"><div className="radar"><span /><span /><span /><span /></div><Siren size={26} /></div><h2>Every decision<br />has a reason.</h2><p>Conclave filters hard constraints before ranking anything. Ineligible ambulances are never scored as alternatives.</p><div className="aside-rule"><Check size={14} /> Eligibility before proximity</div><div className="aside-rule"><Check size={14} /> Freshness shown at a glance</div><div className="aside-rule"><Check size={14} /> Server-authoritative reservations</div></aside><div className="form-actions"><span><Info size={15} /> This creates a simulated incident for the demo scenario.</span><button className="primary-button" type="submit" disabled={state === 'loading'}>{state === 'loading' ? <><RefreshCw className="spin" size={16} /> CREATING...</> : <>CREATE & ANALYZE <ArrowRight size={17} /></>}</button></div></form></>
}

function IncidentDetail({ incident, onBack, onError }: { incident: Incident; onBack: () => void; onError: (message: string) => void }) {
  const [ambulances, setAmbulances] = useState<Candidate[]>([]); const [hospitals, setHospitals] = useState<HospitalCandidate[]>([]); const [ambulanceState, setAmbulanceState] = useState<ViewState>('loading'); const [hospitalState, setHospitalState] = useState<ViewState>('idle'); const [selectedAmbulance, setSelectedAmbulance] = useState<Candidate | null>(null); const [selectedHospital, setSelectedHospital] = useState<HospitalCandidate | null>(null); const [route, setRoute] = useState<RouteResult | null>(null); const [actionState, setActionState] = useState<ViewState>('idle'); const [showWhy, setShowWhy] = useState(false)
  useEffect(() => { let active = true; api.matchAmbulances(incident.id).then((items) => { if (active) { setAmbulances(items); setAmbulanceState('success'); setSelectedAmbulance(items.find((item) => item.eligible) ?? null) } }).catch((cause) => { if (active) { setAmbulanceState('error'); onError(cause instanceof ApiError ? cause.message : 'Ambulance matching service unavailable.') } }); return () => { active = false } }, [incident.id, onError])
  async function confirmAmbulance() { if (!selectedAmbulance?.ambulance_id) return; setActionState('loading'); try { await api.confirmAmbulance(selectedAmbulance.ambulance_id, incident.id); setActionState('success'); await loadHospitals() } catch (cause) { setActionState('error'); onError(cause instanceof ApiError ? cause.message : 'Ambulance confirmation failed. No assignment was made.') } }
  async function loadHospitals() { setHospitalState('loading'); try { const items = await api.matchHospitals(incident.id); setHospitals(items); setHospitalState('success'); setSelectedHospital(items.find((item) => item.eligible) ?? null) } catch (cause) { setHospitalState('error'); onError(cause instanceof ApiError ? cause.message : 'Hospital matching service unavailable.') } }
  async function calculateRoute() { if (!selectedHospital?.hospital_id) return; setActionState('loading'); try { const next = await api.calculateRoute(incident.id, selectedHospital.hospital_id); setRoute(next); setActionState('success') } catch (cause) { setActionState('error'); onError(cause instanceof ApiError ? cause.message : 'Routing service unavailable. Last known route is not available.') } }
  return <><div className="page-heading detail-heading"><div><button className="back-link" type="button" onClick={onBack}>← New incident</button><div className="eyebrow"><span className="critical-dot" /> ACTIVE INCIDENT / {incident.incident_code}</div><h1>{incident.incident_type} response <span className="severity-badge">{incident.severity}</span></h1><p><MapPin size={15} /> {incident.address_text} <span className="separator">·</span> Patient count {incident.patient_count}</p></div><div className="detail-status"><span className="status-pill simulated"><CircleDot size={13} /> SIMULATED</span><span className="status-pill warning"><Clock3 size={13} /> UPDATED JUST NOW</span></div></div>
    <div className="incident-banner"><div className="incident-banner-icon"><Siren size={21} /></div><div><strong>Clinical requirements locked</strong><span>ICU capacity · Ventilator · Trauma capability</span></div><span className="banner-status"><Check size={15} /> READY TO MATCH</span></div>
     <div className="detail-grid"><section className="workspace-panel"><div className="section-heading"><div><span className="section-number">01</span><div><h2>Ambulance recommendation</h2><p>Suitable resources ranked by ETA, capability, and data freshness.</p></div></div><button className="ghost-button" type="button" onClick={() => { setAmbulanceState('loading'); api.matchAmbulances(incident.id).then(setAmbulances).then(() => setAmbulanceState('success')).catch(() => setAmbulanceState('error')) }}><RefreshCw size={15} /> Refresh</button></div><CandidateList title="AVAILABLE FLEET" candidates={ambulances} state={ambulanceState} kind="ambulance" onSelect={setSelectedAmbulance} selectedCode={selectedAmbulance?.code} onRetry={() => { setAmbulanceState('loading'); api.matchAmbulances(incident.id).then(setAmbulances).then(() => setAmbulanceState('success')).catch(() => setAmbulanceState('error')) }} /></section>
      <aside className="right-column"><div className="map-panel"><div className="map-grid" /><div className="map-topline"><span><Navigation size={14} /> LIVE OPERATIONS MAP</span><span className="map-badge">MOCK ROUTING</span></div><div className="route-line route-a" /><div className="route-line route-b" /><div className="map-marker marker-incident"><Siren size={13} /></div><div className="map-marker marker-ambulance"><Ambulance size={13} /></div><div className="map-label label-incident">INCIDENT</div><div className="map-label label-ambulance">{selectedAmbulance?.code ?? 'AMBULANCE'}</div><div className="map-footer"><span><span className="legend-dot red" /> Incident</span><span><span className="legend-dot blue" /> Recommended unit</span></div></div><div className="explain-panel"><div className="panel-kicker"><Zap size={16} /> DECISION TRACE <button type="button" onClick={() => setShowWhy((value) => !value)} aria-expanded={showWhy}>{showWhy ? 'Hide' : 'Why selected?'}</button></div>{showWhy ? <ul className="reason-list"><li><Check size={15} /> Required equipment present</li><li><Check size={15} /> Available with no active mission</li><li><Check size={15} /> GPS fresh · 5 seconds old</li><li><Check size={15} /> Feasible ETA · 7 minutes</li></ul> : <p>Select “Why selected?” to inspect the deterministic eligibility and ranking trace.</p>}</div></aside>
    </div><div className="confirmation-bar"><div><span className="bar-label">SELECTED UNIT</span><strong>{selectedAmbulance?.code ?? 'No eligible unit selected'}</strong><span>{selectedAmbulance ? 'ETA 7 min · ALS crew · suitable for locked requirements' : 'Choose an eligible ambulance to continue'}</span></div><button className="primary-button" type="button" disabled={!selectedAmbulance || actionState === 'loading'} onClick={confirmAmbulance}>{actionState === 'loading' ? <><RefreshCw className="spin" size={16} /> CONFIRMING...</> : actionState === 'success' ? <><Check size={16} /> ASSIGNMENT CONFIRMED</> : <>CONFIRM AMBULANCE <ArrowRight size={17} /></>}</button></div>
     <section className="workspace-panel hospital-section"><div className="section-heading"><div><span className="section-number">02</span><div><h2>Destination & resources</h2><p>Hospitals are ranked only after ambulance assignment is confirmed.</p></div></div></div>{actionState !== 'success' && hospitalState === 'idle' ? <div className="locked-state"><ShieldCheck size={24} /><strong>Awaiting ambulance confirmation</strong><span>Confirm the suitable unit above to query destination capacity.</span></div> : <><CandidateList title="HOSPITAL NETWORK" candidates={hospitals} state={hospitalState} kind="hospital" onSelect={setSelectedHospital} selectedCode={selectedHospital?.code} /><div className="resource-actions"><div className="resource-summary"><span className="bar-label">DESTINATION</span><strong>{selectedHospital?.code ?? 'Select an eligible hospital'}</strong><span>{selectedHospital ? 'ICU · Ventilator capacity verified · simulated feed' : 'No destination selected'}</span></div><button className="secondary-button" type="button" disabled={!selectedHospital || actionState === 'loading'} onClick={calculateRoute}>{route ? <><Check size={16} /> ROUTE CALCULATED</> : <><Navigation size={16} /> CALCULATE ROUTE</>}</button></div>{route && <div className="route-result"><Navigation size={16} /><strong>{Math.round(route.duration_seconds / 60)} min</strong><span>via Mock Routing · {(route.distance_m / 1000).toFixed(1)} km · confidence {Math.round(route.confidence * 100)}%</span><span className="status-pill simulated">SIMULATED</span></div>}</>}</section>
  </>
}

export default function RoutedApp() { return <BrowserRouter><App /></BrowserRouter> }
