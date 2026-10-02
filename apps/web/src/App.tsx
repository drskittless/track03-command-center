import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'

type Role = 'Operations' | 'Volunteers' | 'Leadership'
type ChangeType = 'venue' | 'schedule' | 'deployment'
type EventRecord = { id: string; name: string; venue: string; date?: string; status: string }
type Item = { id: string; name: string; type: string; owner_role: Role; status: string; location: string; depends_on: string[] }
type Task = { id: string; name: string; owner_role: Role; status: string }
type Impact = { id: string; name: string; type: string; owner_role: Role; reason: string; dependency_path: string[] }
type Preview = { event_id: string; change_type: ChangeType; from_value: string; to_value: string; target_item_id?: string; affected: Impact[]; follow_up_tasks: Task[] }
type Board = { event: EventRecord; role: Role; items: Item[]; all_items: Item[]; tasks: Task[]; data_source: string; counts: { total: number; visible: number; blocked: number; at_risk: number; tasks: number }; role_counts: Record<Role, number> }

const roles: Role[] = ['Operations', 'Volunteers', 'Leadership']
const changeLabels: Record<ChangeType, string> = { venue: 'Venue change', schedule: 'Schedule change', deployment: 'Volunteer / resource reassignment' }
const api = 'http://localhost:8000'

