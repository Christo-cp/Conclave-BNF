import { useEffect, useState } from 'react'
import { Activity, AlertTriangle, Ambulance, Check, CircleDot, RefreshCw, ShieldCheck, Wifi, X } from 'lucide-react'
import { api, ApiError, type AcceptanceRequest, type Mission, type ResourceSnapshot, type ViewState } from './lib/api'
import { getAuthContext, type Role } from './lib/auth'
import { RealtimeClient, realtimeUrl, type RealtimeEvent } from './lib/realtime'
import { ResourceCard } from './components/decision-state'

function StateBanner({ state, message }: { state: ViewState; message?: string }) {
  if (state === 'loading') return <div className="state-banner" role="status" aria-live="polite" aria-atomic="true"><RefreshCw aria-hidden="true" className="spin" size={16} /> Loading current data...</div>
  if (state === 'error') return <div className="state-banner state-error" role="alert"><AlertTriangle aria-hidden="true" size={16} /> {message ?? 'The service is unavailable. No action was confirmed.'}</div>
  if (state === 'stale') return <div className="state-banner state-stale" role="status" aria-live="polite" aria-atomic="true"><AlertTriangle aria-hidden="true" size={16} /> Showing stale data. Refresh before making a critical decision.</div>
  return null
}

function RoleHeader({ role }: { role: Role }) {
  const labels: Record<Role, string> = { DISPATCHER: 'DISPATCHER', HOSPITAL: 'HOSPITAL INTAKE', AMBULANCE_CREW: 'AMBULANCE CREW', DEMO_CONTROLLER: 'DEMO CONTROLLER' }
  return <div className="page-heading role-heading"><div><div className="eyebrow"><span className="live-dot" /> ROLE WORKSPACE / {labels[role]}</div><h1>{labels[role]}</h1><p>Decision support for synthetic emergency coordination. Server state remains authoritative.</p></div><div className="demo-stamp"><CircleDot aria-hidden="true" size={14} /> SIMULATED DATA</div></div>
}

function useRealtime(onEvent: (event: RealtimeEvent) => void, onResync: () => Promise<void>) {
  useEffect(() => {
    const auth = getAuthContext(api.getToken())
    if (!auth || auth.demoFallback) return
    const client = new RealtimeClient(realtimeUrl(auth.token), onEvent, onResync)
    client.connect()
    return () => client.stop()
  }, [onEvent, onResync])
}

