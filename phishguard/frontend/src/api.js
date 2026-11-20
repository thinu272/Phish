import { useEffect, useState } from 'react'

const FILTER_KEYS = ['from', 'to', 'department', 'attack_type', 'severity', 'status', 'country', 'domain']

export function queryString(filters) {
  const p = new URLSearchParams()
  FILTER_KEYS.forEach((k) => { if (filters[k]) p.set(k, filters[k]) })
  const s = p.toString()
  return s ? '?' + s : ''
}

/** useApi('executive', filters) -> { data, loading, error }. Keeps the previous data while reloading. */
export function useApi(endpoint, filters) {
  const [state, setState] = useState({ data: null, loading: true, error: null })
  const qs = queryString(filters)
  useEffect(() => {
    const ctl = new AbortController()
    setState((s) => ({ ...s, loading: true, error: null }))
    fetch(`/api/${endpoint}${qs}`, { signal: ctl.signal })
      .then((r) => { if (!r.ok) throw new Error(`${r.status} ${r.statusText}`); return r.json() })
      .then((data) => setState({ data, loading: false, error: null }))
      .catch((e) => { if (e.name !== 'AbortError') setState((s) => ({ ...s, loading: false, error: e.message })) })
    return () => ctl.abort()
  }, [endpoint, qs])
  return state
}