function App() {
  const [role, setRole] = useState<Role>('Operations')
  const [board, setBoard] = useState<Board | null>(null)
  const [changeType, setChangeType] = useState<ChangeType>('venue')
  const [newValue, setNewValue] = useState('Open Air Theatre')
  const [targetId, setTargetId] = useState('')
  const [closeoutSummary, setCloseoutSummary] = useState('')
  const [closeoutLessons, setCloseoutLessons] = useState('')
  const [preview, setPreview] = useState<Preview | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const loadBoard = useCallback(async () => {
    const response = await fetch(`${api}/api/events/EVT-001/board?role=${role}`)
    const payload = await response.json()
    if (!response.ok) throw new Error(payload.detail ?? 'Could not load the event board')
    setBoard(payload as Board)
  }, [role])

  useEffect(() => { loadBoard().catch((reason: Error) => setError(reason.message)) }, [loadBoard])

  const grouped = useMemo(() => board?.role_counts ?? { Operations: 0, Volunteers: 0, Leadership: 0 }, [board])
  const deployableItems = useMemo(() => board?.all_items.filter((item) => ['volunteer', 'equipment'].includes(item.type.toLowerCase())) ?? [], [board])
  const selectedItem = deployableItems.find((item) => item.id === targetId) ?? deployableItems[0]

  function valueForType(type: ChangeType) {
    if (type === 'venue') return board?.event.venue ?? ''
    if (type === 'schedule') return board?.event.date ?? ''
    return deployableItems.find((item) => item.id === targetId)?.location ?? deployableItems[0]?.location ?? ''
  }

  function body() {
    if (changeType === 'venue') return { change_type: changeType, new_venue: newValue.trim() }
    if (changeType === 'schedule') return { change_type: changeType, new_date: newValue }
    return { change_type: changeType, target_item_id: targetId || selectedItem?.id, new_location: newValue.trim() }
  }

  async function request(path: string, payload?: object) {
    const response = await fetch(`${api}${path}`, {
      method: payload ? 'POST' : 'GET',
      headers: payload ? { 'Content-Type': 'application/json' } : undefined,
      body: payload ? JSON.stringify(payload) : undefined,
    })
    const result = await response.json()
    if (!response.ok) throw new Error(result.detail ?? 'Request failed')
    return result
  }

  async function makePreview() {
    setBusy(true); setError(''); setNotice('')
    try { setPreview(await request('/api/events/EVT-001/preview', body()) as Preview) }
    catch (reason) { setError((reason as Error).message) }
    finally { setBusy(false) }
  }

  async function applyChange() {
    setBusy(true); setError(''); setNotice('')
    try {
      await request('/api/events/EVT-001/apply', body())
      setPreview(null)
      await loadBoard()
      setNotice(board?.data_source === 'notion' ? 'Change, impact log, and follow-up tasks synced to Notion.' : 'Change applied to the demo fixture.')
    } catch (reason) { setError((reason as Error).message) }
    finally { setBusy(false) }
  }

  async function resetDemo() {
    setBusy(true); setError(''); setNotice('')
    try { await request('/api/demo/reset'); setPreview(null); await loadBoard(); setNotice('Demo data reset.') }
    catch (reason) { setError((reason as Error).message) }
    finally { setBusy(false) }
  }

  async function saveCloseout() {
    setBusy(true); setError(''); setNotice('')
    try {
      await request('/api/events/EVT-001/closeout', { summary: closeoutSummary.trim(), lessons: closeoutLessons.trim() })
      await loadBoard()
      setNotice(board?.data_source === 'notion' ? 'Event marked done and the closeout was saved to the Notion Impact Log.' : 'Event closeout saved to the demo fixture.')
    } catch (reason) { setError((reason as Error).message) }
    finally { setBusy(false) }
  }

  const currentValue = valueForType(changeType)
  const valueLabel = changeType === 'venue' ? 'NEW VENUE' : changeType === 'schedule' ? 'NEW EVENT DATE' : 'NEW DEPLOYMENT LOCATION'
  const inputType = changeType === 'schedule' ? 'date' : 'text'
  const changeReady = changeType === 'deployment' ? Boolean(selectedItem && newValue.trim().length >= 2) : newValue.trim().length >= 2

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top"><span className="brand-mark">T</span> TRACK03 <span className="brand-light">/ COMMAND CENTER</span></a>
        <div className="topbar-right"><span className="live-dot" /> EVENT LIVE <span className="divider">·</span><span>{board?.data_source === 'notion' ? 'NOTION SYNC' : 'DEMO FIXTURE'}</span></div>
      </header>

      <section className="hero" id="top">
        <div className="eyebrow">KBC TECH FEST 2026 <span>/{board?.event.id ?? 'EVT-001'}</span></div>
        <div className="hero-line"><div><h1>Event operations</h1><p>One change. Every team in sync.</p></div><div className="venue-card"><span className="label">CURRENT VENUE</span><strong>{board?.event.venue ?? 'Loading…'}</strong><span className="status-pill"><i /> {board?.event.status ?? '—'}</span><span className="label">EVENT DATE</span><strong>{board?.event.date ?? 'Not set'}</strong></div></div>
      </section>

      <section className="metrics" aria-label="Event status">
        <div className="metric"><span>OPERATION ITEMS</span><strong>{board?.counts.total ?? '—'}</strong><small>across all teams</small></div>
        <div className="metric"><span>IN THIS VIEW</span><strong>{board?.counts.visible ?? '—'}</strong><small>{role.toLowerCase()} assignments</small></div>
        <div className="metric"><span>BLOCKED</span><strong className={board?.counts.blocked ? 'warn' : ''}>{board?.counts.blocked ?? '—'}</strong><small>need attention</small></div>
        <div className="metric"><span>FOLLOW-UPS</span><strong>{board?.counts.tasks ?? '—'}</strong><small>created from changes</small></div>
      </section>

      <section className="workspace">
        <div className="section-head"><div><span className="eyebrow">LIVE WORKSPACE</span><h2>Team view</h2></div><div className="role-tabs" role="tablist" aria-label="Team role">{roles.map((item) => <button key={item} role="tab" aria-selected={role === item} className={role === item ? 'active' : ''} onClick={() => { setRole(item); setPreview(null) }}>{item}<b>{grouped[item]}</b></button>)}</div></div>
        <div className="table-wrap"><table><thead><tr><th>ITEM</th><th>TYPE</th><th>LOCATION</th><th>DEPENDS ON</th><th>STATUS</th></tr></thead><tbody>{board?.items.map((item) => <tr key={item.id}><td><span className="row-id">{item.id}</span><strong>{item.name}</strong></td><td><span className="type-tag">{item.type}</span></td><td>{item.location}</td><td>{item.depends_on.length ? item.depends_on.join(', ') : <span className="muted">—</span>}</td><td><span className={`task-status ${item.status.toLowerCase().replace(' ', '-')}`}>{item.status}</span></td></tr>)}</tbody></table>{board?.items.length === 0 && <div className="empty">No items assigned to this role.</div>}</div>
      </section>

      <section className="change-panel">
        <div className="change-copy"><span className="eyebrow">SCENARIO / OPERATIONAL CHANGE</span><h2>Preview a change</h2><p>Review downstream impact before updating the operational record.</p>
          <div className="scenario-tabs" role="tablist" aria-label="Change scenario">{(['venue', 'schedule', 'deployment'] as ChangeType[]).map((type) => <button key={type} className={changeType === type ? 'active' : ''} onClick={() => { setChangeType(type); setNewValue(type === 'venue' ? 'Open Air Theatre' : type === 'schedule' ? board?.event.date ?? '' : 'Seminar Hall B'); setPreview(null); setError('') }}>{changeLabels[type]}</button>)}</div>
          {changeType === 'deployment' && <label className="field-label" htmlFor="target-item">VOLUNTEER OR RESOURCE<select id="target-item" value={selectedItem?.id ?? ''} onChange={(event) => { setTargetId(event.target.value); setPreview(null); const item = deployableItems.find((candidate) => candidate.id === event.target.value); if (item) setNewValue(item.location) }}>{deployableItems.map((item) => <option key={item.id} value={item.id}>{item.name} · {item.type}</option>)}</select></label>}
          <div className="change-input"><label htmlFor="change-value">{valueLabel}</label><input id="change-value" type={inputType} value={newValue} onChange={(event) => { setNewValue(event.target.value); setPreview(null) }} /><button className="primary" disabled={busy || !changeReady} onClick={makePreview}>{busy ? 'WORKING…' : 'PREVIEW IMPACT ↗'}</button></div>
        </div>
        <div className="change-side"><div className="change-from"><span>FROM</span><strong>{selectedItem && changeType === 'deployment' ? `${selectedItem.name}: ${currentValue}` : currentValue || '—'}</strong></div><div className="arrow">→</div><div className="change-from"><span>TO</span><strong>{newValue || '—'}</strong></div><div className="impact-count"><b>{preview?.affected.length ?? '—'}</b><span>records<br />impacted</span></div></div>
      </section>

      {error && <div className="alert error" role="alert">{error}</div>}{notice && <div className="alert success" role="status">{notice}</div>}
      {preview && <section className="preview"><div className="section-head"><div><span className="eyebrow">{changeLabels[preview.change_type].toUpperCase()} · IMPACT PREVIEW</span><h2>{preview.affected.length} records need follow-up</h2><p>Each item is linked by location or a dependency path. Review before applying.</p></div><button className="primary apply" disabled={busy} onClick={applyChange}>CONFIRM & SYNC ↗</button></div><div className="impact-list">{preview.affected.map((item) => <article className="impact-item" key={item.id}><div className="impact-title"><span className="row-id">{item.id}</span><strong>{item.name}</strong><span className="type-tag">{item.owner_role}</span></div><p>{item.reason}</p><small>DEPENDENCY PATH · {item.dependency_path.join(' → ')}</small></article>)}</div><div className="preview-footer"><span>{preview.follow_up_tasks.length} follow-up tasks will be assigned by role.</span><button className="text-button" onClick={() => setPreview(null)}>Cancel</button></div></section>}

      {board?.tasks.length ? <section className="tasks"><div className="section-head"><div><span className="eyebrow">ACTION QUEUE</span><h2>Follow-up tasks</h2></div>{board.data_source === 'fixtures' && <button className="text-button" onClick={resetDemo} disabled={busy}>Reset demo</button>}</div><div className="task-grid">{board.tasks.map((task) => <article className="task-card" key={task.id}><span className="row-id">{task.id}</span><strong>{task.name}</strong><div><span>{task.owner_role}</span><span className="task-status">{task.status}</span></div></article>)}</div></section> : board?.data_source === 'fixtures' && <div className="demo-footer"><span>DEMO CONTROLS</span><button className="text-button" onClick={resetDemo} disabled={busy}>Reset scenario</button></div>}
      <section className="closeout"><div><span className="eyebrow">POST-EVENT KNOWLEDGE</span><h2>Capture the closeout</h2><p>Save the event summary and lessons learned to the operational log.</p></div><label>EVENT SUMMARY<textarea value={closeoutSummary} onChange={(event) => setCloseoutSummary(event.target.value)} placeholder="What happened?" /></label><label>LESSONS LEARNED<textarea value={closeoutLessons} onChange={(event) => setCloseoutLessons(event.target.value)} placeholder="What should the team reuse or improve?" /></label><button className="primary" disabled={busy || closeoutSummary.trim().length < 5 || closeoutLessons.trim().length < 5} onClick={saveCloseout}>SAVE CLOSEOUT TO {board?.data_source === 'notion' ? 'NOTION' : 'DEMO'} ↗</button></section>
      <footer><span>TRACK03 <b>EVENT COMMAND CENTER</b></span><span>Operational context powered by Notion</span></footer>
    </main>
  )
}

export default App