export function HospitalScreen() {
  const [requestId, setRequestId] = useState('')
  const [hospitalId, setHospitalId] = useState('H-003')
  const [reason, setReason] = useState('')
  const [acceptance, setAcceptance] = useState<AcceptanceRequest | null>(null)
  const [resources, setResources] = useState<ResourceSnapshot[]>([])
  const [state, setState] = useState<ViewState>('idle')
  const [message, setMessage] = useState('')
  const refresh = async () => { setState('loading'); try { setResources(await api.resources(hospitalId)); setState('success') } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Resource endpoint unavailable.') } }
  useRealtime(() => { void refresh() }, refresh)
  async function respond(action: 'accept' | 'reject') { if (!requestId) return; setState('loading'); try { const result = action === 'accept' ? await api.acceptAcceptance(requestId) : await api.rejectAcceptance(requestId, reason); setAcceptance(result); setState('success') } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Acceptance action was not confirmed.') } }
  return <><RoleHeader role="HOSPITAL" /><div className="role-grid"><section className="workspace-panel"><div className="section-heading"><div><span className="section-number">01</span><div><h2>Incoming acceptance</h2><p>Review a dispatch request before accepting or rejecting the destination.</p></div></div></div><StateBanner state={state} message={message} /><div className="field"><label htmlFor="acceptance-request">Acceptance request ID</label><input id="acceptance-request" value={requestId} onChange={(event) => setRequestId(event.target.value)} placeholder="UUID from dispatcher notification" /></div><div className="field"><label htmlFor="hospital-code">Hospital code</label><input id="hospital-code" value={hospitalId} onChange={(event) => setHospitalId(event.target.value)} /></div><div className="field"><label htmlFor="rejection-reason">Rejection reason</label><textarea id="rejection-reason" value={reason} onChange={(event) => setReason(event.target.value)} rows={3} /></div><div className="button-row"><button className="primary-button" type="button" disabled={!requestId || state === 'loading'} onClick={() => respond('accept')}><Check aria-hidden="true" size={16} /> ACCEPT</button><button className="secondary-button" type="button" disabled={!requestId || !reason || state === 'loading'} onClick={() => respond('reject')}><X aria-hidden="true" size={16} /> REJECT</button></div>{acceptance && <div className="success-note" role="status" aria-live="polite"><ShieldCheck aria-hidden="true" size={16} /> Server response: {acceptance.status}</div>}</section><section className="workspace-panel"><div className="section-heading"><div><span className="section-number">02</span><div><h2>Resource availability</h2><p>Unknown capacity is never treated as available.</p></div></div><button className="ghost-button" type="button" onClick={refresh}>Refresh</button></div>{state === 'success' && resources.length === 0 ? <ResourceCard state="error" /> : resources.map((resource) => <div className="resource-row" key={resource.code}><strong>{resource.code}</strong><span>{resource.available ?? 'UNKNOWN'} available</span><span>{resource.reserved ?? 'UNKNOWN'} reserved</span><span className="simulated-text">{resource.data_mode ?? 'SIMULATED'}</span></div>)}</section></div></>
}

export function AmbulanceScreen() {
  const [missionId, setMissionId] = useState('')
  const [mission, setMission] = useState<Mission | null>(null)
  const [state, setState] = useState<ViewState>('idle')
  const [message, setMessage] = useState('')
  const refresh = async () => { if (!missionId) return; setState('loading'); try { setMission(await api.mission(missionId)); setState('success') } catch (error) { setState('stale'); setMessage(error instanceof ApiError ? error.message : 'Mission endpoint unavailable. Cached destination may be shown.') } }
  useRealtime((event) => { if (event.entity_id === missionId) void refresh() }, refresh)
  async function update(status: string) { if (!mission) return; setState('loading'); try { setMission(await api.patchMission(mission.id, status, mission.state_version)); setState('success') } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Mission update was rejected.') } }
  return <><RoleHeader role="AMBULANCE_CREW" /><div className="role-grid"><section className="workspace-panel"><div className="section-heading"><div><span className="section-number">01</span><div><h2>Mission status</h2><p>Updates include the server state version to prevent stale overwrites.</p></div></div></div><div className="field"><label htmlFor="mission-id">Mission ID</label><input id="mission-id" value={missionId} onChange={(event) => setMissionId(event.target.value)} placeholder="MSN-000001 or UUID" /></div><button className="primary-button" type="button" onClick={refresh} disabled={!missionId || state === 'loading'}><RefreshCw aria-hidden="true" size={16} /> LOAD MISSION</button><StateBanner state={state} message={message} />{mission && <div className="mission-card"><span className="status-pill simulated"><CircleDot aria-hidden="true" size={13} /> {mission.data_mode ?? 'SIMULATED'}</span><h2>{mission.status}</h2><p>Version {mission.state_version} · Mission {mission.id}</p><div className="button-row"><button className="secondary-button" type="button" onClick={() => update('EN_ROUTE')}>EN ROUTE</button><button className="secondary-button" type="button" onClick={() => update('ARRIVED')}>ARRIVED</button></div></div>}</section><aside className="workspace-panel cached-destination"><div className="panel-kicker"><Wifi aria-hidden="true" size={16} /> OFFLINE-SAFE DESTINATION</div>{mission?.destination ? <><h2>{mission.destination.code ?? 'Destination'}</h2><p>{mission.destination.name ?? 'Cached destination name unavailable'}</p><span className="status-pill warning">CACHED / VERIFY WHEN ONLINE</span></> : <><Ambulance aria-hidden="true" size={28} /><h2>No cached destination</h2><p>Load a mission while connected. Unknown destination data is not fabricated.</p></>}</aside></div></>
}

export function DemoControllerScreen() {
  const [state, setState] = useState<ViewState>('idle')
  const [message, setMessage] = useState('')
  async function control(action: string) { setState('loading'); try { await api.simulation(action); setState('success'); setMessage(`Simulation action requested: ${action}`) } catch (error) { setState('error'); setMessage(error instanceof ApiError ? error.message : 'Simulation control endpoint unavailable.') } }
  return <><RoleHeader role="DEMO_CONTROLLER" /><section className="workspace-panel controller-panel"><div className="panel-kicker"><Activity aria-hidden="true" size={16} /> DEMO SCENARIO CONTROLS</div><p>Controls are visibly simulated and must never be presented as live clinical data.</p><StateBanner state={state} message={message} />{state === 'success' && <div className="success-note" role="status" aria-live="polite">{message}</div>}<div className="control-grid">{['RESET_SCENARIO', 'TRAFFIC_CHANGE', 'HOSPITAL_REJECT', 'RESOURCE_LOSS', 'RECONNECT_STREAM'].map((action) => <button className="secondary-button" type="button" key={action} onClick={() => control(action)} disabled={state === 'loading'}>{action.replaceAll('_', ' ')}</button>)}</div></section></>
}
