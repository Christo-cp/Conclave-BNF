import { divIcon, latLngBounds } from 'leaflet'
import type { DivIcon, LatLngTuple, PathOptions, TileEvent } from 'leaflet'
import type { JSX } from 'react'
import { useEffect, useMemo, useRef, useState } from 'react'
import { MapContainer, Marker, Polyline, TileLayer, ZoomControl, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './mission-map.css'

export type LatLng = { lat: number; lng: number }
export type MapPoint = LatLng & { label?: string; sublabel?: string; stale?: boolean }
export type MissionMapProps = { incident?: MapPoint | null; ambulance?: MapPoint | null; hospital?: MapPoint | null; route?: LatLng[] | null; alternativeRoute?: LatLng[] | null; dataMode?: string; height?: number; className?: string }

type MarkerKind = 'incident' | 'ambulance' | 'hospital'

const KINDS: Record<MarkerKind, { glyph: string; name: string }> = { incident: { glyph: '!', name: 'Incident' }, ambulance: { glyph: 'A', name: 'Ambulance' }, hospital: { glyph: 'H', name: 'Hospital' } }
const PRIMARY_ROUTE: PathOptions = { color: '#3b82f6', weight: 5, opacity: .95, lineCap: 'round', lineJoin: 'round' }
const ALTERNATIVE_ROUTE: PathOptions = { color: '#a8b7ca', weight: 3, opacity: .55, dashArray: '9 9', lineCap: 'butt' }
const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const TILE_ATTRIBUTION = '&copy; OpenStreetMap contributors'
const TILE_STALL_MS = 6000
// Inline transparent GIF: a failed tile must not fire a second asset request or leave a broken-image box.
const BLANK_TILE = 'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
const ESCAPES: Record<string, string> = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }

const escapeHtml = (value: string) => value.replace(/[&<>"']/g, (char) => ESCAPES[char] ?? char)
const isCoord = (value: number) => typeof value === 'number' && Number.isFinite(value)
const inRange = (point: LatLng) => isCoord(point.lat) && isCoord(point.lng) && Math.abs(point.lat) <= 90 && Math.abs(point.lng) <= 180
const usablePoint = (point?: MapPoint | null): MapPoint | null => (point && inRange(point) ? point : null)
const usableRoute = (route?: LatLng[] | null): LatLng[] => (Array.isArray(route) ? route.filter((vertex) => vertex && inRange(vertex)) : [])
const toTuple = (point: LatLng): LatLngTuple => [point.lat, point.lng]

function buildIcon(kind: MarkerKind, point: MapPoint): DivIcon {
  const chip = [point.label ? `<span class="mm-chip-label">${escapeHtml(point.label)}</span>` : '', point.sublabel ? `<span class="mm-chip-sub">${escapeHtml(point.sublabel)}</span>` : '', point.stale ? '<span class="mm-chip-stale">STALE</span>' : ''].join('')
  // divIcon instead of the default marker image: bundlers break Leaflet's _getIconUrl asset paths, and inline HTML also keeps the map working with no network.
  return divIcon({ className: `mm-marker mm-${kind}${point.stale ? ' mm-stale' : ''}`, iconSize: [30, 30], iconAnchor: [15, 15], html: `<span class="mm-pin" aria-hidden="true">${KINDS[kind].glyph}</span>${chip ? `<span class="mm-chip">${chip}</span>` : ''}` })
}

function MissionMarker({ kind, point }: { kind: MarkerKind; point: MapPoint }) {
  const { lat, lng, label, sublabel, stale } = point
  const icon = useMemo(() => buildIcon(kind, { lat, lng, label, sublabel, stale }), [kind, lat, lng, label, sublabel, stale])
  const title = `${KINDS[kind].name}${label ? ` ${label}` : ''}${sublabel ? `, ${sublabel}` : ''}${stale ? ', position is stale' : ''}`
  return <Marker position={{ lat, lng }} icon={icon} title={title} alt={title} />
}

function ViewportSync({ points, height }: { points: LatLngTuple[]; height: number }) {
  const map = useMap()
  const applied = useRef('')
  // No dependency array: the geometry arrives as a fresh array every render, so the fit is gated on the values changing rather than on identity.
  useEffect(() => {
    const signature = `${height}|${points.map(([lat, lng]) => `${lat.toFixed(5)},${lng.toFixed(5)}`).join(';')}`
    if (points.length === 0 || signature === applied.current) return
    applied.current = signature
    try {
      map.invalidateSize(false)
      const size = map.getSize()
      // jsdom and a not-yet-laid-out container report a zero-size viewport, where fitBounds cannot solve a zoom.
      if (points.length === 1 || size.x < 2 || size.y < 2) { map.setView(latLngBounds(points).getCenter(), points.length === 1 ? 14 : map.getZoom()); return }
      map.fitBounds(latLngBounds(points), { padding: [42, 42], maxZoom: 16 })
    } catch { /* a failed fit must never blank the map; the last good view stays */ }
  })
  return null
}

function Legend({ entries, hasRoute, hasAlternative }: { entries: { kind: MarkerKind; point: MapPoint | null }[]; hasRoute: boolean; hasAlternative: boolean }) {
  return <ul className="mission-map-legend">{entries.map(({ kind, point }) => <li className={point ? '' : 'mm-unknown'} key={kind}><span className={`mm-key mm-${kind}`} aria-hidden="true">{KINDS[kind].glyph}</span>{point ? (point.label ?? KINDS[kind].name.toUpperCase()) : `${KINDS[kind].name.toUpperCase()} — UNKNOWN`}</li>)}{hasRoute && <li><span className="mm-key mm-line-primary" aria-hidden="true" />ACTIVE ROUTE</li>}{hasAlternative && <li><span className="mm-key mm-line-alt" aria-hidden="true" />ALTERNATIVE</li>}</ul>
}

export function MissionMap({ incident, ambulance, hospital, route, alternativeRoute, dataMode, height = 360, className }: MissionMapProps): JSX.Element {
  const [tilesDown, setTilesDown] = useState(false)
  const batch = useRef({ ok: 0, failed: 0 })
  const stall = useRef<number | undefined>(undefined)
  const clearStall = () => { if (stall.current !== undefined) { window.clearTimeout(stall.current); stall.current = undefined } }
  useEffect(() => clearStall, [])
  const inc = usablePoint(incident), amb = usablePoint(ambulance), hos = usablePoint(hospital)
  const primary = usableRoute(route), alternative = usableRoute(alternativeRoute)
  const entries: { kind: MarkerKind; point: MapPoint | null }[] = [{ kind: 'incident', point: inc }, { kind: 'ambulance', point: amb }, { kind: 'hospital', point: hos }]
  const points: LatLngTuple[] = [...entries.map((entry) => entry.point).filter((point): point is MapPoint => point !== null).map(toTuple), ...primary.map(toTuple), ...alternative.map(toTuple)]
  const wrapperClass = ['mission-map', className ?? ''].filter(Boolean).join(' ')

  if (points.length === 0) return <div className={wrapperClass} style={{ height }} role="group" aria-label="Mission map"><div className="mission-map-empty"><strong>NO MAPPABLE POSITIONS</strong><span>No incident, unit, hospital or route coordinates were supplied. Nothing is plotted rather than guessed.</span>{dataMode ? <span className="mm-badge">{dataMode}</span> : null}</div></div>

  return <div className={wrapperClass} style={{ height }} role="group" aria-label="Mission map">
    <MapContainer center={points[0]} zoom={13} className="mission-map-canvas" scrollWheelZoom zoomControl={false}>
      <ZoomControl position="topright" />
      <TileLayer url={TILE_URL} attribution={TILE_ATTRIBUTION} errorTileUrl={BLANK_TILE} eventHandlers={{
        // A stalled network never fires tileerror or load, so the batch is also failed if nothing has arrived by the deadline.
        loading: () => { batch.current = { ok: 0, failed: 0 }; clearStall(); stall.current = window.setTimeout(() => { if (batch.current.ok === 0) setTilesDown(true) }, TILE_STALL_MS) },
        // errorTileUrl re-points a failed tile at the blank GIF, whose own load fires tileload too, so only a real tile counts as the basemap working.
        tileload: (event: TileEvent) => { if (event.tile.getAttribute('src') !== BLANK_TILE) batch.current.ok += 1 },
        tileerror: () => { batch.current.failed += 1 },
        load: () => { clearStall(); setTilesDown(batch.current.ok === 0) },
      }} />
      {alternative.length > 1 ? <Polyline positions={alternative} pathOptions={ALTERNATIVE_ROUTE} /> : null}
      {primary.length > 1 ? <Polyline positions={primary} pathOptions={PRIMARY_ROUTE} /> : null}
      {hos ? <MissionMarker kind="hospital" point={hos} /> : null}
      {amb ? <MissionMarker kind="ambulance" point={amb} /> : null}
      {inc ? <MissionMarker kind="incident" point={inc} /> : null}
      <ViewportSync points={points} height={height} />
    </MapContainer>
    <div className="mission-map-overlay">
      <div className="mission-map-topline">{dataMode ? <span className="mm-badge">{dataMode}</span> : null}{tilesDown ? <span className="mm-tile-warning" role="status">MAP TILES UNAVAILABLE — OFFLINE BASEMAP</span> : null}</div>
      <Legend entries={entries} hasRoute={primary.length > 1} hasAlternative={alternative.length > 1} />
    </div>
  </div>
}
